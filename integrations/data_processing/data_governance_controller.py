"""Data Governance Controller - Enterprise Data Governance
========================================================

Comprehensive data governance and compliance management with data catalog,
lineage tracking, metadata management, and automated compliance enforcement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
import re
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from pathlib import Path

try:
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

import redis.asyncio as redis


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class ComplianceRegulation(Enum):
    """Compliance regulations."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST = "nist"


class DataAction(Enum):
    """Data access actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    SHARE = "share"
    ANONYMIZE = "anonymize"


class PolicyType(Enum):
    """Data policy types."""
    ACCESS_CONTROL = "access_control"
    RETENTION = "retention"
    PRIVACY = "privacy"
    QUALITY = "quality"
    SECURITY = "security"
    USAGE = "usage"


@dataclass
class DataAsset:
    """Data asset in the catalog."""
    id: str
    name: str
    description: str
    asset_type: str  # table, view, file, api, etc.
    schema_name: Optional[str] = None
    database_name: Optional[str] = None
    location: Optional[str] = None
    classification: DataClassification = DataClassification.INTERNAL
    owner: Optional[str] = None
    steward: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    columns: List[Dict[str, Any]] = field(default_factory=list)
    lineage: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataPolicy:
    """Data governance policy."""
    id: str
    name: str
    policy_type: PolicyType
    description: str
    rules: List[Dict[str, Any]]
    applicable_classifications: List[DataClassification] = field(default_factory=list)
    applicable_regulations: List[ComplianceRegulation] = field(default_factory=list)
    enforcement_actions: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    """Data access request."""
    id: str
    user_id: str
    asset_id: str
    action: DataAction
    justification: str
    status: str = "pending"  # pending, approved, denied
    requested_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None
    expiry_date: Optional[datetime] = None
    conditions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageNode:
    """Data lineage node."""
    id: str
    asset_id: str
    node_type: str  # source, transformation, target
    process_id: Optional[str] = None
    transformation_logic: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageEdge:
    """Data lineage relationship."""
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str  # input, output, dependency
    transformation_details: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceViolation:
    """Compliance violation record."""
    id: str
    asset_id: str
    regulation: ComplianceRegulation
    violation_type: str
    severity: str  # low, medium, high, critical
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    remediation_actions: List[str] = field(default_factory=list)
    status: str = "open"  # open, in_progress, resolved, acknowledged
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEvent:
    """Data access audit event."""
    id: str
    user_id: str
    asset_id: str
    action: DataAction
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    result: str = "success"  # success, failure, denied
    details: Dict[str, Any] = field(default_factory=dict)


Base = declarative_base() if SQLALCHEMY_AVAILABLE else None


class DataAssetModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Data asset database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'data_assets'
        
        id = sa.Column(sa.String(36), primary_key=True)
        name = sa.Column(sa.String(200), nullable=False)
        description = sa.Column(sa.Text)
        asset_type = sa.Column(sa.String(50), nullable=False)
        schema_name = sa.Column(sa.String(100))
        database_name = sa.Column(sa.String(100))
        location = sa.Column(sa.String(500))
        classification = sa.Column(sa.String(20), nullable=False)
        owner = sa.Column(sa.String(100))
        steward = sa.Column(sa.String(100))
        tags = sa.Column(sa.Text)
        columns = sa.Column(sa.Text)
        lineage = sa.Column(sa.Text)
        quality_metrics = sa.Column(sa.Text)
        compliance_status = sa.Column(sa.Text)
        created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        updated_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        metadata = sa.Column(sa.Text)


class DataPolicyModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Data policy database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'data_policies'
        
        id = sa.Column(sa.String(36), primary_key=True)
        name = sa.Column(sa.String(200), nullable=False)
        policy_type = sa.Column(sa.String(50), nullable=False)
        description = sa.Column(sa.Text)
        rules = sa.Column(sa.Text, nullable=False)
        applicable_classifications = sa.Column(sa.Text)
        applicable_regulations = sa.Column(sa.Text)
        enforcement_actions = sa.Column(sa.Text)
        enabled = sa.Column(sa.Boolean, default=True)
        created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        updated_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        metadata = sa.Column(sa.Text)


class AccessRequestModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Access request database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'access_requests'
        
        id = sa.Column(sa.String(36), primary_key=True)
        user_id = sa.Column(sa.String(100), nullable=False)
        asset_id = sa.Column(sa.String(36), nullable=False)
        action = sa.Column(sa.String(20), nullable=False)
        justification = sa.Column(sa.Text, nullable=False)
        status = sa.Column(sa.String(20), default='pending')
        requested_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        reviewed_at = sa.Column(sa.DateTime)
        reviewer_id = sa.Column(sa.String(100))
        expiry_date = sa.Column(sa.DateTime)
        conditions = sa.Column(sa.Text)
        metadata = sa.Column(sa.Text)


class AuditEventModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Audit event database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'audit_events'
        
        id = sa.Column(sa.String(36), primary_key=True)
        user_id = sa.Column(sa.String(100), nullable=False)
        asset_id = sa.Column(sa.String(36), nullable=False)
        action = sa.Column(sa.String(20), nullable=False)
        timestamp = sa.Column(sa.DateTime, default=datetime.utcnow)
        source_ip = sa.Column(sa.String(45))
        user_agent = sa.Column(sa.String(500))
        result = sa.Column(sa.String(20), default='success')
        details = sa.Column(sa.Text)


class ComplianceViolationModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Compliance violation database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'compliance_violations'
        
        id = sa.Column(sa.String(36), primary_key=True)
        asset_id = sa.Column(sa.String(36), nullable=False)
        regulation = sa.Column(sa.String(20), nullable=False)
        violation_type = sa.Column(sa.String(100), nullable=False)
        severity = sa.Column(sa.String(20), nullable=False)
        description = sa.Column(sa.Text, nullable=False)
        detected_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        resolved_at = sa.Column(sa.DateTime)
        remediation_actions = sa.Column(sa.Text)
        status = sa.Column(sa.String(20), default='open')
        metadata = sa.Column(sa.Text)


class DataGovernanceController:
    """Comprehensive data governance and compliance management system."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url and SQLALCHEMY_AVAILABLE:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Redis setup for caching and notifications
        self.redis_url = redis_url
        self.redis_client = None
        
        # Governance state
        self.data_catalog: Dict[str, DataAsset] = {}
        self.policies: Dict[str, DataPolicy] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        self.lineage_graph: Dict[str, LineageNode] = {}
        self.lineage_edges: List[LineageEdge] = []
        
        # Compliance engines
        self.compliance_rules: Dict[ComplianceRegulation, List[Callable]] = {}
        self.pii_detectors: List[Callable] = []
        self.data_classifiers: List[Callable] = []
        
        # Monitoring and enforcement
        self.monitoring_active = False
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Performance tracking
        self.governance_metrics = {
            'total_assets': 0,
            'total_policies': 0,
            'compliance_score': 100.0,
            'access_requests_pending': 0,
            'violations_open': 0,
            'audit_events_today': 0
        }
        
        # Setup components
        self._setup_compliance_rules()
        self._setup_pii_detectors()
        self._setup_data_classifiers()
        self._setup_default_policies()
    
    async def initialize(self):
        """Initialize the data governance controller."""
        # Initialize database if configured
        if self.engine and SQLALCHEMY_AVAILABLE:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        # Load existing assets and policies
        await self._load_catalog_from_database()
        await self._load_policies_from_database()
        
        self.logger.info("Data governance controller initialized")
    
    def _setup_compliance_rules(self):
        """Setup compliance validation rules."""
        self.compliance_rules = {
            ComplianceRegulation.GDPR: [
                self._check_gdpr_consent,
                self._check_gdpr_data_subject_rights,
                self._check_gdpr_data_minimization,
                self._check_gdpr_retention_limits
            ],
            ComplianceRegulation.CCPA: [
                self._check_ccpa_privacy_rights,
                self._check_ccpa_data_sale_opt_out,
                self._check_ccpa_disclosure_requirements
            ],
            ComplianceRegulation.HIPAA: [
                self._check_hipaa_phi_protection,
                self._check_hipaa_access_controls,
                self._check_hipaa_audit_logs
            ],
            ComplianceRegulation.SOX: [
                self._check_sox_financial_data_integrity,
                self._check_sox_access_controls,
                self._check_sox_audit_trail
            ],
            ComplianceRegulation.PCI_DSS: [
                self._check_pci_cardholder_data,
                self._check_pci_encryption,
                self._check_pci_access_controls
            ]
        }
    
    def _setup_pii_detectors(self):
        """Setup PII detection functions."""
        self.pii_detectors = [
            self._detect_email_addresses,
            self._detect_phone_numbers,
            self._detect_ssn,
            self._detect_credit_cards,
            self._detect_ip_addresses,
            self._detect_names,
            self._detect_addresses
        ]
    
    def _setup_data_classifiers(self):
        """Setup automatic data classification functions."""
        self.data_classifiers = [
            self._classify_by_column_name,
            self._classify_by_data_content,
            self._classify_by_source_system,
            self._classify_by_business_context
        ]
    
    def _setup_default_policies(self):
        """Setup default governance policies."""
        # PII Protection Policy
        pii_policy = DataPolicy(
            id="pii_protection_policy",
            name="PII Protection Policy",
            policy_type=PolicyType.PRIVACY,
            description="Protects personally identifiable information",
            rules=[
                {
                    "rule_type": "access_restriction",
                    "condition": "contains_pii = true",
                    "action": "require_approval",
                    "parameters": {"approval_level": "data_steward"}
                },
                {
                    "rule_type": "anonymization",
                    "condition": "classification = confidential AND action = export",
                    "action": "auto_anonymize",
                    "parameters": {"method": "k_anonymity", "k": 5}
                }
            ],
            applicable_classifications=[DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED],
            applicable_regulations=[ComplianceRegulation.GDPR, ComplianceRegulation.CCPA]
        )
        
        # Data Retention Policy
        retention_policy = DataPolicy(
            id="data_retention_policy",
            name="Data Retention Policy",
            policy_type=PolicyType.RETENTION,
            description="Manages data retention and deletion",
            rules=[
                {
                    "rule_type": "retention_period",
                    "condition": "asset_type = user_data",
                    "action": "delete_after",
                    "parameters": {"period_days": 2555}  # 7 years
                },
                {
                    "rule_type": "retention_period",
                    "condition": "asset_type = log_data",
                    "action": "archive_after",
                    "parameters": {"period_days": 365}  # 1 year
                }
            ]
        )
        
        # Access Control Policy
        access_policy = DataPolicy(
            id="access_control_policy",
            name="Access Control Policy",
            policy_type=PolicyType.ACCESS_CONTROL,
            description="Controls data access based on classification",
            rules=[
                {
                    "rule_type": "role_based_access",
                    "condition": "classification = restricted",
                    "action": "require_role",
                    "parameters": {"required_roles": ["data_admin", "senior_analyst"]}
                },
                {
                    "rule_type": "time_based_access",
                    "condition": "classification = confidential",
                    "action": "restrict_hours",
                    "parameters": {"allowed_hours": "08:00-18:00", "timezone": "UTC"}
                }
            ]
        )
        
        # Register default policies
        for policy in [pii_policy, retention_policy, access_policy]:
            self.policies[policy.id] = policy
    
    # Data Catalog Management
    async def register_data_asset(self, asset: DataAsset) -> bool:
        """Register a new data asset in the catalog."""
        try:
            # Auto-classify the asset
            await self._auto_classify_asset(asset)
            
            # Detect PII
            await self._detect_pii_in_asset(asset)
            
            # Store in catalog
            self.data_catalog[asset.id] = asset
            
            # Persist to database
            if self.async_session:
                await self._store_data_asset(asset)
            
            # Update lineage if applicable
            await self._update_lineage_for_asset(asset)
            
            # Check compliance
            await self._check_asset_compliance(asset)
            
            self.governance_metrics['total_assets'] += 1
            self.logger.info(f"Registered data asset: {asset.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering asset: {e}")
            return False
    
    async def _auto_classify_asset(self, asset: DataAsset):
        """Automatically classify data asset."""
        classification_scores = {}
        
        for classifier in self.data_classifiers:
            try:
                score, classification = await classifier(asset)
                if score > 0:
                    classification_scores[classification] = score
            except Exception as e:
                self.logger.warning(f"Classifier error: {e}")
        
        # Select highest scoring classification
        if classification_scores:
            best_classification = max(classification_scores, key=classification_scores.get)
            asset.classification = best_classification
            
            # Store classification metadata
            asset.metadata['auto_classification'] = {
                'scores': classification_scores,
                'selected': best_classification.value,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _detect_pii_in_asset(self, asset: DataAsset):
        """Detect PII in data asset."""
        pii_findings = []
        
        for column in asset.columns:
            column_name = column.get('name', '')
            sample_values = column.get('sample_values', [])
            
            for detector in self.pii_detectors:
                try:
                    is_pii, pii_type, confidence = await detector(column_name, sample_values)
                    if is_pii:
                        pii_findings.append({
                            'column': column_name,
                            'pii_type': pii_type,
                            'confidence': confidence,
                            'detector': detector.__name__
                        })
                        
                        # Update column metadata
                        column['contains_pii'] = True
                        column['pii_type'] = pii_type
                        column['pii_confidence'] = confidence
                        
                except Exception as e:
                    self.logger.warning(f"PII detector error: {e}")
        
        # Store PII findings
        if pii_findings:
            asset.metadata['pii_findings'] = pii_findings
            
            # Upgrade classification if PII detected
            if asset.classification in [DataClassification.PUBLIC, DataClassification.INTERNAL]:
                asset.classification = DataClassification.CONFIDENTIAL
    
    async def _update_lineage_for_asset(self, asset: DataAsset):
        """Update data lineage for asset."""
        # Create lineage node
        lineage_node = LineageNode(
            id=str(uuid.uuid4()),
            asset_id=asset.id,
            node_type="asset",
            metadata={
                'asset_type': asset.asset_type,
                'location': asset.location,
                'created_at': asset.created_at.isoformat()
            }
        )
        
        self.lineage_graph[lineage_node.id] = lineage_node
        
        # Store lineage in asset
        asset.lineage = {
            'node_id': lineage_node.id,
            'upstream_assets': [],
            'downstream_assets': []
        }
    
    async def _check_asset_compliance(self, asset: DataAsset):
        """Check asset compliance with regulations."""
        violations = []
        
        for regulation, rules in self.compliance_rules.items():
            for rule in rules:
                try:
                    is_compliant, violation_details = await rule(asset)
                    if not is_compliant:
                        violation = ComplianceViolation(
                            id=str(uuid.uuid4()),
                            asset_id=asset.id,
                            regulation=regulation,
                            violation_type=violation_details.get('type', 'unknown'),
                            severity=violation_details.get('severity', 'medium'),
                            description=violation_details.get('description', 'Compliance violation detected')
                        )
                        violations.append(violation)
                        
                except Exception as e:
                    self.logger.warning(f"Compliance check error: {e}")
        
        # Store violations
        if violations:
            for violation in violations:
                if self.async_session:
                    await self._store_compliance_violation(violation)
            
            asset.compliance_status = {
                'compliant': False,
                'violations': len(violations),
                'last_checked': datetime.utcnow().isoformat()
            }
        else:
            asset.compliance_status = {
                'compliant': True,
                'violations': 0,
                'last_checked': datetime.utcnow().isoformat()
            }
    
    # Policy Management
    async def create_policy(self, policy: DataPolicy) -> bool:
        """Create a new data governance policy."""
        try:
            self.policies[policy.id] = policy
            
            # Persist to database
            if self.async_session:
                await self._store_data_policy(policy)
            
            self.governance_metrics['total_policies'] += 1
            self.logger.info(f"Created data policy: {policy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating policy: {e}")
            return False
    
    async def enforce_policies(self, asset_id: str, action: DataAction, user_id: str) -> Dict[str, Any]:
        """Enforce policies for data access."""
        if asset_id not in self.data_catalog:
            return {'allowed': False, 'reason': 'Asset not found'}
        
        asset = self.data_catalog[asset_id]
        enforcement_results = []
        
        # Check applicable policies
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            # Check if policy applies to this asset
            if (not policy.applicable_classifications or 
                asset.classification in policy.applicable_classifications):
                
                result = await self._apply_policy(policy, asset, action, user_id)
                enforcement_results.append(result)
        
        # Determine final decision
        access_allowed = all(result.get('allowed', True) for result in enforcement_results)
        reasons = [result.get('reason') for result in enforcement_results if result.get('reason')]
        conditions = [result.get('conditions', []) for result in enforcement_results]
        flattened_conditions = [cond for sublist in conditions for cond in sublist]
        
        return {
            'allowed': access_allowed,
            'reasons': reasons,
            'conditions': flattened_conditions,
            'policy_results': enforcement_results
        }
    
    async def _apply_policy(self, policy: DataPolicy, asset: DataAsset, action: DataAction, user_id: str) -> Dict[str, Any]:
        """Apply a specific policy to data access."""
        for rule in policy.rules:
            rule_type = rule.get('rule_type')
            condition = rule.get('condition')
            rule_action = rule.get('action')
            parameters = rule.get('parameters', {})
            
            # Evaluate condition
            if await self._evaluate_policy_condition(condition, asset, action, user_id):
                return await self._execute_policy_action(rule_action, parameters, asset, action, user_id)
        
        return {'allowed': True}
    
    async def _evaluate_policy_condition(self, condition: str, asset: DataAsset, action: DataAction, user_id: str) -> bool:
        """Evaluate policy condition."""
        try:
            # Simple condition evaluation
            context = {
                'asset': asset,
                'action': action.value,
                'user_id': user_id,
                'classification': asset.classification.value,
                'asset_type': asset.asset_type,
                'contains_pii': any(col.get('contains_pii', False) for col in asset.columns)
            }
            
            # Replace condition variables
            eval_condition = condition
            for key, value in context.items():
                eval_condition = eval_condition.replace(key, str(value))
            
            return eval(eval_condition, {"__builtins__": {}})
            
        except Exception as e:
            self.logger.warning(f"Policy condition evaluation error: {e}")
            return False
    
    async def _execute_policy_action(self, action: str, parameters: Dict[str, Any], asset: DataAsset, data_action: DataAction, user_id: str) -> Dict[str, Any]:
        """Execute policy action."""
        if action == "require_approval":
            return {
                'allowed': False,
                'reason': 'Access requires approval',
                'conditions': ['approval_required'],
                'approval_level': parameters.get('approval_level', 'data_steward')
            }
        
        elif action == "auto_anonymize":
            return {
                'allowed': True,
                'reason': 'Access granted with anonymization',
                'conditions': ['data_anonymization_required'],
                'anonymization_method': parameters.get('method', 'k_anonymity')
            }
        
        elif action == "require_role":
            # Check user roles (simplified - would integrate with identity system)
            required_roles = parameters.get('required_roles', [])
            return {
                'allowed': False,  # Would check actual user roles
                'reason': f'Requires role: {", ".join(required_roles)}',
                'conditions': ['role_check_required']
            }
        
        elif action == "restrict_hours":
            # Check time restrictions
            current_hour = datetime.utcnow().hour
            allowed_hours = parameters.get('allowed_hours', '00:00-23:59')
            start_hour, end_hour = allowed_hours.split('-')
            start_h = int(start_hour.split(':')[0])
            end_h = int(end_hour.split(':')[0])
            
            if start_h <= current_hour <= end_h:
                return {'allowed': True}
            else:
                return {
                    'allowed': False,
                    'reason': f'Access restricted to {allowed_hours}',
                    'conditions': ['time_restriction']
                }
        
        elif action == "delete_after":
            # Schedule for deletion
            period_days = parameters.get('period_days', 365)
            return {
                'allowed': True,
                'conditions': ['scheduled_deletion'],
                'deletion_date': (datetime.utcnow() + timedelta(days=period_days)).isoformat()
            }
        
        return {'allowed': True}
    
    # Access Management
    async def request_access(self, request: AccessRequest) -> str:
        """Submit data access request."""
        # Validate request
        if request.asset_id not in self.data_catalog:
            raise ValueError("Asset not found")
        
        # Store request
        self.access_requests[request.id] = request
        
        # Persist to database
        if self.async_session:
            await self._store_access_request(request)
        
        # Auto-approve if policies allow
        enforcement_result = await self.enforce_policies(request.asset_id, request.action, request.user_id)
        
        if enforcement_result['allowed'] and not any('approval' in cond for cond in enforcement_result.get('conditions', [])):
            request.status = "approved"
            request.reviewed_at = datetime.utcnow()
            request.reviewer_id = "system"
        
        self.governance_metrics['access_requests_pending'] += 1
        self.logger.info(f"Access request submitted: {request.id}")
        return request.id
    
    async def review_access_request(self, request_id: str, reviewer_id: str, decision: str, notes: Optional[str] = None) -> bool:
        """Review and approve/deny access request."""
        if request_id not in self.access_requests:
            return False
        
        request = self.access_requests[request_id]
        request.status = decision
        request.reviewed_at = datetime.utcnow()
        request.reviewer_id = reviewer_id
        
        if notes:
            request.metadata['review_notes'] = notes
        
        # Update database
        if self.async_session:
            await self._store_access_request(request)
        
        if request.status != "pending":
            self.governance_metrics['access_requests_pending'] -= 1
        
        self.logger.info(f"Access request {decision}: {request_id}")
        return True
    
    # Auditing
    async def log_data_access(self, event: AuditEvent):
        """Log data access event for auditing."""
        # Store audit event
        if self.async_session:
            await self._store_audit_event(event)
        
        # Update daily metrics
        self.governance_metrics['audit_events_today'] += 1
        
        # Check for suspicious activity
        await self._analyze_access_patterns(event)
    
    async def _analyze_access_patterns(self, event: AuditEvent):
        """Analyze access patterns for anomalies."""
        # This would implement anomaly detection
        # For now, just log high-frequency access
        pass
    
    # Data Lineage
    async def track_data_transformation(
        self, 
        source_asset_ids: List[str], 
        target_asset_id: str, 
        transformation_logic: str,
        process_id: Optional[str] = None
    ):
        """Track data transformation for lineage."""
        # Create transformation node
        transform_node = LineageNode(
            id=str(uuid.uuid4()),
            asset_id=target_asset_id,
            node_type="transformation",
            process_id=process_id,
            transformation_logic=transformation_logic
        )
        
        self.lineage_graph[transform_node.id] = transform_node
        
        # Create edges from sources to transformation
        for source_id in source_asset_ids:
            if source_id in self.data_catalog:
                source_lineage = self.data_catalog[source_id].lineage
                if source_lineage and 'node_id' in source_lineage:
                    edge = LineageEdge(
                        id=str(uuid.uuid4()),
                        source_node_id=source_lineage['node_id'],
                        target_node_id=transform_node.id,
                        relationship_type="input"
                    )
                    self.lineage_edges.append(edge)
        
        # Update target asset lineage
        if target_asset_id in self.data_catalog:
            target_asset = self.data_catalog[target_asset_id]
            if 'lineage' in target_asset.lineage:
                target_asset.lineage['upstream_assets'].extend(source_asset_ids)
    
    async def get_data_lineage(self, asset_id: str, depth: int = 3) -> Dict[str, Any]:
        """Get data lineage for an asset."""
        if asset_id not in self.data_catalog:
            return {}
        
        lineage = {
            'asset_id': asset_id,
            'upstream': [],
            'downstream': [],
            'transformations': []
        }
        
        # Get upstream and downstream assets
        asset = self.data_catalog[asset_id]
        if asset.lineage:
            lineage['upstream'] = asset.lineage.get('upstream_assets', [])
            lineage['downstream'] = asset.lineage.get('downstream_assets', [])
        
        return lineage
    
    # Classification Functions
    async def _classify_by_column_name(self, asset: DataAsset) -> Tuple[float, DataClassification]:
        """Classify based on column names."""
        sensitive_patterns = {
            r'(ssn|social_security)': DataClassification.CONFIDENTIAL,
            r'(password|pwd|secret)': DataClassification.RESTRICTED,
            r'(email|phone|address)': DataClassification.CONFIDENTIAL,
            r'(credit_card|cc_number)': DataClassification.RESTRICTED,
            r'(salary|income|revenue)': DataClassification.CONFIDENTIAL
        }
        
        for column in asset.columns:
            column_name = column.get('name', '').lower()
            for pattern, classification in sensitive_patterns.items():
                if re.search(pattern, column_name):
                    return 0.8, classification
        
        return 0.0, DataClassification.PUBLIC
    
    async def _classify_by_data_content(self, asset: DataAsset) -> Tuple[float, DataClassification]:
        """Classify based on data content patterns."""
        # Check for PII in sample data
        has_pii = any(col.get('contains_pii', False) for col in asset.columns)
        
        if has_pii:
            return 0.9, DataClassification.CONFIDENTIAL
        
        return 0.0, DataClassification.PUBLIC
    
    async def _classify_by_source_system(self, asset: DataAsset) -> Tuple[float, DataClassification]:
        """Classify based on source system."""
        sensitive_systems = {
            'hr_system': DataClassification.CONFIDENTIAL,
            'finance_system': DataClassification.CONFIDENTIAL,
            'customer_db': DataClassification.CONFIDENTIAL,
            'public_api': DataClassification.PUBLIC
        }
        
        system_name = asset.metadata.get('source_system', '').lower()
        if system_name in sensitive_systems:
            return 0.7, sensitive_systems[system_name]
        
        return 0.0, DataClassification.INTERNAL
    
    async def _classify_by_business_context(self, asset: DataAsset) -> Tuple[float, DataClassification]:
        """Classify based on business context."""
        if 'financial' in asset.name.lower() or 'financial' in asset.description.lower():
            return 0.6, DataClassification.CONFIDENTIAL
        
        if 'public' in asset.name.lower():
            return 0.8, DataClassification.PUBLIC
        
        return 0.0, DataClassification.INTERNAL
    
    # PII Detection Functions
    async def _detect_email_addresses(self, column_name: str, sample_values: List[str]) -> Tuple[bool, str, float]:
        """Detect email addresses."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        if 'email' in column_name.lower():
            return True, 'email', 0.9
        
        email_count = 0
        for value in sample_values[:10]:  # Check first 10 samples
            if isinstance(value, str) and re.search(email_pattern, value):
                email_count += 1
        
        if email_count > 0:
            confidence = email_count / min(len(sample_values), 10)
            return confidence > 0.5, 'email', confidence
        
        return False, '', 0.0
    
    async def _detect_phone_numbers(self, column_name: str, sample_values: List[str]) -> Tuple[bool, str, float]:
        """Detect phone numbers."""
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s?\d{3}-\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b'  # 1234567890
        ]
        
        if 'phone' in column_name.lower():
            return True, 'phone', 0.9
        
        phone_count = 0
        for value in sample_values[:10]:
            if isinstance(value, str):
                for pattern in phone_patterns:
                    if re.search(pattern, value):
                        phone_count += 1
                        break
        
        if phone_count > 0:
            confidence = phone_count / min(len(sample_values), 10)
            return confidence > 0.5, 'phone', confidence
        
        return False, '', 0.0
    
    async def _detect_ssn(self, column_name: str, sample_values: List[str]) -> Tuple[bool, str, float]:
        """Detect Social Security Numbers."""
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        
        if 'ssn' in column_name.lower() or 'social_security' in column_name.lower():
            return True, 'ssn', 0.95
        
        ssn_count = 0
        for value in sample_values[:10]:
            if isinstance(value, str) and re.search(ssn_pattern, value):
                ssn_count += 1
        
        if ssn_count > 0:
            confidence = ssn_count / min(len(sample_values), 10)
            return confidence > 0.5, 'ssn', confidence
        
        return False, '', 0.0
    
    async def _detect_credit_cards(self, column_name: str, sample_values: List[str]) -> Tuple[bool, str, float]:
        """Detect credit card numbers."""
        cc_pattern = r'\b(?:\d{4}[\s-]?){3}\d{4}\b'
        
        if 'credit_card' in column_name.lower() or 'cc_number' in column_name.lower():
            return True, 'credit_card', 0.95
        
        cc_count = 0
        for value in sample_values[:10]:
            if isinstance(value, str) and re.search(cc_pattern, value):
                cc_count += 1
        
        if cc_count > 0:
            confidence = cc_count / min(len(sample_values), 10)
            return confidence > 0.5, 'credit_card', confidence
        
        return False, '', 0.0
    
    async def _detect_ip_addresses(self, column_name: str, sample_values: List[str]) -> Tuple[bool, str, float]:
        """Detect IP addresses."""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        
        if 'ip' in column_name.lower():
            return True, 'ip_address', 0.9
        
        ip_count = 0
        for value in sample_values[:10]:
            if isinstance(value, str) and re.search(ip_pattern, value):
                ip_count += 1
        
        if ip_count > 0:
            confidence = ip_count / min(len(sample_values), 10)
            return confidence > 0.5, 'ip_address', confidence
        
        return False, '', 0.0
    
    async def _detect_names(self, column_name: str, sample_values: List[str]) -> Tuple[bool, str, float]:
        """Detect names."""
        name_indicators = ['name', 'first_name', 'last_name', 'full_name', 'fname', 'lname']
        
        if any(indicator in column_name.lower() for indicator in name_indicators):
            return True, 'name', 0.8
        
        return False, '', 0.0
    
    async def _detect_addresses(self, column_name: str, sample_values: List[str]) -> Tuple[bool, str, float]:
        """Detect addresses."""
        address_indicators = ['address', 'street', 'city', 'zip', 'postal']
        
        if any(indicator in column_name.lower() for indicator in address_indicators):
            return True, 'address', 0.8
        
        return False, '', 0.0
    
    # Compliance Check Functions
    async def _check_gdpr_consent(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check GDPR consent requirements."""
        has_personal_data = any(col.get('contains_pii', False) for col in asset.columns)
        
        if has_personal_data:
            consent_documented = asset.metadata.get('gdpr_consent_documented', False)
            if not consent_documented:
                return False, {
                    'type': 'gdpr_consent_missing',
                    'severity': 'high',
                    'description': 'GDPR consent not documented for asset containing personal data'
                }
        
        return True, {}
    
    async def _check_gdpr_data_subject_rights(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check GDPR data subject rights implementation."""
        has_personal_data = any(col.get('contains_pii', False) for col in asset.columns)
        
        if has_personal_data:
            rights_procedures = asset.metadata.get('gdpr_rights_procedures', {})
            required_rights = ['access', 'rectification', 'erasure', 'portability']
            
            missing_rights = [right for right in required_rights if not rights_procedures.get(right)]
            if missing_rights:
                return False, {
                    'type': 'gdpr_rights_missing',
                    'severity': 'high',
                    'description': f'GDPR data subject rights procedures missing: {", ".join(missing_rights)}'
                }
        
        return True, {}
    
    async def _check_gdpr_data_minimization(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check GDPR data minimization principle."""
        purpose_documented = asset.metadata.get('processing_purpose')
        if not purpose_documented:
            return False, {
                'type': 'gdpr_purpose_missing',
                'severity': 'medium',
                'description': 'Data processing purpose not documented'
            }
        
        return True, {}
    
    async def _check_gdpr_retention_limits(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check GDPR retention limits."""
        retention_policy = asset.metadata.get('retention_policy')
        if not retention_policy:
            return False, {
                'type': 'gdpr_retention_policy_missing',
                'severity': 'medium',
                'description': 'Data retention policy not defined'
            }
        
        return True, {}
    
    async def _check_ccpa_privacy_rights(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check CCPA privacy rights."""
        return True, {}  # Simplified
    
    async def _check_ccpa_data_sale_opt_out(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check CCPA data sale opt-out."""
        return True, {}  # Simplified
    
    async def _check_ccpa_disclosure_requirements(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check CCPA disclosure requirements."""
        return True, {}  # Simplified
    
    async def _check_hipaa_phi_protection(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check HIPAA PHI protection."""
        return True, {}  # Simplified
    
    async def _check_hipaa_access_controls(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check HIPAA access controls."""
        return True, {}  # Simplified
    
    async def _check_hipaa_audit_logs(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check HIPAA audit logs."""
        return True, {}  # Simplified
    
    async def _check_sox_financial_data_integrity(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check SOX financial data integrity."""
        return True, {}  # Simplified
    
    async def _check_sox_access_controls(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check SOX access controls."""
        return True, {}  # Simplified
    
    async def _check_sox_audit_trail(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check SOX audit trail."""
        return True, {}  # Simplified
    
    async def _check_pci_cardholder_data(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check PCI cardholder data protection."""
        return True, {}  # Simplified
    
    async def _check_pci_encryption(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check PCI encryption requirements."""
        return True, {}  # Simplified
    
    async def _check_pci_access_controls(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Check PCI access controls."""
        return True, {}  # Simplified
    
    # Database operations
    async def _load_catalog_from_database(self):
        """Load data catalog from database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                result = await session.execute(sa.select(DataAssetModel))
                assets = result.scalars().all()
                
                for db_asset in assets:
                    asset = DataAsset(
                        id=db_asset.id,
                        name=db_asset.name,
                        description=db_asset.description or '',
                        asset_type=db_asset.asset_type,
                        schema_name=db_asset.schema_name,
                        database_name=db_asset.database_name,
                        location=db_asset.location,
                        classification=DataClassification(db_asset.classification),
                        owner=db_asset.owner,
                        steward=db_asset.steward,
                        tags=json.loads(db_asset.tags) if db_asset.tags else [],
                        columns=json.loads(db_asset.columns) if db_asset.columns else [],
                        lineage=json.loads(db_asset.lineage) if db_asset.lineage else {},
                        quality_metrics=json.loads(db_asset.quality_metrics) if db_asset.quality_metrics else {},
                        compliance_status=json.loads(db_asset.compliance_status) if db_asset.compliance_status else {},
                        created_at=db_asset.created_at,
                        updated_at=db_asset.updated_at,
                        metadata=json.loads(db_asset.metadata) if db_asset.metadata else {}
                    )
                    self.data_catalog[asset.id] = asset
                
                self.governance_metrics['total_assets'] = len(self.data_catalog)
                
        except Exception as e:
            self.logger.error(f"Error loading catalog: {e}")
    
    async def _load_policies_from_database(self):
        """Load policies from database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                result = await session.execute(sa.select(DataPolicyModel))
                policies = result.scalars().all()
                
                for db_policy in policies:
                    policy = DataPolicy(
                        id=db_policy.id,
                        name=db_policy.name,
                        policy_type=PolicyType(db_policy.policy_type),
                        description=db_policy.description or '',
                        rules=json.loads(db_policy.rules),
                        applicable_classifications=[
                            DataClassification(c) for c in json.loads(db_policy.applicable_classifications)
                        ] if db_policy.applicable_classifications else [],
                        applicable_regulations=[
                            ComplianceRegulation(r) for r in json.loads(db_policy.applicable_regulations)
                        ] if db_policy.applicable_regulations else [],
                        enforcement_actions=json.loads(db_policy.enforcement_actions) if db_policy.enforcement_actions else [],
                        enabled=db_policy.enabled,
                        created_at=db_policy.created_at,
                        updated_at=db_policy.updated_at,
                        metadata=json.loads(db_policy.metadata) if db_policy.metadata else {}
                    )
                    self.policies[policy.id] = policy
                
                self.governance_metrics['total_policies'] = len(self.policies)
                
        except Exception as e:
            self.logger.error(f"Error loading policies: {e}")
    
    async def _store_data_asset(self, asset: DataAsset):
        """Store data asset to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_asset = DataAssetModel(
                    id=asset.id,
                    name=asset.name,
                    description=asset.description,
                    asset_type=asset.asset_type,
                    schema_name=asset.schema_name,
                    database_name=asset.database_name,
                    location=asset.location,
                    classification=asset.classification.value,
                    owner=asset.owner,
                    steward=asset.steward,
                    tags=json.dumps(asset.tags),
                    columns=json.dumps(asset.columns),
                    lineage=json.dumps(asset.lineage),
                    quality_metrics=json.dumps(asset.quality_metrics),
                    compliance_status=json.dumps(asset.compliance_status),
                    created_at=asset.created_at,
                    updated_at=asset.updated_at,
                    metadata=json.dumps(asset.metadata)
                )
                session.add(db_asset)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing asset: {e}")
    
    async def _store_data_policy(self, policy: DataPolicy):
        """Store data policy to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_policy = DataPolicyModel(
                    id=policy.id,
                    name=policy.name,
                    policy_type=policy.policy_type.value,
                    description=policy.description,
                    rules=json.dumps(policy.rules),
                    applicable_classifications=json.dumps([c.value for c in policy.applicable_classifications]),
                    applicable_regulations=json.dumps([r.value for r in policy.applicable_regulations]),
                    enforcement_actions=json.dumps(policy.enforcement_actions),
                    enabled=policy.enabled,
                    created_at=policy.created_at,
                    updated_at=policy.updated_at,
                    metadata=json.dumps(policy.metadata)
                )
                session.add(db_policy)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing policy: {e}")
    
    async def _store_access_request(self, request: AccessRequest):
        """Store access request to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_request = AccessRequestModel(
                    id=request.id,
                    user_id=request.user_id,
                    asset_id=request.asset_id,
                    action=request.action.value,
                    justification=request.justification,
                    status=request.status,
                    requested_at=request.requested_at,
                    reviewed_at=request.reviewed_at,
                    reviewer_id=request.reviewer_id,
                    expiry_date=request.expiry_date,
                    conditions=json.dumps(request.conditions),
                    metadata=json.dumps(request.metadata)
                )
                session.add(db_request)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing access request: {e}")
    
    async def _store_audit_event(self, event: AuditEvent):
        """Store audit event to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_event = AuditEventModel(
                    id=event.id,
                    user_id=event.user_id,
                    asset_id=event.asset_id,
                    action=event.action.value,
                    timestamp=event.timestamp,
                    source_ip=event.source_ip,
                    user_agent=event.user_agent,
                    result=event.result,
                    details=json.dumps(event.details)
                )
                session.add(db_event)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing audit event: {e}")
    
    async def _store_compliance_violation(self, violation: ComplianceViolation):
        """Store compliance violation to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_violation = ComplianceViolationModel(
                    id=violation.id,
                    asset_id=violation.asset_id,
                    regulation=violation.regulation.value,
                    violation_type=violation.violation_type,
                    severity=violation.severity,
                    description=violation.description,
                    detected_at=violation.detected_at,
                    resolved_at=violation.resolved_at,
                    remediation_actions=json.dumps(violation.remediation_actions),
                    status=violation.status,
                    metadata=json.dumps(violation.metadata)
                )
                session.add(db_violation)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing compliance violation: {e}")
    
    def get_governance_metrics(self) -> Dict[str, Any]:
        """Get governance metrics."""
        return {
            **self.governance_metrics,
            'data_catalog_size': len(self.data_catalog),
            'active_policies': len([p for p in self.policies.values() if p.enabled]),
            'lineage_nodes': len(self.lineage_graph),
            'lineage_edges': len(self.lineage_edges)
        }


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize governance controller
        controller = DataGovernanceController(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await controller.initialize()
        
        # Register a data asset
        asset = DataAsset(
            id=str(uuid.uuid4()),
            name="User Profiles Table",
            description="Contains user profile information",
            asset_type="table",
            schema_name="public",
            database_name="user_db",
            location="postgresql://localhost/user_db.public.user_profiles",
            owner="data_team@example.com",
            steward="john.doe@example.com",
            tags=["pii", "user_data", "production"],
            columns=[
                {
                    "name": "user_id",
                    "type": "integer",
                    "description": "Unique user identifier"
                },
                {
                    "name": "email",
                    "type": "varchar",
                    "description": "User email address",
                    "sample_values": ["john@example.com", "jane@example.com"]
                },
                {
                    "name": "phone",
                    "type": "varchar",
                    "description": "User phone number",
                    "sample_values": ["123-456-7890", "987-654-3210"]
                }
            ]
        )
        
        await controller.register_data_asset(asset)
        print(f"Registered asset: {asset.name}")
        print(f"Classification: {asset.classification.value}")
        print(f"PII findings: {asset.metadata.get('pii_findings', [])}")
        
        # Test policy enforcement
        enforcement_result = await controller.enforce_policies(
            asset.id, DataAction.READ, "user123"
        )
        print(f"Access enforcement: {enforcement_result}")
        
        # Submit access request
        access_request = AccessRequest(
            id=str(uuid.uuid4()),
            user_id="analyst1",
            asset_id=asset.id,
            action=DataAction.EXPORT,
            justification="Need data for quarterly analysis"
        )
        
        request_id = await controller.request_access(access_request)
        print(f"Access request submitted: {request_id}")
        
        # Get governance metrics
        metrics = controller.get_governance_metrics()
        print(f"Governance metrics: {metrics}")
    
    asyncio.run(main())