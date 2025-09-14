"""
Feature Access Controller module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🚀 **Feature Access Controller - Enterprise ML Feature Security**

**Author:** Fahed Mlaiel (mlaiel@live.de) - DBA + Sécurité  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.  
**Version:** 1.0.0  
**Created:** January 2025

**⚠️ WARNING:** This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly prohibited.

---

## 🎯 **ROLE: DBA + SÉCURITÉ - FEATURE DATA GOVERNANCE MASTERY**

Enterprise-grade feature access control with RBAC, privacy-preserving access,
audit logging, and creator-specific data protection policies.
"""

import asyncio
import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class AccessLevel(Enum):
    """Feature access levels"""
    NONE = "none"           # No access
    READ = "read"           # Read-only access
    WRITE = "write"         # Read and write access
    ADMIN = "admin"         # Full administrative access
    OWNER = "owner"         # Owner-level access

class FeatureCategory(Enum):
    """Feature categories for access control"""
    PERSONAL_DATA = "personal_data"
    BEHAVIORAL_DATA = "behavioral_data"
    CONTENT_FEATURES = "content_features"
    PERFORMANCE_METRICS = "performance_metrics"
    TECHNICAL_METADATA = "technical_metadata"
    ENGAGEMENT_DATA = "engagement_data"
    FINANCIAL_DATA = "financial_data"
    SENSITIVE_ANALYTICS = "sensitive_analytics"

class CreatorType(Enum):
    """Creator types for specialized access"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"

class UserRole(Enum):
    """User roles in the system"""
    CREATOR = "creator"
    ADMIN = "admin"
    ANALYST = "analyst"
    ML_ENGINEER = "ml_engineer"
    DATA_SCIENTIST = "data_scientist"
    AUDITOR = "auditor"
    SYSTEM = "system"

@dataclass
class AccessPolicy:
    """Feature access policy definition"""
    policy_id: str
    feature_pattern: str  # Regex pattern for feature names
    feature_categories: List[FeatureCategory]
    user_roles: List[UserRole]
    creator_types: List[CreatorType]
    access_level: AccessLevel
    conditions: Dict[str, Any]  # Additional conditions
    valid_from: datetime
    valid_until: Optional[datetime] = None
    created_by: str = "system"

@dataclass
class AccessRequest:
    """Feature access request"""
    request_id: str
    user_id: str
    user_role: UserRole
    creator_id: Optional[str]
    creator_type: Optional[CreatorType]
    feature_names: List[str]
    requested_access: AccessLevel
    purpose: str
    timestamp: datetime
    context: Dict[str, Any]

@dataclass
class AccessGrant:
    """Granted feature access"""
    grant_id: str
    request_id: str
    user_id: str
    feature_names: List[str]
    granted_access: AccessLevel
    granted_at: datetime
    expires_at: Optional[datetime]
    conditions: Dict[str, Any]
    audit_trail: List[Dict[str, Any]]

@dataclass
class PrivacyFilter:
    """Privacy filter for sensitive data"""
    filter_id: str
    feature_pattern: str
    filter_type: str  # "mask", "hash", "encrypt", "remove"
    applies_to: List[UserRole]
    exceptions: List[str]  # User IDs with exceptions
    created_at: datetime

class FeatureAccessController:
    """
    🚀 **Enterprise Feature Access Controller**
    
    **DBA + Sécurité Role:** Comprehensive feature data governance
    - Role-based access control (RBAC) for ML features
    - Privacy-preserving feature access with data masking
    - Creator-specific data protection and ownership
    - Comprehensive audit logging and compliance tracking
    - Dynamic access policies with time-based restrictions
    - Feature-level encryption and anonymization
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Access control storage
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.access_grants: Dict[str, AccessGrant] = {}
        self.privacy_filters: Dict[str, PrivacyFilter] = {}
        
        # User and creator mappings
        self.user_roles: Dict[str, UserRole] = {}
        self.creator_mappings: Dict[str, CreatorType] = {}
        self.creator_ownership: Dict[str, Set[str]] = {}  # creator_id -> feature_names
        
        # Encryption for sensitive features
        self.encryption_key = config.get('encryption_key', Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Audit logging
        self.audit_log: List[Dict[str, Any]] = []
        
        # Access cache for performance
        self.access_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=config.get('cache_ttl_minutes', 15))
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self) -> None:
        """Initialize default access policies"""
        
        # Creator access to their own data
        self.access_policies["creator_own_data"] = AccessPolicy(
            policy_id="creator_own_data",
            feature_pattern=".*",
            feature_categories=list(FeatureCategory),
            user_roles=[UserRole.CREATOR],
            creator_types=list(CreatorType),
            access_level=AccessLevel.READ,
            conditions={"owns_data": True},
            valid_from=datetime.utcnow(),
            created_by="system"
        )
        
        # Admin full access
        self.access_policies["admin_full_access"] = AccessPolicy(
            policy_id="admin_full_access",
            feature_pattern=".*",
            feature_categories=list(FeatureCategory),
            user_roles=[UserRole.ADMIN],
            creator_types=list(CreatorType),
            access_level=AccessLevel.ADMIN,
            conditions={},
            valid_from=datetime.utcnow(),
            created_by="system"
        )
        
        # ML Engineer access to technical features
        self.access_policies["ml_engineer_technical"] = AccessPolicy(
            policy_id="ml_engineer_technical",
            feature_pattern=".*_(features|embeddings|scores|metrics).*",
            feature_categories=[
                FeatureCategory.CONTENT_FEATURES,
                FeatureCategory.PERFORMANCE_METRICS,
                FeatureCategory.TECHNICAL_METADATA
            ],
            user_roles=[UserRole.ML_ENGINEER, UserRole.DATA_SCIENTIST],
            creator_types=list(CreatorType),
            access_level=AccessLevel.READ,
            conditions={},
            valid_from=datetime.utcnow(),
            created_by="system"
        )
        
        # Analyst access to aggregated data
        self.access_policies["analyst_aggregated"] = AccessPolicy(
            policy_id="analyst_aggregated",
            feature_pattern=".*_(avg|sum|count|total).*",
            feature_categories=[
                FeatureCategory.PERFORMANCE_METRICS,
                FeatureCategory.ENGAGEMENT_DATA
            ],
            user_roles=[UserRole.ANALYST],
            creator_types=list(CreatorType),
            access_level=AccessLevel.READ,
            conditions={"aggregated_only": True},
            valid_from=datetime.utcnow(),
            created_by="system"
        )
        
        # Initialize privacy filters
        self._initialize_privacy_filters()
    
    def _initialize_privacy_filters(self) -> None:
        """Initialize privacy filters for sensitive data"""
        
        # Mask personal identifiers
        self.privacy_filters["mask_personal_ids"] = PrivacyFilter(
            filter_id="mask_personal_ids",
            feature_pattern=".*(email|phone|ssn|id).*",
            filter_type="mask",
            applies_to=[UserRole.ANALYST, UserRole.ML_ENGINEER],
            exceptions=["admin_user"],
            created_at=datetime.utcnow()
        )
        
        # Hash behavioral data
        self.privacy_filters["hash_behavioral"] = PrivacyFilter(
            filter_id="hash_behavioral",
            feature_pattern=".*behavioral.*",
            filter_type="hash",
            applies_to=[UserRole.DATA_SCIENTIST, UserRole.ANALYST],
            exceptions=[],
            created_at=datetime.utcnow()
        )
        
        # Encrypt financial data
        self.privacy_filters["encrypt_financial"] = PrivacyFilter(
            filter_id="encrypt_financial",
            feature_pattern=".*financial.*",
            filter_type="encrypt",
            applies_to=[UserRole.ANALYST, UserRole.ML_ENGINEER],
            exceptions=["financial_admin"],
            created_at=datetime.utcnow()
        )
    
    async def request_feature_access(
        self,
        user_id: str,
        feature_names: List[str],
        access_level: AccessLevel,
        purpose: str,
        creator_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Request access to features
        
        **DBA + Sécurité Expertise:**
        - Policy evaluation and access determination
        - Creator ownership validation
        - Purpose-based access control
        - Audit trail generation
        
        Returns: (granted, reason, grant_id)
        """
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Get user role and creator type
        user_role = self.user_roles.get(user_id, UserRole.CREATOR)
        creator_type = self.creator_mappings.get(creator_id) if creator_id else None
        
        # Create access request
        request = AccessRequest(
            request_id=request_id,
            user_id=user_id,
            user_role=user_role,
            creator_id=creator_id,
            creator_type=creator_type,
            feature_names=feature_names,
            requested_access=access_level,
            purpose=purpose,
            timestamp=timestamp,
            context=context or {}
        )
        
        # Evaluate access policies
        granted, reason = await self._evaluate_access_policies(request)
        
        grant_id = None
        if granted:
            # Create access grant
            grant_id = str(uuid.uuid4())
            grant = AccessGrant(
                grant_id=grant_id,
                request_id=request_id,
                user_id=user_id,
                feature_names=feature_names,
                granted_access=access_level,
                granted_at=timestamp,
                expires_at=timestamp + timedelta(hours=24),  # Default 24h expiry
                conditions={},
                audit_trail=[{
                    'action': 'granted',
                    'timestamp': timestamp.isoformat(),
                    'reason': reason
                }]
            )
            
            self.access_grants[grant_id] = grant
            
            # Update access cache
            cache_key = f"{user_id}:{','.join(feature_names)}"
            self.access_cache[cache_key] = {
                'granted': True,
                'grant_id': grant_id,
                'expires_at': grant.expires_at,
                'cached_at': timestamp
            }
        
        # Log audit event
        await self._log_access_request(request, granted, reason, grant_id)
        
        return granted, reason, grant_id
    
    async def access_features(
        self,
        user_id: str,
        feature_data: Dict[str, Any],
        grant_id: Optional[str] = None,
        purpose: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Access features with privacy filtering applied
        
        **DBA + Sécurité Excellence:** Privacy-preserving feature access
        """
        # Validate access grant if provided
        if grant_id:
            if not await self._validate_access_grant(grant_id, user_id, list(feature_data.keys())):
                raise PermissionError("Invalid or expired access grant")
        else:
            # Check cached access or request new access
            feature_names = list(feature_data.keys())
            granted, reason, new_grant_id = await self.request_feature_access(
                user_id=user_id,
                feature_names=feature_names,
                access_level=AccessLevel.READ,
                purpose=purpose or "feature_access"
            )
            
            if not granted:
                raise PermissionError(f"Access denied: {reason}")
            
            grant_id = new_grant_id
        
        # Apply privacy filters
        filtered_data = await self._apply_privacy_filters(user_id, feature_data)
        
        # Log access event
        await self._log_feature_access(user_id, list(feature_data.keys()), grant_id)
        
        return filtered_data
    
    async def _evaluate_access_policies(self, request: AccessRequest) -> Tuple[bool, str]:
        """Evaluate access policies for a request"""
        import re
        
        user_role = request.user_role
        creator_type = request.creator_type
        feature_names = request.feature_names
        
        # Check each feature against policies
        denied_features = []
        granted_features = []
        
        for feature_name in feature_names:
            feature_granted = False
            
            for policy_id, policy in self.access_policies.items():
                # Check if policy applies
                if not self._policy_applies(policy, request, feature_name):
                    continue
                
                # Check access level
                if self._access_level_sufficient(policy.access_level, request.requested_access):
                    # Check additional conditions
                    if await self._check_policy_conditions(policy, request, feature_name):
                        feature_granted = True
                        break
            
            if feature_granted:
                granted_features.append(feature_name)
            else:
                denied_features.append(feature_name)
        
        # Determine overall result
        if not denied_features:
            return True, "Access granted to all requested features"
        elif not granted_features:
            return False, f"Access denied to all features: {', '.join(denied_features)}"
        else:
            return False, f"Partial access denied to: {', '.join(denied_features)}"
    
    def _policy_applies(self, policy: AccessPolicy, request: AccessRequest, feature_name: str) -> bool:
        """Check if a policy applies to the request"""
        import re
        
        # Check feature pattern
        if not re.match(policy.feature_pattern, feature_name):
            return False
        
        # Check user role
        if request.user_role not in policy.user_roles:
            return False
        
        # Check creator type if specified
        if (policy.creator_types and 
            request.creator_type and 
            request.creator_type not in policy.creator_types):
            return False
        
        # Check validity period
        now = datetime.utcnow()
        if now < policy.valid_from:
            return False
        
        if policy.valid_until and now > policy.valid_until:
            return False
        
        return True
    
    def _access_level_sufficient(self, granted_level: AccessLevel, requested_level: AccessLevel) -> bool:
        """Check if granted access level is sufficient for requested level"""
        level_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4
        }
        
        return level_hierarchy[granted_level] >= level_hierarchy[requested_level]
    
    async def _check_policy_conditions(
        self,
        policy: AccessPolicy,
        request: AccessRequest,
        feature_name: str
    ) -> bool:
        """Check additional policy conditions"""
        conditions = policy.conditions
        
        # Check data ownership condition
        if conditions.get("owns_data", False):
            if not request.creator_id:
                return False
            
            # Check if user owns the data
            if not await self._user_owns_feature_data(request.user_id, request.creator_id, feature_name):
                return False
        
        # Check aggregation requirement
        if conditions.get("aggregated_only", False):
            if not self._is_aggregated_feature(feature_name):
                return False
        
        # Check time-based conditions
        if "time_restrictions" in conditions:
            time_restrictions = conditions["time_restrictions"]
            current_hour = datetime.utcnow().hour
            
            if "allowed_hours" in time_restrictions:
                if current_hour not in time_restrictions["allowed_hours"]:
                    return False
        
        return True
    
    async def _user_owns_feature_data(self, user_id: str, creator_id: str, feature_name: str) -> bool:
        """Check if user owns the feature data"""
        # For creators accessing their own data
        if user_id == creator_id:
            return True
        
        # Check explicit ownership mappings
        if creator_id in self.creator_ownership:
            return feature_name in self.creator_ownership[creator_id]
        
        return False
    
    def _is_aggregated_feature(self, feature_name: str) -> bool:
        """Check if feature is aggregated (non-individual)"""
        aggregation_patterns = ["_avg", "_sum", "_count", "_total", "_mean", "_median", "_std"]
        return any(pattern in feature_name for pattern in aggregation_patterns)
    
    async def _apply_privacy_filters(self, user_id: str, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply privacy filters to feature data"""
        user_role = self.user_roles.get(user_id, UserRole.CREATOR)
        filtered_data = {}
        
        for feature_name, feature_value in feature_data.items():
            filtered_value = feature_value
            
            # Apply applicable privacy filters
            for filter_id, privacy_filter in self.privacy_filters.items():
                if self._filter_applies(privacy_filter, user_id, user_role, feature_name):
                    filtered_value = await self._apply_filter(privacy_filter, feature_name, filtered_value)
            
            filtered_data[feature_name] = filtered_value
        
        return filtered_data
    
    def _filter_applies(
        self,
        privacy_filter: PrivacyFilter,
        user_id: str,
        user_role: UserRole,
        feature_name: str
    ) -> bool:
        """Check if privacy filter applies"""
        import re
        
        # Check feature pattern
        if not re.match(privacy_filter.feature_pattern, feature_name):
            return False
        
        # Check user role
        if user_role not in privacy_filter.applies_to:
            return False
        
        # Check exceptions
        if user_id in privacy_filter.exceptions:
            return False
        
        return True
    
    async def _apply_filter(
        self,
        privacy_filter: PrivacyFilter,
        feature_name: str,
        feature_value: Any
    ) -> Any:
        """Apply specific privacy filter"""
        filter_type = privacy_filter.filter_type
        
        if filter_type == "mask":
            return self._mask_value(feature_value)
        elif filter_type == "hash":
            return self._hash_value(feature_value)
        elif filter_type == "encrypt":
            return self._encrypt_value(feature_value)
        elif filter_type == "remove":
            return None
        else:
            return feature_value
    
    def _mask_value(self, value: Any) -> str:
        """Mask sensitive value"""
        str_value = str(value)
        if len(str_value) <= 4:
            return "*" * len(str_value)
        else:
            return str_value[:2] + "*" * (len(str_value) - 4) + str_value[-2:]
    
    def _hash_value(self, value: Any) -> str:
        """Hash sensitive value"""
        str_value = str(value)
        return hashlib.sha256(str_value.encode()).hexdigest()[:16]  # Truncated hash
    
    def _encrypt_value(self, value: Any) -> str:
        """Encrypt sensitive value"""
        str_value = str(value)
        encrypted = self.cipher_suite.encrypt(str_value.encode())
        return base64.b64encode(encrypted).decode()
    
    async def _validate_access_grant(
        self,
        grant_id: str,
        user_id: str,
        feature_names: List[str]
    ) -> bool:
        """Validate access grant"""
        if grant_id not in self.access_grants:
            return False
        
        grant = self.access_grants[grant_id]
        
        # Check user
        if grant.user_id != user_id:
            return False
        
        # Check expiry
        if grant.expires_at and datetime.utcnow() > grant.expires_at:
            return False
        
        # Check feature access
        for feature_name in feature_names:
            if feature_name not in grant.feature_names:
                return False
        
        return True
    
    async def add_access_policy(
        self,
        policy_id: str,
        feature_pattern: str,
        feature_categories: List[FeatureCategory],
        user_roles: List[UserRole],
        access_level: AccessLevel,
        creator_types: Optional[List[CreatorType]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        valid_until: Optional[datetime] = None,
        created_by: str = "admin"
    ) -> bool:
        """Add new access policy"""
        try:
            policy = AccessPolicy(
                policy_id=policy_id,
                feature_pattern=feature_pattern,
                feature_categories=feature_categories,
                user_roles=user_roles,
                creator_types=creator_types or [],
                access_level=access_level,
                conditions=conditions or {},
                valid_from=datetime.utcnow(),
                valid_until=valid_until,
                created_by=created_by
            )
            
            self.access_policies[policy_id] = policy
            
            # Log policy creation
            await self._log_policy_change("created", policy_id, created_by)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding access policy {policy_id}: {e}")
            return False
    
    async def revoke_access_grant(self, grant_id: str, revoked_by: str) -> bool:
        """Revoke access grant"""
        if grant_id not in self.access_grants:
            return False
        
        grant = self.access_grants[grant_id]
        grant.audit_trail.append({
            'action': 'revoked',
            'timestamp': datetime.utcnow().isoformat(),
            'revoked_by': revoked_by
        })
        
        # Remove from active grants
        del self.access_grants[grant_id]
        
        # Clear cache entries
        self._clear_user_cache(grant.user_id)
        
        # Log revocation
        await self._log_access_revocation(grant_id, revoked_by)
        
        return True
    
    def set_user_role(self, user_id -> None: str, role -> None: UserRole) -> None:
        """Set user role"""
        self.user_roles[user_id] = role
        self._clear_user_cache(user_id)
    
    def set_creator_type(self, creator_id -> None: str, creator_type -> None: CreatorType) -> None:
        """Set creator type"""
        self.creator_mappings[creator_id] = creator_type
    
    def add_creator_ownership(self, creator_id -> None: str, feature_names -> None: List[str]) -> None:
        """Add feature ownership for creator"""
        if creator_id not in self.creator_ownership:
            self.creator_ownership[creator_id] = set()
        
        self.creator_ownership[creator_id].update(feature_names)
    
    def _clear_user_cache(self, user_id -> None: str) -> None:
        """Clear access cache for user"""
        keys_to_remove = [key for key in self.access_cache.keys() if key.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self.access_cache[key]
    
    async def _log_access_request(
        self,
        request -> None: AccessRequest,
        granted -> None: bool,
        reason -> None: str,
        grant_id -> None: Optional[str]
    ) -> None:
        """Log access request for audit"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'access_request',
            'request_id': request.request_id,
            'user_id': request.user_id,
            'user_role': request.user_role.value,
            'creator_id': request.creator_id,
            'feature_names': request.feature_names,
            'requested_access': request.requested_access.value,
            'purpose': request.purpose,
            'granted': granted,
            'reason': reason,
            'grant_id': grant_id,
            'context': request.context
        }
        
        self.audit_log.append(audit_entry)
        self._trim_audit_log()
        
        self.logger.info(f"Access request logged: {request.user_id} -> {len(request.feature_names)} features, granted: {granted}")
    
    async def _log_feature_access(self, user_id -> None: str, feature_names -> None: List[str], grant_id -> None: str) -> None:
        """Log feature access for audit"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'feature_access',
            'user_id': user_id,
            'feature_names': feature_names,
            'grant_id': grant_id,
            'feature_count': len(feature_names)
        }
        
        self.audit_log.append(audit_entry)
        self._trim_audit_log()
    
    async def _log_policy_change(self, action -> None: str, policy_id -> None: str, changed_by -> None: str) -> None:
        """Log policy changes for audit"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'policy_change',
            'action': action,
            'policy_id': policy_id,
            'changed_by': changed_by
        }
        
        self.audit_log.append(audit_entry)
        self._trim_audit_log()
    
    async def _log_access_revocation(self, grant_id -> None: str, revoked_by -> None: str) -> None:
        """Log access revocation for audit"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'access_revocation',
            'grant_id': grant_id,
            'revoked_by': revoked_by
        }
        
        self.audit_log.append(audit_entry)
        self._trim_audit_log()
    
    def _trim_audit_log(self) -> None:
        """Keep audit log size manageable"""
        max_entries = self.config.get('max_audit_entries', 10000)
        if len(self.audit_log) > max_entries:
            self.audit_log = self.audit_log[-max_entries:]
    
    async def get_access_audit_report(
        self,
        user_id: Optional[str] = None,
        feature_pattern: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Generate access audit report"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        relevant_entries = []
        for entry in self.audit_log:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time < cutoff_date:
                continue
            
            # Filter by user if specified
            if user_id and entry.get('user_id') != user_id:
                continue
            
            # Filter by feature pattern if specified
            if feature_pattern and entry.get('feature_names'):
                import re
                if not any(re.match(feature_pattern, fn) for fn in entry['feature_names']):
                    continue
            
            relevant_entries.append(entry)
        
        # Generate statistics
        total_requests = len([e for e in relevant_entries if e['event_type'] == 'access_request'])
        granted_requests = len([e for e in relevant_entries if e['event_type'] == 'access_request' and e.get('granted', False)])
        denied_requests = total_requests - granted_requests
        
        unique_users = len(set(e.get('user_id') for e in relevant_entries if e.get('user_id')))
        
        return {
            'report_period_days': days,
            'total_audit_entries': len(relevant_entries),
            'access_requests': {
                'total': total_requests,
                'granted': granted_requests,
                'denied': denied_requests,
                'grant_rate': granted_requests / total_requests if total_requests > 0 else 0
            },
            'unique_users': unique_users,
            'entries': relevant_entries
        }

# Usage example
async def main() -> None:
    """Example usage of FeatureAccessController"""
    config = {
        'cache_ttl_minutes': 15,
        'max_audit_entries': 1000
    }
    
    controller = FeatureAccessController(config)
    
    # Set up users and creators
    controller.set_user_role("user_123", UserRole.CREATOR)
    controller.set_user_role("analyst_456", UserRole.ANALYST)
    controller.set_user_role("ml_eng_789", UserRole.ML_ENGINEER)
    
    controller.set_creator_type("creator_123", CreatorType.MUSICIAN)
    controller.add_creator_ownership("creator_123", ["audio_tempo", "audio_genre", "engagement_score"])
    
    # Request access to features
    granted, reason, grant_id = await controller.request_feature_access(
        user_id="user_123",
        feature_names=["audio_tempo", "audio_genre", "engagement_score"],
        access_level=AccessLevel.READ,
        purpose="content_analysis",
        creator_id="creator_123"
    )
    
    print(f"Access granted: {granted}, Reason: {reason}, Grant ID: {grant_id}")
    
    if granted:
        # Access features with privacy filtering
        feature_data = {
            "audio_tempo": 120,
            "audio_genre": "rock",
            "engagement_score": 0.85,
            "user_email": "user@example.com"
        }
        
        filtered_data = await controller.access_features(
            user_id="user_123",
            feature_data=feature_data,
            grant_id=grant_id
        )
        
        print(f"Filtered data: {filtered_data}")
    
    # Generate audit report
    audit_report = await controller.get_access_audit_report(days=1)
    print(f"Audit report: {audit_report}")

if __name__ == "__main__":
    asyncio.run(main())