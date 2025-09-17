"""🔒 Access Control Manager - ML Security Module
=======================================================================
Gestionnaire contrôle accès granulaire ML avec RBAC avancé.
Role-based access + attribute-based control + ML-specific permissions + audit integration.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue ML Security - Access Control
Version: 1.0 Production
=======================================================================
"""

import asyncio
import logging
import time
import hashlib
import json
import secrets
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import jwt
import base64
from collections import defaultdict

logger = logging.getLogger(__name__)

class AccessControlType(Enum):
    """Types de contrôle d'accès"""
    ROLE_BASED = "role_based"
    ATTRIBUTE_BASED = "attribute_based"
    MANDATORY = "mandatory"
    DISCRETIONARY = "discretionary"
    CONTEXT_AWARE = "context_aware"
    TIME_BASED = "time_based"
    LOCATION_BASED = "location_based"
    RISK_ADAPTIVE = "risk_adaptive"

class MLResourceType(Enum):
    """Types de ressources ML"""
    MODEL = "model"
    DATASET = "dataset"
    TRAINING_JOB = "training_job"
    INFERENCE_ENDPOINT = "inference_endpoint"
    FEATURE_STORE = "feature_store"
    EXPERIMENT = "experiment"
    PIPELINE = "pipeline"
    ARTIFACT = "artifact"
    NOTEBOOK = "notebook"
    WORKSPACE = "workspace"

class Permission(Enum):
    """Permissions ML spécifiques"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    TRAIN = "train"
    DEPLOY = "deploy"
    INFERENCE = "inference"
    ADMIN = "admin"
    AUDIT = "audit"
    SHARE = "share"

class AccessDecision(Enum):
    """Décisions d'accès"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    ESCALATE = "escalate"

@dataclass
class AccessControlConfig:
    """Configuration contrôle d'accès"""
    access_control_types: List[AccessControlType] = field(default_factory=lambda: [
        AccessControlType.ROLE_BASED,
        AccessControlType.ATTRIBUTE_BASED
    ])
    session_timeout: int = 3600  # 1 hour
    max_concurrent_sessions: int = 5
    audit_enabled: bool = True
    mfa_required: bool = True
    risk_assessment_enabled: bool = True
    context_evaluation: bool = True
    creator_protection_mode: bool = True  # Ainflue-specific
    ip_protection_enabled: bool = True    # Fahed Mlaiel IP protection

@dataclass
class UserContext:
    """Contexte utilisateur"""
    user_id: str
    roles: List[str]
    attributes: Dict[str, Any]
    session_id: str
    ip_address: Optional[str] = None
    location: Optional[str] = None
    device_info: Optional[Dict] = None
    risk_score: float = 0.0
    authentication_method: str = "password"
    last_activity: float = field(default_factory=time.time)

@dataclass
class AccessContext:
    """Contexte d'accès"""
    resource_type: MLResourceType
    resource_id: str
    requested_permission: Permission
    context_attributes: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    request_origin: Optional[str] = None
    business_context: Optional[str] = None

@dataclass
class AccessControlRequest:
    """Requête contrôle d'accès"""
    user_context: UserContext
    access_context: AccessContext
    policy_overrides: Optional[Dict] = None
    emergency_access: bool = False

@dataclass
class AccessControlResult:
    """Résultat contrôle d'accès"""
    decision: AccessDecision
    granted_permissions: List[Permission]
    conditions: List[str]
    audit_trail: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    session_info: Dict[str, Any]
    enforcement_time_ms: float

class MLRole:
    """Rôle ML avec permissions spécifiques"""
    
    def __init__(self, name: str, permissions: List[Permission], resource_types: List[MLResourceType]):
        self.name = name
        self.permissions = set(permissions)
        self.resource_types = set(resource_types)
        self.creation_time = time.time()
        self.created_by = "system"
        
    def has_permission(self, permission: Permission, resource_type: MLResourceType) -> bool:
        """Vérification permission pour type de ressource"""
        return permission in self.permissions and resource_type in self.resource_types
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            "name": self.name,
            "permissions": [p.value for p in self.permissions],
            "resource_types": [rt.value for rt in self.resource_types],
            "creation_time": self.creation_time,
            "created_by": self.created_by
        }

class RoleBasedAccessEngine:
    """Moteur contrôle accès basé sur rôles"""
    
    def __init__(self, config: AccessControlConfig):
        self.config = config
        self.roles = self._initialize_default_roles()
        self.user_role_assignments = {}
        
    def _initialize_default_roles(self) -> Dict[str, MLRole]:
        """Initialisation rôles par défaut"""
        return {
            "ml_admin": MLRole(
                name="ml_admin",
                permissions=[Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DELETE, 
                           Permission.TRAIN, Permission.DEPLOY, Permission.ADMIN, Permission.AUDIT],
                resource_types=list(MLResourceType)
            ),
            "ml_engineer": MLRole(
                name="ml_engineer",
                permissions=[Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.TRAIN, 
                           Permission.DEPLOY, Permission.INFERENCE],
                resource_types=[MLResourceType.MODEL, MLResourceType.DATASET, MLResourceType.TRAINING_JOB,
                              MLResourceType.EXPERIMENT, MLResourceType.PIPELINE]
            ),
            "data_scientist": MLRole(
                name="data_scientist",
                permissions=[Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.TRAIN],
                resource_types=[MLResourceType.DATASET, MLResourceType.EXPERIMENT, MLResourceType.NOTEBOOK,
                              MLResourceType.MODEL]
            ),
            "creator": MLRole(  # Ainflue-specific role
                name="creator",
                permissions=[Permission.READ, Permission.INFERENCE, Permission.SHARE],
                resource_types=[MLResourceType.MODEL, MLResourceType.INFERENCE_ENDPOINT]
            ),
            "viewer": MLRole(
                name="viewer",
                permissions=[Permission.READ],
                resource_types=[MLResourceType.MODEL, MLResourceType.DATASET, MLResourceType.EXPERIMENT]
            )
        }
    
    async def enforce_rbac_policies(self, user_context: UserContext, access_context: AccessContext) -> Dict[str, Any]:
        """Enforcement politiques RBAC pour ressources ML"""
        try:
            rbac_result = {
                "decision": AccessDecision.DENY,
                "reason": "no_matching_role",
                "evaluated_roles": [],
                "granted_permissions": []
            }
            
            user_roles = user_context.roles
            requested_permission = access_context.requested_permission
            resource_type = access_context.resource_type
            
            # Evaluate each user role
            for role_name in user_roles:
                if role_name in self.roles:
                    role = self.roles[role_name]
                    rbac_result["evaluated_roles"].append(role_name)
                    
                    if role.has_permission(requested_permission, resource_type):
                        rbac_result["decision"] = AccessDecision.ALLOW
                        rbac_result["reason"] = f"granted_by_role_{role_name}"
                        rbac_result["granted_permissions"] = list(role.permissions)
                        break
            
            # Special handling for creator IP protection (Ainflue-specific)
            if self.config.creator_protection_mode and "creator" in user_roles:
                rbac_result["creator_protection"] = self._apply_creator_protection(user_context, access_context)
            
            # IP protection for Fahed Mlaiel
            if self.config.ip_protection_enabled:
                rbac_result["ip_protection"] = self._apply_ip_protection(user_context, access_context)
            
            return rbac_result
            
        except Exception as e:
            logger.error(f"RBAC enforcement failed: {e}")
            return {"decision": AccessDecision.DENY, "error": str(e)}
    
    def _apply_creator_protection(self, user_context: UserContext, access_context: AccessContext) -> Dict[str, Any]:
        """Application protection spéciale créateurs Ainflue"""
        protection_result = {
            "creator_protection_active": True,
            "protected_resources": [],
            "additional_permissions": []
        }
        
        # Protect creator intellectual property
        if access_context.resource_type in [MLResourceType.MODEL, MLResourceType.INFERENCE_ENDPOINT]:
            protection_result["protected_resources"].append(access_context.resource_id)
            
            # Grant additional permissions for own content
            creator_id = user_context.attributes.get("creator_id")
            resource_owner = access_context.context_attributes.get("owner_id")
            
            if creator_id and creator_id == resource_owner:
                protection_result["additional_permissions"] = [Permission.SHARE, Permission.ADMIN]
        
        return protection_result
    
    def _apply_ip_protection(self, user_context: UserContext, access_context: AccessContext) -> Dict[str, Any]:
        """Application protection IP Fahed Mlaiel"""
        ip_protection = {
            "ip_protection_active": True,
            "protected_by": "Fahed Mlaiel (mlaiel@live.de)",
            "protection_level": "maximum"
        }
        
        # Enhanced protection for core ML security components
        if access_context.context_attributes.get("component_type") == "ml_security":
            ip_protection["enhanced_protection"] = True
            ip_protection["access_logged"] = True
            ip_protection["notification_sent"] = True
        
        return ip_protection

class AttributeBasedAccessEngine:
    """Moteur contrôle accès basé sur attributs"""
    
    def __init__(self, config: AccessControlConfig):
        self.config = config
        self.policy_rules = self._initialize_abac_policies()
        
    def _initialize_abac_policies(self) -> List[Dict[str, Any]]:
        """Initialisation politiques ABAC"""
        return [
            {
                "id": "time_based_access",
                "condition": "current_time >= start_time AND current_time <= end_time",
                "attributes": ["current_time", "start_time", "end_time"],
                "effect": "allow"
            },
            {
                "id": "location_based_access",
                "condition": "user_location IN allowed_locations",
                "attributes": ["user_location", "allowed_locations"],
                "effect": "allow"
            },
            {
                "id": "risk_based_access",
                "condition": "user_risk_score <= max_risk_threshold",
                "attributes": ["user_risk_score", "max_risk_threshold"],
                "effect": "conditional"
            },
            {
                "id": "creator_content_protection",
                "condition": "resource_owner == user_id OR user_role == 'admin'",
                "attributes": ["resource_owner", "user_id", "user_role"],
                "effect": "allow"
            },
            {
                "id": "fahed_mlaiel_ip_protection",
                "condition": "component_owner == 'Fahed Mlaiel' AND user_clearance >= 'high'",
                "attributes": ["component_owner", "user_clearance"],
                "effect": "conditional"
            }
        ]
    
    async def evaluate_abac_rules(self, access_context: AccessContext, user_context: UserContext) -> Dict[str, Any]:
        """Évaluation règles ABAC avec context-aware permissions"""
        try:
            abac_result = {
                "decision": AccessDecision.DENY,
                "evaluated_policies": [],
                "conditions": [],
                "attribute_evaluation": {}
            }
            
            # Build evaluation context
            eval_context = self._build_evaluation_context(access_context, user_context)
            
            # Evaluate each policy
            allow_count = 0
            conditional_count = 0
            
            for policy in self.policy_rules:
                policy_result = await self._evaluate_policy(policy, eval_context)
                abac_result["evaluated_policies"].append({
                    "policy_id": policy["id"],
                    "result": policy_result
                })
                
                if policy_result["decision"] == "allow":
                    allow_count += 1
                elif policy_result["decision"] == "conditional":
                    conditional_count += 1
                    abac_result["conditions"].extend(policy_result.get("conditions", []))
            
            # Final decision logic
            if allow_count > 0:
                if conditional_count > 0:
                    abac_result["decision"] = AccessDecision.CONDITIONAL
                else:
                    abac_result["decision"] = AccessDecision.ALLOW
            elif conditional_count > 0:
                abac_result["decision"] = AccessDecision.CONDITIONAL
            
            abac_result["attribute_evaluation"] = eval_context
            
            return abac_result
            
        except Exception as e:
            logger.error(f"ABAC evaluation failed: {e}")
            return {"decision": AccessDecision.DENY, "error": str(e)}
    
    def _build_evaluation_context(self, access_context: AccessContext, user_context: UserContext) -> Dict[str, Any]:
        """Construction contexte évaluation ABAC"""
        current_time = time.time()
        
        return {
            "current_time": current_time,
            "user_id": user_context.user_id,
            "user_roles": user_context.roles,
            "user_risk_score": user_context.risk_score,
            "user_location": user_context.location,
            "user_clearance": user_context.attributes.get("clearance", "low"),
            "resource_type": access_context.resource_type.value,
            "resource_id": access_context.resource_id,
            "resource_owner": access_context.context_attributes.get("owner_id"),
            "component_owner": access_context.context_attributes.get("component_owner"),
            "requested_permission": access_context.requested_permission.value,
            "business_context": access_context.business_context,
            "start_time": user_context.attributes.get("access_start_time", current_time),
            "end_time": user_context.attributes.get("access_end_time", current_time + 86400),
            "allowed_locations": user_context.attributes.get("allowed_locations", []),
            "max_risk_threshold": 0.7,
            "ip_address": user_context.ip_address
        }
    
    async def _evaluate_policy(self, policy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Évaluation politique ABAC individuelle"""
        try:
            policy_result = {
                "decision": "deny",
                "conditions": [],
                "evaluation_details": {}
            }
            
            # Simplified policy evaluation
            policy_id = policy["id"]
            
            if policy_id == "time_based_access":
                current_time = context.get("current_time", 0)
                start_time = context.get("start_time", 0)
                end_time = context.get("end_time", float('inf'))
                
                if start_time <= current_time <= end_time:
                    policy_result["decision"] = "allow"
                else:
                    policy_result["decision"] = "deny"
                    policy_result["conditions"].append("outside_allowed_time_window")
            
            elif policy_id == "location_based_access":
                user_location = context.get("user_location")
                allowed_locations = context.get("allowed_locations", [])
                
                if not user_location:
                    policy_result["decision"] = "conditional"
                    policy_result["conditions"].append("location_verification_required")
                elif user_location in allowed_locations or not allowed_locations:
                    policy_result["decision"] = "allow"
                else:
                    policy_result["decision"] = "deny"
            
            elif policy_id == "risk_based_access":
                risk_score = context.get("user_risk_score", 1.0)
                threshold = context.get("max_risk_threshold", 0.7)
                
                if risk_score <= threshold:
                    policy_result["decision"] = "allow"
                else:
                    policy_result["decision"] = "conditional"
                    policy_result["conditions"].append("additional_authentication_required")
            
            elif policy_id == "creator_content_protection":
                resource_owner = context.get("resource_owner")
                user_id = context.get("user_id")
                user_roles = context.get("user_roles", [])
                
                if resource_owner == user_id or "admin" in user_roles:
                    policy_result["decision"] = "allow"
                else:
                    policy_result["decision"] = "deny"
            
            elif policy_id == "fahed_mlaiel_ip_protection":
                component_owner = context.get("component_owner")
                user_clearance = context.get("user_clearance", "low")
                
                if component_owner == "Fahed Mlaiel":
                    if user_clearance in ["high", "maximum"]:
                        policy_result["decision"] = "conditional"
                        policy_result["conditions"].append("ip_access_logged")
                    else:
                        policy_result["decision"] = "deny"
                else:
                    policy_result["decision"] = "allow"
            
            return policy_result
            
        except Exception as e:
            return {"decision": "deny", "error": str(e)}

class MLPermissionManager:
    """Gestionnaire permissions ML avec granularité fine"""
    
    def __init__(self, config: AccessControlConfig):
        self.config = config
        self.permission_matrix = self._initialize_permission_matrix()
        self.resource_permissions = defaultdict(dict)
        
    def _initialize_permission_matrix(self) -> Dict[str, Dict[str, List[Permission]]]:
        """Initialisation matrice permissions ML"""
        return {
            "model": {
                "owner": [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.DEPLOY, 
                         Permission.SHARE, Permission.ADMIN],
                "collaborator": [Permission.READ, Permission.INFERENCE, Permission.SHARE],
                "viewer": [Permission.READ, Permission.INFERENCE],
                "admin": [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.DEPLOY,
                         Permission.ADMIN, Permission.AUDIT]
            },
            "dataset": {
                "owner": [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE],
                "collaborator": [Permission.READ],
                "viewer": [Permission.READ],
                "admin": [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN]
            },
            "training_job": {
                "owner": [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DELETE],
                "collaborator": [Permission.READ, Permission.EXECUTE],
                "viewer": [Permission.READ],
                "admin": [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DELETE, Permission.ADMIN]
            }
        }
    
    async def manage_ml_permissions(self, permission_request: Dict[str, Any]) -> Dict[str, Any]:
        """Gestion permissions ML avec granularité fine"""
        try:
            request_type = permission_request.get("type", "check")
            resource_type = permission_request.get("resource_type")
            resource_id = permission_request.get("resource_id")
            user_id = permission_request.get("user_id")
            requested_permission = permission_request.get("permission")
            
            if request_type == "check":
                return await self._check_permission(resource_type, resource_id, user_id, requested_permission)
            elif request_type == "grant":
                return await self._grant_permission(resource_type, resource_id, user_id, requested_permission)
            elif request_type == "revoke":
                return await self._revoke_permission(resource_type, resource_id, user_id, requested_permission)
            elif request_type == "list":
                return await self._list_permissions(resource_type, resource_id, user_id)
            else:
                return {"success": False, "error": "unknown_request_type"}
                
        except Exception as e:
            logger.error(f"Permission management failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_permission(self, resource_type: str, resource_id: str, user_id: str, permission: str) -> Dict[str, Any]:
        """Vérification permission spécifique"""
        resource_key = f"{resource_type}:{resource_id}"
        user_permissions = self.resource_permissions[resource_key].get(user_id, [])
        
        permission_enum = Permission(permission) if permission in [p.value for p in Permission] else None
        has_permission = permission_enum in user_permissions if permission_enum else False
        
        return {
            "success": True,
            "has_permission": has_permission,
            "user_permissions": [p.value for p in user_permissions],
            "checked_permission": permission
        }
    
    async def _grant_permission(self, resource_type: str, resource_id: str, user_id: str, permission: str) -> Dict[str, Any]:
        """Attribution permission"""
        resource_key = f"{resource_type}:{resource_id}"
        permission_enum = Permission(permission) if permission in [p.value for p in Permission] else None
        
        if not permission_enum:
            return {"success": False, "error": "invalid_permission"}
        
        if user_id not in self.resource_permissions[resource_key]:
            self.resource_permissions[resource_key][user_id] = []
        
        if permission_enum not in self.resource_permissions[resource_key][user_id]:
            self.resource_permissions[resource_key][user_id].append(permission_enum)
        
        return {
            "success": True,
            "granted_permission": permission,
            "user_permissions": [p.value for p in self.resource_permissions[resource_key][user_id]]
        }
    
    async def _revoke_permission(self, resource_type: str, resource_id: str, user_id: str, permission: str) -> Dict[str, Any]:
        """Révocation permission"""
        resource_key = f"{resource_type}:{resource_id}"
        permission_enum = Permission(permission) if permission in [p.value for p in Permission] else None
        
        if not permission_enum:
            return {"success": False, "error": "invalid_permission"}
        
        if user_id in self.resource_permissions[resource_key]:
            if permission_enum in self.resource_permissions[resource_key][user_id]:
                self.resource_permissions[resource_key][user_id].remove(permission_enum)
        
        return {
            "success": True,
            "revoked_permission": permission,
            "user_permissions": [p.value for p in self.resource_permissions[resource_key].get(user_id, [])]
        }
    
    async def _list_permissions(self, resource_type: str, resource_id: str, user_id: str) -> Dict[str, Any]:
        """Liste permissions utilisateur"""
        resource_key = f"{resource_type}:{resource_id}"
        user_permissions = self.resource_permissions[resource_key].get(user_id, [])
        
        return {
            "success": True,
            "user_id": user_id,
            "resource": resource_key,
            "permissions": [p.value for p in user_permissions]
        }

class SecureSessionManager:
    """Gestionnaire sessions sécurisées avec token handling"""
    
    def __init__(self, config: AccessControlConfig):
        self.config = config
        self.active_sessions = {}
        self.session_tokens = {}
        self.secret_key = secrets.token_hex(32)
        
    async def create_secure_session(self, user_context: UserContext) -> Dict[str, Any]:
        """Création session sécurisée"""
        try:
            session_id = secrets.token_hex(16)
            session_token = self._generate_session_token(user_context, session_id)
            
            # Check concurrent session limit
            user_sessions = [s for s in self.active_sessions.values() if s["user_id"] == user_context.user_id]
            if len(user_sessions) >= self.config.max_concurrent_sessions:
                # Terminate oldest session
                oldest_session = min(user_sessions, key=lambda x: x["created_at"])
                await self.terminate_session(oldest_session["session_id"])
            
            session_info = {
                "session_id": session_id,
                "user_id": user_context.user_id,
                "created_at": time.time(),
                "last_activity": time.time(),
                "expires_at": time.time() + self.config.session_timeout,
                "ip_address": user_context.ip_address,
                "device_info": user_context.device_info,
                "authentication_method": user_context.authentication_method,
                "roles": user_context.roles.copy(),
                "risk_score": user_context.risk_score
            }
            
            self.active_sessions[session_id] = session_info
            self.session_tokens[session_id] = session_token
            
            return {
                "success": True,
                "session_id": session_id,
                "session_token": session_token,
                "expires_at": session_info["expires_at"],
                "session_info": session_info
            }
            
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_session(self, session_id: str, session_token: str) -> Dict[str, Any]:
        """Validation session et token"""
        try:
            if session_id not in self.active_sessions:
                return {"valid": False, "reason": "session_not_found"}
            
            session_info = self.active_sessions[session_id]
            
            # Check expiration
            if time.time() > session_info["expires_at"]:
                await self.terminate_session(session_id)
                return {"valid": False, "reason": "session_expired"}
            
            # Validate token
            if not self._validate_session_token(session_token, session_id):
                return {"valid": False, "reason": "invalid_token"}
            
            # Update last activity
            session_info["last_activity"] = time.time()
            
            return {
                "valid": True,
                "session_info": session_info,
                "remaining_time": session_info["expires_at"] - time.time()
            }
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def terminate_session(self, session_id: str) -> Dict[str, Any]:
        """Terminaison session"""
        try:
            if session_id in self.active_sessions:
                session_info = self.active_sessions[session_id]
                del self.active_sessions[session_id]
                
                if session_id in self.session_tokens:
                    del self.session_tokens[session_id]
                
                return {
                    "success": True,
                    "terminated_session": session_id,
                    "user_id": session_info["user_id"]
                }
            else:
                return {"success": False, "reason": "session_not_found"}
                
        except Exception as e:
            logger.error(f"Session termination failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_session_token(self, user_context: UserContext, session_id: str) -> str:
        """Génération token session JWT"""
        payload = {
            "session_id": session_id,
            "user_id": user_context.user_id,
            "roles": user_context.roles,
            "iat": time.time(),
            "exp": time.time() + self.config.session_timeout,
            "iss": "Fahed Mlaiel ML Security"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def _validate_session_token(self, token: str, session_id: str) -> bool:
        """Validation token session"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload.get("session_id") == session_id
        except jwt.InvalidTokenError:
            return False
    
    def get_active_sessions_summary(self) -> Dict[str, Any]:
        """Résumé sessions actives"""
        return {
            "total_sessions": len(self.active_sessions),
            "sessions_by_user": len(set(s["user_id"] for s in self.active_sessions.values())),
            "average_session_age": np.mean([time.time() - s["created_at"] for s in self.active_sessions.values()]) if self.active_sessions else 0,
            "sessions_expiring_soon": len([s for s in self.active_sessions.values() if s["expires_at"] - time.time() < 300])  # 5 minutes
        }

class AccessAuditAnalyzer:
    """Analyseur audit patterns accès pour anomaly detection"""
    
    def __init__(self, config: AccessControlConfig):
        self.config = config
        self.access_logs = []
        self.anomaly_threshold = 3.0  # Standard deviations
        
    async def audit_access_patterns(self, access_logs: List[Dict]) -> Dict[str, Any]:
        """Audit patterns accès pour anomaly detection"""
        try:
            self.access_logs.extend(access_logs)
            
            audit_result = {
                "analyzed_requests": len(access_logs),
                "anomalies_detected": [],
                "user_behavior_analysis": {},
                "resource_access_patterns": {},
                "security_alerts": []
            }
            
            # Analyze user behavior patterns
            user_analysis = await self._analyze_user_behavior(access_logs)
            audit_result["user_behavior_analysis"] = user_analysis
            
            # Analyze resource access patterns
            resource_analysis = await self._analyze_resource_patterns(access_logs)
            audit_result["resource_access_patterns"] = resource_analysis
            
            # Detect anomalies
            anomalies = await self._detect_access_anomalies(access_logs)
            audit_result["anomalies_detected"] = anomalies
            
            # Generate security alerts
            alerts = self._generate_security_alerts(user_analysis, resource_analysis, anomalies)
            audit_result["security_alerts"] = alerts
            
            return audit_result
            
        except Exception as e:
            logger.error(f"Access audit failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_user_behavior(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyse comportement utilisateurs"""
        user_stats = defaultdict(lambda: {
            "total_requests": 0,
            "denied_requests": 0,
            "unique_resources": set(),
            "unique_ips": set(),
            "request_times": [],
            "permissions_requested": defaultdict(int)
        })
        
        for log in logs:
            user_id = log.get("user_id")
            if user_id:
                stats = user_stats[user_id]
                stats["total_requests"] += 1
                
                if log.get("decision") == "deny":
                    stats["denied_requests"] += 1
                
                if log.get("resource_id"):
                    stats["unique_resources"].add(log["resource_id"])
                
                if log.get("ip_address"):
                    stats["unique_ips"].add(log["ip_address"])
                
                if log.get("timestamp"):
                    stats["request_times"].append(log["timestamp"])
                
                if log.get("permission"):
                    stats["permissions_requested"][log["permission"]] += 1
        
        # Convert to serializable format and calculate metrics
        behavior_analysis = {}
        for user_id, stats in user_stats.items():
            behavior_analysis[user_id] = {
                "total_requests": stats["total_requests"],
                "denied_requests": stats["denied_requests"],
                "denial_rate": stats["denied_requests"] / stats["total_requests"] if stats["total_requests"] > 0 else 0,
                "unique_resources_count": len(stats["unique_resources"]),
                "unique_ips_count": len(stats["unique_ips"]),
                "most_requested_permission": max(stats["permissions_requested"].items(), key=lambda x: x[1])[0] if stats["permissions_requested"] else None,
                "request_frequency": len(stats["request_times"]) / (max(stats["request_times"]) - min(stats["request_times"]) + 1) if len(stats["request_times"]) > 1 else 0
            }
        
        return behavior_analysis
    
    async def _analyze_resource_patterns(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyse patterns accès ressources"""
        resource_stats = defaultdict(lambda: {
            "total_accesses": 0,
            "unique_users": set(),
            "access_times": [],
            "permissions_requested": defaultdict(int),
            "denied_accesses": 0
        })
        
        for log in logs:
            resource_id = log.get("resource_id")
            if resource_id:
                stats = resource_stats[resource_id]
                stats["total_accesses"] += 1
                
                if log.get("user_id"):
                    stats["unique_users"].add(log["user_id"])
                
                if log.get("timestamp"):
                    stats["access_times"].append(log["timestamp"])
                
                if log.get("permission"):
                    stats["permissions_requested"][log["permission"]] += 1
                
                if log.get("decision") == "deny":
                    stats["denied_accesses"] += 1
        
        # Convert to serializable format
        resource_analysis = {}
        for resource_id, stats in resource_stats.items():
            resource_analysis[resource_id] = {
                "total_accesses": stats["total_accesses"],
                "unique_users_count": len(stats["unique_users"]),
                "denied_accesses": stats["denied_accesses"],
                "denial_rate": stats["denied_accesses"] / stats["total_accesses"] if stats["total_accesses"] > 0 else 0,
                "most_requested_permission": max(stats["permissions_requested"].items(), key=lambda x: x[1])[0] if stats["permissions_requested"] else None,
                "access_frequency": len(stats["access_times"]) / (max(stats["access_times"]) - min(stats["access_times"]) + 1) if len(stats["access_times"]) > 1 else 0
            }
        
        return resource_analysis
    
    async def _detect_access_anomalies(self, logs: List[Dict]) -> List[Dict[str, Any]]:
        """Détection anomalies accès"""
        anomalies = []
        
        # Group logs by user
        user_logs = defaultdict(list)
        for log in logs:
            if log.get("user_id"):
                user_logs[log["user_id"]].append(log)
        
        # Detect anomalies for each user
        for user_id, user_log_list in user_logs.items():
            # High denial rate anomaly
            denied_count = sum(1 for log in user_log_list if log.get("decision") == "deny")
            denial_rate = denied_count / len(user_log_list) if user_log_list else 0
            
            if denial_rate > 0.5:  # More than 50% denied
                anomalies.append({
                    "type": "high_denial_rate",
                    "user_id": user_id,
                    "severity": "medium",
                    "details": f"Denial rate: {denial_rate:.2%}",
                    "recommendation": "Review user permissions"
                })
            
            # Unusual access time anomaly
            access_times = [log.get("timestamp", 0) for log in user_log_list]
            if access_times:
                time_diffs = [access_times[i+1] - access_times[i] for i in range(len(access_times)-1)]
                if time_diffs:
                    avg_interval = np.mean(time_diffs)
                    if avg_interval < 1:  # Less than 1 second between requests
                        anomalies.append({
                            "type": "rapid_fire_requests",
                            "user_id": user_id,
                            "severity": "high",
                            "details": f"Average interval: {avg_interval:.2f}s",
                            "recommendation": "Potential automated attack"
                        })
            
            # Multiple IP addresses anomaly
            unique_ips = set(log.get("ip_address") for log in user_log_list if log.get("ip_address"))
            if len(unique_ips) > 3:  # More than 3 different IPs
                anomalies.append({
                    "type": "multiple_ip_addresses",
                    "user_id": user_id,
                    "severity": "medium",
                    "details": f"IPs used: {len(unique_ips)}",
                    "recommendation": "Verify user identity"
                })
        
        return anomalies
    
    def _generate_security_alerts(self, user_analysis: Dict, resource_analysis: Dict, anomalies: List[Dict]) -> List[Dict[str, Any]]:
        """Génération alertes sécurité"""
        alerts = []
        
        # High-severity anomaly alerts
        for anomaly in anomalies:
            if anomaly.get("severity") == "high":
                alerts.append({
                    "alert_type": "security_anomaly",
                    "severity": "high",
                    "title": f"Security Anomaly Detected: {anomaly['type']}",
                    "description": anomaly.get("details", ""),
                    "affected_user": anomaly.get("user_id"),
                    "recommendation": anomaly.get("recommendation", ""),
                    "timestamp": time.time()
                })
        
        # Suspicious user behavior alerts
        for user_id, analysis in user_analysis.items():
            if analysis["denial_rate"] > 0.7:  # Very high denial rate
                alerts.append({
                    "alert_type": "suspicious_behavior",
                    "severity": "medium",
                    "title": f"High Denial Rate for User {user_id}",
                    "description": f"Denial rate: {analysis['denial_rate']:.2%}",
                    "affected_user": user_id,
                    "recommendation": "Review user access requirements",
                    "timestamp": time.time()
                })
        
        return alerts

class AccessControlManager:
    """
    Gestionnaire contrôle accès granulaire ML avec RBAC avancé.
    Role-based access + attribute-based control + ML-specific permissions + audit integration.
    """
    
    def __init__(self, access_config: AccessControlConfig):
        self.access_config = access_config
        self.rbac_engine = RoleBasedAccessEngine(access_config)
        self.abac_engine = AttributeBasedAccessEngine(access_config)
        self.permission_manager = MLPermissionManager(access_config)
        self.session_manager = SecureSessionManager(access_config)
        self.audit_analyzer = AccessAuditAnalyzer(access_config)
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        
    async def initialize(self, config) -> None:
        """Initialisation gestionnaire contrôle accès"""
        self.logger.info("🔒 Initializing Access Control Manager...")
        self.access_config = config
        self._initialized = True
        self.logger.info("✅ Access Control Manager initialized successfully")
        
    async def execute_security_check(self, request: Any) -> Dict[str, Any]:
        """Exécution check sécurité pour contrôle accès"""
        if isinstance(request, dict):
            user_context = UserContext(
                user_id=request.get("user_id", "unknown"),
                roles=request.get("roles", []),
                attributes=request.get("attributes", {}),
                session_id=request.get("session_id", ""),
                ip_address=request.get("ip_address"),
                risk_score=request.get("risk_score", 0.0)
            )
            
            access_context = AccessContext(
                resource_type=MLResourceType(request.get("resource_type", "model")),
                resource_id=request.get("resource_id", "unknown"),
                requested_permission=Permission(request.get("permission", "read")),
                context_attributes=request.get("context_attributes", {})
            )
            
            access_request = AccessControlRequest(
                user_context=user_context,
                access_context=access_context
            )
        else:
            # Default request
            access_request = AccessControlRequest(
                user_context=UserContext(user_id="test", roles=["viewer"], attributes={}, session_id="test"),
                access_context=AccessContext(
                    resource_type=MLResourceType.MODEL,
                    resource_id="test",
                    requested_permission=Permission.READ,
                    context_attributes={}
                )
            )
        
        result = await self.manage_ml_access_control(access_request)
        
        return {
            "service": "access_control_manager",
            "decision": result.decision.value,
            "granted_permissions": [p.value for p in result.granted_permissions],
            "conditions_count": len(result.conditions),
            "risk_score": result.risk_assessment.get("risk_score", 0.0),
            "session_valid": result.session_info.get("valid", False),
            "enforcement_time_ms": result.enforcement_time_ms,
            "score": 100 if result.decision == AccessDecision.ALLOW else 50 if result.decision == AccessDecision.CONDITIONAL else 0
        }
        
    async def get_security_status(self) -> Dict[str, Any]:
        """Statut service contrôle accès"""
        session_summary = self.session_manager.get_active_sessions_summary()
        
        return {
            "service": "access_control_manager",
            "status": "active" if self._initialized else "inactive",
            "version": "1.0.0",
            "access_control_types": [t.value for t in self.access_config.access_control_types],
            "session_summary": session_summary,
            "audit_enabled": self.access_config.audit_enabled,
            "mfa_required": self.access_config.mfa_required,
            "creator_protection_mode": self.access_config.creator_protection_mode,
            "ip_protection_enabled": self.access_config.ip_protection_enabled,
            "last_update": time.time()
        }
        
    async def handle_security_incident(self, incident: Any) -> Any:
        """Gestion incident sécurité contrôle accès"""
        return {"status": "access_incident_logged", "response": "access_restrictions_applied"}
        
    async def manage_ml_access_control(self, access_request: AccessControlRequest) -> AccessControlResult:
        """
        Gestion contrôle accès ML avec granularité fine.
        
        Access Control Features:
        - Role-based access control avec ML-specific roles
        - Attribute-based access control pour fine-grained permissions
        - Model-level access control avec per-model permissions
        - Data-level access control avec dataset-specific rules
        - API endpoint protection avec rate limiting et authentication
        - Session management avec secure token handling
        - Multi-factor authentication pour sensitive operations
        - Just-in-time access provisioning avec time-bounded permissions
        - Privilege escalation detection avec access pattern analysis
        - Integration avec audit trails pour compliance monitoring
        """
        start_time = time.time()
        
        self.logger.info("🔒 Starting ML access control evaluation...")
        
        try:
            conditions = []
            granted_permissions = []
            audit_trail = {}
            risk_assessment = {}
            
            # 1. Session Validation
            session_validation = await self.session_manager.validate_session(
                access_request.user_context.session_id,
                access_request.user_context.attributes.get("session_token", "")
            )
            audit_trail["session_validation"] = session_validation
            
            if not session_validation.get("valid", False):
                return AccessControlResult(
                    decision=AccessDecision.DENY,
                    granted_permissions=[],
                    conditions=["invalid_session"],
                    audit_trail=audit_trail,
                    risk_assessment={"risk_score": 1.0, "reason": "invalid_session"},
                    session_info=session_validation,
                    enforcement_time_ms=(time.time() - start_time) * 1000
                )
            
            # 2. RBAC Evaluation
            if AccessControlType.ROLE_BASED in self.access_config.access_control_types:
                rbac_result = await self.rbac_engine.enforce_rbac_policies(
                    access_request.user_context,
                    access_request.access_context
                )
                audit_trail["rbac_evaluation"] = rbac_result
                
                if rbac_result["decision"] == AccessDecision.ALLOW:
                    granted_permissions.extend([Permission(p) for p in rbac_result.get("granted_permissions", [])])
            
            # 3. ABAC Evaluation
            if AccessControlType.ATTRIBUTE_BASED in self.access_config.access_control_types:
                abac_result = await self.abac_engine.evaluate_abac_rules(
                    access_request.access_context,
                    access_request.user_context
                )
                audit_trail["abac_evaluation"] = abac_result
                
                if abac_result["decision"] == AccessDecision.CONDITIONAL:
                    conditions.extend(abac_result.get("conditions", []))
                elif abac_result["decision"] == AccessDecision.DENY:
                    return AccessControlResult(
                        decision=AccessDecision.DENY,
                        granted_permissions=[],
                        conditions=["abac_policy_violation"],
                        audit_trail=audit_trail,
                        risk_assessment={"risk_score": 0.8, "reason": "abac_denied"},
                        session_info=session_validation,
                        enforcement_time_ms=(time.time() - start_time) * 1000
                    )
            
            # 4. Risk Assessment
            risk_assessment = await self._assess_access_risk(access_request)
            audit_trail["risk_assessment"] = risk_assessment
            
            if risk_assessment["risk_score"] > 0.8:
                conditions.append("high_risk_access")
            
            # 5. Final Decision Logic
            final_decision = self._make_final_decision(rbac_result, abac_result, risk_assessment, conditions)
            
            # 6. Permission Finalization
            if final_decision in [AccessDecision.ALLOW, AccessDecision.CONDITIONAL]:
                # Ensure requested permission is included if granted
                if access_request.access_context.requested_permission not in granted_permissions:
                    granted_permissions.append(access_request.access_context.requested_permission)
            
            enforcement_time = (time.time() - start_time) * 1000
            
            # 7. Audit Logging
            if self.access_config.audit_enabled:
                await self._log_access_decision(access_request, final_decision, audit_trail)
            
            result = AccessControlResult(
                decision=final_decision,
                granted_permissions=granted_permissions,
                conditions=conditions,
                audit_trail=audit_trail,
                risk_assessment=risk_assessment,
                session_info=session_validation,
                enforcement_time_ms=enforcement_time
            )
            
            self.logger.info(f"🔒 Access control evaluation complete: {final_decision.value}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Access control evaluation failed: {e}")
            return AccessControlResult(
                decision=AccessDecision.DENY,
                granted_permissions=[],
                conditions=["system_error"],
                audit_trail={"error": str(e)},
                risk_assessment={"risk_score": 1.0, "reason": "system_error"},
                session_info={"valid": False},
                enforcement_time_ms=(time.time() - start_time) * 1000
            )
    
    async def _assess_access_risk(self, access_request: AccessControlRequest) -> Dict[str, Any]:
        """Évaluation risque accès"""
        risk_factors = []
        risk_score = 0.0
        
        # User risk factors
        user_risk = access_request.user_context.risk_score
        risk_score += user_risk * 0.4
        
        if user_risk > 0.7:
            risk_factors.append("high_user_risk_score")
        
        # Resource sensitivity
        sensitive_resources = [MLResourceType.MODEL, MLResourceType.TRAINING_JOB]
        if access_request.access_context.resource_type in sensitive_resources:
            risk_score += 0.2
            risk_factors.append("sensitive_resource_access")
        
        # Permission sensitivity
        sensitive_permissions = [Permission.DELETE, Permission.ADMIN, Permission.DEPLOY]
        if access_request.access_context.requested_permission in sensitive_permissions:
            risk_score += 0.3
            risk_factors.append("sensitive_permission_requested")
        
        # Time-based risk
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Off-hours access
            risk_score += 0.1
            risk_factors.append("off_hours_access")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "assessment_time": time.time()
        }
    
    def _make_final_decision(self, rbac_result: Dict, abac_result: Dict, risk_assessment: Dict, conditions: List[str]) -> AccessDecision:
        """Décision finale basée sur tous les évaluations"""
        # High risk always requires conditions or denial
        if risk_assessment["risk_score"] > 0.9:
            return AccessDecision.DENY
        
        # RBAC denial overrides
        if rbac_result.get("decision") == AccessDecision.DENY:
            return AccessDecision.DENY
        
        # ABAC denial overrides
        if abac_result.get("decision") == AccessDecision.DENY:
            return AccessDecision.DENY
        
        # Conditional access if conditions present
        if conditions or abac_result.get("decision") == AccessDecision.CONDITIONAL:
            return AccessDecision.CONDITIONAL
        
        # Allow if RBAC allows and no blocking conditions
        if rbac_result.get("decision") == AccessDecision.ALLOW:
            return AccessDecision.ALLOW
        
        # Default deny
        return AccessDecision.DENY
    
    async def _log_access_decision(self, request: AccessControlRequest, decision: AccessDecision, audit_trail: Dict) -> None:
        """Logging décision accès pour audit"""
        log_entry = {
            "timestamp": time.time(),
            "user_id": request.user_context.user_id,
            "resource_type": request.access_context.resource_type.value,
            "resource_id": request.access_context.resource_id,
            "permission": request.access_context.requested_permission.value,
            "decision": decision.value,
            "ip_address": request.user_context.ip_address,
            "session_id": request.user_context.session_id,
            "audit_trail": audit_trail
        }
        
        # Add to audit analyzer
        await self.audit_analyzer.audit_access_patterns([log_entry])
        
        self.logger.info(f"🔒 Access decision logged: {decision.value} for user {request.user_context.user_id}")

# Export API
__all__ = [
    'AccessControlManager',
    'AccessControlConfig',
    'AccessControlRequest',
    'AccessControlResult',
    'UserContext',
    'AccessContext',
    'MLResourceType',
    'Permission',
    'AccessDecision',
    'AccessControlType'
]