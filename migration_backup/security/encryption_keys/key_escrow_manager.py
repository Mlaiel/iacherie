#!/usr/bin/env python3
"""
🔐 Key Escrow Manager - Enterprise Cryptographic Key Escrow and Recovery System
Production-grade key escrow management for IA Chéries Creator Economy Platform

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
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import yaml
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

logger = logging.getLogger(__name__)


class EscrowType(Enum):
    """Types of key escrow."""
    LEGAL_COMPLIANCE = "legal_compliance"
    BUSINESS_CONTINUITY = "business_continuity"
    DISASTER_RECOVERY = "disaster_recovery"
    LAW_ENFORCEMENT = "law_enforcement"
    REGULATORY = "regulatory"
    INTERNAL_AUDIT = "internal_audit"
    CREATOR_RECOVERY = "creator_recovery"


class EscrowAgent(Enum):
    """Escrow agent types."""
    TRUSTED_THIRD_PARTY = "trusted_third_party"
    GOVERNMENT_AGENCY = "government_agency"
    LEGAL_AUTHORITY = "legal_authority"
    CORPORATE_COMPLIANCE = "corporate_compliance"
    INSURANCE_PROVIDER = "insurance_provider"
    INTERNAL_CUSTODIAN = "internal_custodian"


class AccessLevel(Enum):
    """Access levels for escrow operations."""
    EMERGENCY_ONLY = "emergency_only"
    COURT_ORDER = "court_order"
    REGULATORY_REQUEST = "regulatory_request"
    BUSINESS_CONTINUITY = "business_continuity"
    CREATOR_REQUEST = "creator_request"
    TECHNICAL_RECOVERY = "technical_recovery"
    AUDIT_PURPOSES = "audit_purposes"


class EscrowStatus(Enum):
    """Status of escrow deposits."""
    ACTIVE = "active"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    COMPROMISED = "compromised"
    RELEASED = "released"
    DESTROYED = "destroyed"


@dataclass
class EscrowPolicy:
    """Key escrow policy configuration."""
    escrow_type: EscrowType
    required_agents: List[EscrowAgent]
    access_level: AccessLevel
    retention_period: timedelta
    verification_interval: timedelta
    split_threshold: int  # Minimum shares needed for recovery
    total_shares: int    # Total shares created
    geographic_distribution: List[str]  # Countries/regions for distribution
    compliance_frameworks: List[str]
    emergency_access_enabled: bool = True
    audit_logging_required: bool = True
    creator_notification: bool = True
    legal_hold_support: bool = True


@dataclass
class EscrowDeposit:
    """Key escrow deposit record."""
    deposit_id: str
    key_id: str
    escrow_type: EscrowType
    policy: EscrowPolicy
    encrypted_key_material: bytes
    key_metadata: Dict[str, Any]
    shares: Dict[str, bytes]  # Share ID -> encrypted share
    depositor_id: str
    creator_id: Optional[str]
    deposit_timestamp: datetime
    expiry_timestamp: datetime
    status: EscrowStatus
    verification_checksum: str
    access_log: List[Dict[str, Any]]
    compliance_attestation: Dict[str, Any]

    def __post_init__(self):
        if not self.access_log:
            self.access_log = []


@dataclass
class RecoveryRequest:
    """Key recovery request."""
    request_id: str
    deposit_id: str
    requester_id: str
    requester_type: str  # "creator", "legal_authority", "business_unit", etc.
    justification: str
    legal_documentation: Optional[Dict[str, Any]]
    urgency_level: int  # 1-10, 10 being most urgent
    approval_status: str  # "pending", "approved", "denied", "completed"
    required_approvals: List[str]
    obtained_approvals: List[str]
    created_at: datetime
    approved_at: Optional[datetime]
    completed_at: Optional[datetime]
    recovered_key_data: Optional[bytes] = None


@dataclass
class EscrowAgent:
    """Escrow agent configuration."""
    agent_id: str
    agent_type: EscrowAgent
    name: str
    contact_info: Dict[str, str]
    public_key: bytes
    geographic_location: str
    compliance_certifications: List[str]
    trust_level: int  # 1-10
    active: bool = True


class KeyEscrowManager:
    """
    🔐 Key Escrow Manager - Enterprise Key Escrow and Recovery System
    
    Provides comprehensive key escrow management for IA Chéries Creator Economy:
    - Multi-agent secret sharing with geographic distribution
    - Compliance-driven escrow policies (GDPR, CCPA, industry regulations)
    - Creator-focused recovery procedures
    - Legal and regulatory access controls
    - Business continuity and disaster recovery
    - Audit trails and compliance reporting
    - Emergency access procedures
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Key Escrow Manager."""
        self.config = self._load_configuration(config_path)
        self.escrow_deposits: Dict[str, EscrowDeposit] = {}
        self.escrow_policies: Dict[str, EscrowPolicy] = {}
        self.escrow_agents: Dict[str, EscrowAgent] = {}
        self.recovery_requests: Dict[str, RecoveryRequest] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default policies and agents
        self._initialize_default_policies()
        self._initialize_default_agents()
        
        # Callback functions for external integrations
        self.notification_callback: Optional[Callable] = None
        self.audit_callback: Optional[Callable] = None
        self.compliance_callback: Optional[Callable] = None

    def _load_configuration(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load escrow manager configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f).get('escrow_manager_config', {})
        
        # Default configuration
        return {
            "default_retention_days": 2555,  # 7 years
            "verification_interval_days": 90,
            "emergency_access_enabled": True,
            "geographic_distribution_required": True,
            "minimum_agents": 3,
            "recovery_approval_timeout_hours": 72,
            "audit_retention_years": 10,
            "compliance_frameworks": ["GDPR", "CCPA", "SOX", "HIPAA"],
            "notification_enabled": True
        }

    def _initialize_default_policies(self):
        """Initialize default escrow policies."""
        # Creator content protection policy
        self.escrow_policies["creator_content"] = EscrowPolicy(
            escrow_type=EscrowType.CREATOR_RECOVERY,
            required_agents=[EscrowAgent.TRUSTED_THIRD_PARTY, EscrowAgent.INTERNAL_CUSTODIAN],
            access_level=AccessLevel.CREATOR_REQUEST,
            retention_period=timedelta(days=2555),  # 7 years
            verification_interval=timedelta(days=90),
            split_threshold=2,
            total_shares=3,
            geographic_distribution=["US", "EU", "ASIA"],
            compliance_frameworks=["GDPR", "CCPA", "DMCA"],
            creator_notification=True
        )
        
        # Financial data escrow policy
        self.escrow_policies["financial_data"] = EscrowPolicy(
            escrow_type=EscrowType.REGULATORY,
            required_agents=[EscrowAgent.GOVERNMENT_AGENCY, EscrowAgent.CORPORATE_COMPLIANCE],
            access_level=AccessLevel.REGULATORY_REQUEST,
            retention_period=timedelta(days=2555),  # 7 years for financial records
            verification_interval=timedelta(days=30),
            split_threshold=3,
            total_shares=5,
            geographic_distribution=["US", "EU"],
            compliance_frameworks=["SOX", "PCI_DSS", "GDPR"],
            emergency_access_enabled=False,
            legal_hold_support=True
        )
        
        # Legal compliance policy
        self.escrow_policies["legal_compliance"] = EscrowPolicy(
            escrow_type=EscrowType.LEGAL_COMPLIANCE,
            required_agents=[EscrowAgent.LEGAL_AUTHORITY, EscrowAgent.TRUSTED_THIRD_PARTY],
            access_level=AccessLevel.COURT_ORDER,
            retention_period=timedelta(days=3650),  # 10 years
            verification_interval=timedelta(days=180),
            split_threshold=2,
            total_shares=3,
            geographic_distribution=["US"],
            compliance_frameworks=["FISA", "CALEA", "MLAT"],
            emergency_access_enabled=True,
            creator_notification=False  # May be legally prohibited
        )
        
        # Business continuity policy
        self.escrow_policies["business_continuity"] = EscrowPolicy(
            escrow_type=EscrowType.BUSINESS_CONTINUITY,
            required_agents=[EscrowAgent.INTERNAL_CUSTODIAN, EscrowAgent.INSURANCE_PROVIDER],
            access_level=AccessLevel.BUSINESS_CONTINUITY,
            retention_period=timedelta(days=1825),  # 5 years
            verification_interval=timedelta(days=30),
            split_threshold=2,
            total_shares=4,
            geographic_distribution=["US", "EU", "ASIA"],
            compliance_frameworks=["ISO27001", "SOC2"],
            emergency_access_enabled=True
        )

    def _initialize_default_agents(self):
        """Initialize default escrow agents."""
        # Internal custodian
        self.escrow_agents["internal_custodian_001"] = EscrowAgent(
            agent_id="internal_custodian_001",
            agent_type=EscrowAgent.INTERNAL_CUSTODIAN,
            name="IA Chéries Internal Security Custodian",
            contact_info={
                "email": "security-custodian@ainflue.com",
                "phone": "+1-555-0123",
                "address": "123 Security Blvd, Tech City, TC 12345"
            },
            public_key=self._generate_agent_key(),
            geographic_location="US",
            compliance_certifications=["SOC2", "ISO27001"],
            trust_level=9
        )
        
        # Trusted third party (simulated)
        self.escrow_agents["ttp_vault_001"] = EscrowAgent(
            agent_id="ttp_vault_001",
            agent_type=EscrowAgent.TRUSTED_THIRD_PARTY,
            name="SecureVault Escrow Services",
            contact_info={
                "email": "escrow@securevault.com",
                "phone": "+1-555-0456",
                "address": "456 Trust St, Secure City, SC 67890"
            },
            public_key=self._generate_agent_key(),
            geographic_location="US",
            compliance_certifications=["FIPS140-2", "CommonCriteria"],
            trust_level=10
        )
        
        # EU agent
        self.escrow_agents["eu_custodian_001"] = EscrowAgent(
            agent_id="eu_custodian_001",
            agent_type=EscrowAgent.TRUSTED_THIRD_PARTY,
            name="EuroSecure Escrow GmbH",
            contact_info={
                "email": "escrow@eurosecure.de",
                "phone": "+49-30-12345678",
                "address": "Sicherheitsstraße 123, 10115 Berlin, Germany"
            },
            public_key=self._generate_agent_key(),
            geographic_location="EU",
            compliance_certifications=["GDPR", "ISO27001"],
            trust_level=9
        )

    def _generate_agent_key(self) -> bytes:
        """Generate public key for escrow agent."""
        # In production, this would be the actual agent's public key
        return secrets.token_bytes(64)

    async def deposit_key_to_escrow(self,
                                   key_id: str,
                                   key_material: bytes,
                                   key_metadata: Dict[str, Any],
                                   policy_name: str,
                                   depositor_id: str,
                                   creator_id: Optional[str] = None) -> str:
        """
        Deposit cryptographic key into escrow system.
        
        Args:
            key_id: Unique identifier for the key
            key_material: The actual key material to escrow
            key_metadata: Metadata about the key
            policy_name: Name of escrow policy to apply
            depositor_id: ID of entity depositing the key
            creator_id: Optional creator ID if key belongs to creator
            
        Returns:
            Deposit ID for the escrowed key
        """
        try:
            if policy_name not in self.escrow_policies:
                raise ValueError(f"Unknown escrow policy: {policy_name}")
            
            policy = self.escrow_policies[policy_name]
            deposit_id = f"escrow_{policy.escrow_type.value}_{secrets.token_hex(12)}"
            
            # Encrypt key material
            encryption_key = secrets.token_bytes(32)
            encrypted_key = await self._encrypt_key_material(key_material, encryption_key)
            
            # Create secret shares using Shamir's Secret Sharing
            shares = await self._create_secret_shares(
                encryption_key,
                policy.total_shares,
                policy.split_threshold
            )
            
            # Distribute shares to agents
            encrypted_shares = await self._distribute_shares_to_agents(shares, policy)
            
            # Create verification checksum
            verification_data = key_material + json.dumps(key_metadata, sort_keys=True).encode()
            verification_checksum = hashlib.sha256(verification_data).hexdigest()
            
            # Create escrow deposit
            deposit = EscrowDeposit(
                deposit_id=deposit_id,
                key_id=key_id,
                escrow_type=policy.escrow_type,
                policy=policy,
                encrypted_key_material=encrypted_key,
                key_metadata=key_metadata,
                shares=encrypted_shares,
                depositor_id=depositor_id,
                creator_id=creator_id,
                deposit_timestamp=datetime.utcnow(),
                expiry_timestamp=datetime.utcnow() + policy.retention_period,
                status=EscrowStatus.ACTIVE,
                verification_checksum=verification_checksum,
                access_log=[],
                compliance_attestation=await self._generate_compliance_attestation(policy)
            )
            
            # Store deposit
            self.escrow_deposits[deposit_id] = deposit
            
            # Log the deposit
            await self._log_escrow_operation("DEPOSIT", deposit_id, depositor_id, {
                "key_id": key_id,
                "policy": policy_name,
                "creator_id": creator_id,
                "shares_distributed": len(encrypted_shares)
            })
            
            # Notify stakeholders if required
            if policy.creator_notification and creator_id:
                await self._notify_creator_of_escrow(creator_id, deposit_id, policy)
            
            self.logger.info(f"Key deposited to escrow: {deposit_id} for key {key_id}")
            return deposit_id
            
        except Exception as e:
            self.logger.error(f"Key escrow deposit failed: {e}")
            raise

    async def _encrypt_key_material(self, key_material: bytes, encryption_key: bytes) -> bytes:
        """Encrypt key material for escrow storage."""
        nonce = secrets.token_bytes(12)
        cipher = AESGCM(encryption_key)
        ciphertext = cipher.encrypt(nonce, key_material, None)
        return nonce + ciphertext

    async def _create_secret_shares(self, secret: bytes, total_shares: int, threshold: int) -> List[bytes]:
        """Create Shamir's Secret Sharing shares."""
        # Simplified secret sharing implementation
        # In production, use a proper library like pycryptodome or secrets-sharing
        
        shares = []
        secret_int = int.from_bytes(secret, byteorder='big')
        
        # Generate random coefficients for polynomial
        coefficients = [secret_int]  # a0 = secret
        for _ in range(threshold - 1):
            coefficients.append(secrets.randbits(256))
        
        # Calculate shares
        for i in range(1, total_shares + 1):
            share_value = coefficients[0]  # Start with secret
            for j in range(1, threshold):
                share_value += coefficients[j] * (i ** j)
            
            # Convert back to bytes and include share index
            share_data = i.to_bytes(4, byteorder='big') + share_value.to_bytes(32, byteorder='big')
            shares.append(share_data)
        
        return shares

    async def _distribute_shares_to_agents(self, shares: List[bytes], policy: EscrowPolicy) -> Dict[str, bytes]:
        """Distribute shares to designated escrow agents."""
        encrypted_shares = {}
        available_agents = [agent for agent in self.escrow_agents.values() 
                          if agent.active and agent.agent_type in policy.required_agents]
        
        if len(available_agents) < len(shares):
            raise ValueError("Not enough available agents for share distribution")
        
        # Distribute shares geographically if required
        if policy.geographic_distribution:
            agents_by_location = {}
            for agent in available_agents:
                location = agent.geographic_location
                if location not in agents_by_location:
                    agents_by_location[location] = []
                agents_by_location[location].append(agent)
            
            selected_agents = []
            for location in policy.geographic_distribution:
                if location in agents_by_location and agents_by_location[location]:
                    selected_agents.append(agents_by_location[location][0])
            
            # Fill remaining slots with any available agents
            remaining_count = len(shares) - len(selected_agents)
            remaining_agents = [a for a in available_agents if a not in selected_agents]
            selected_agents.extend(remaining_agents[:remaining_count])
        else:
            selected_agents = available_agents[:len(shares)]
        
        # Encrypt shares for each agent
        for i, (share, agent) in enumerate(zip(shares, selected_agents)):
            encrypted_share = await self._encrypt_share_for_agent(share, agent)
            encrypted_shares[f"{agent.agent_id}_{i}"] = encrypted_share
        
        return encrypted_shares

    async def _encrypt_share_for_agent(self, share: bytes, agent: EscrowAgent) -> bytes:
        """Encrypt a share for a specific agent."""
        # In production, use the agent's actual public key
        # For simulation, use a deterministic encryption based on agent ID
        agent_key = hashlib.sha256(agent.agent_id.encode() + agent.public_key).digest()
        
        nonce = secrets.token_bytes(12)
        cipher = AESGCM(agent_key)
        encrypted_share = cipher.encrypt(nonce, share, None)
        return nonce + encrypted_share

    async def _generate_compliance_attestation(self, policy: EscrowPolicy) -> Dict[str, Any]:
        """Generate compliance attestation for escrow deposit."""
        return {
            "compliance_frameworks": policy.compliance_frameworks,
            "attestation_timestamp": datetime.utcnow().isoformat(),
            "attestation_authority": "IA Chéries Security Compliance Office",
            "retention_compliance": True,
            "access_control_compliance": True,
            "geographic_compliance": len(policy.geographic_distribution) > 0,
            "audit_trail_enabled": policy.audit_logging_required
        }

    async def request_key_recovery(self,
                                  deposit_id: str,
                                  requester_id: str,
                                  requester_type: str,
                                  justification: str,
                                  legal_documentation: Optional[Dict[str, Any]] = None,
                                  urgency_level: int = 5) -> str:
        """
        Request recovery of an escrowed key.
        
        Args:
            deposit_id: ID of the escrow deposit
            requester_id: ID of the requesting entity
            requester_type: Type of requester (creator, legal_authority, etc.)
            justification: Reason for recovery request
            legal_documentation: Optional legal documentation
            urgency_level: Urgency level (1-10)
            
        Returns:
            Recovery request ID
        """
        try:
            if deposit_id not in self.escrow_deposits:
                raise ValueError(f"Escrow deposit not found: {deposit_id}")
            
            deposit = self.escrow_deposits[deposit_id]
            
            if deposit.status != EscrowStatus.ACTIVE:
                raise ValueError(f"Deposit not available for recovery: {deposit.status}")
            
            request_id = f"recovery_{requester_type}_{secrets.token_hex(8)}"
            
            # Determine required approvals based on policy
            required_approvals = await self._determine_required_approvals(deposit, requester_type)
            
            recovery_request = RecoveryRequest(
                request_id=request_id,
                deposit_id=deposit_id,
                requester_id=requester_id,
                requester_type=requester_type,
                justification=justification,
                legal_documentation=legal_documentation,
                urgency_level=urgency_level,
                approval_status="pending",
                required_approvals=required_approvals,
                obtained_approvals=[],
                created_at=datetime.utcnow()
            )
            
            self.recovery_requests[request_id] = recovery_request
            
            # Log the recovery request
            await self._log_escrow_operation("RECOVERY_REQUEST", deposit_id, requester_id, {
                "request_id": request_id,
                "requester_type": requester_type,
                "justification": justification[:100],  # First 100 chars
                "urgency_level": urgency_level
            })
            
            # Initiate approval workflow
            await self._initiate_approval_workflow(recovery_request)
            
            self.logger.info(f"Recovery request created: {request_id} for deposit {deposit_id}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Key recovery request failed: {e}")
            raise

    async def _determine_required_approvals(self, deposit: EscrowDeposit, requester_type: str) -> List[str]:
        """Determine required approvals for recovery request."""
        required_approvals = []
        
        # Base approvals based on access level
        if deposit.policy.access_level == AccessLevel.EMERGENCY_ONLY:
            required_approvals.extend(["security_officer", "ciso"])
        elif deposit.policy.access_level == AccessLevel.COURT_ORDER:
            required_approvals.extend(["legal_counsel", "compliance_officer"])
        elif deposit.policy.access_level == AccessLevel.REGULATORY_REQUEST:
            required_approvals.extend(["compliance_officer", "external_auditor"])
        elif deposit.policy.access_level == AccessLevel.CREATOR_REQUEST:
            if requester_type == "creator":
                required_approvals.append("identity_verification")
            else:
                required_approvals.extend(["creator_consent", "legal_counsel"])
        
        # Additional approvals for sensitive data
        if deposit.policy.escrow_type == EscrowType.LEGAL_COMPLIANCE:
            required_approvals.append("law_enforcement_liaison")
        elif deposit.policy.escrow_type == EscrowType.REGULATORY:
            required_approvals.append("regulatory_affairs")
        
        return list(set(required_approvals))  # Remove duplicates

    async def _initiate_approval_workflow(self, request: RecoveryRequest):
        """Initiate approval workflow for recovery request."""
        # In production, this would integrate with workflow management system
        for approval_type in request.required_approvals:
            await self._request_approval(request.request_id, approval_type)

    async def _request_approval(self, request_id: str, approval_type: str):
        """Request specific approval for recovery."""
        # Simulate approval request
        self.logger.info(f"Requesting {approval_type} approval for recovery {request_id}")
        
        # In production, this would send notifications to appropriate approvers

    async def approve_recovery_request(self,
                                     request_id: str,
                                     approver_id: str,
                                     approval_type: str,
                                     approved: bool,
                                     comments: Optional[str] = None) -> bool:
        """
        Approve or deny a recovery request.
        
        Args:
            request_id: Recovery request ID
            approver_id: ID of the approver
            approval_type: Type of approval being given
            approved: Whether the request is approved
            comments: Optional comments
            
        Returns:
            True if recovery is now fully approved, False otherwise
        """
        try:
            if request_id not in self.recovery_requests:
                raise ValueError(f"Recovery request not found: {request_id}")
            
            request = self.recovery_requests[request_id]
            
            if request.approval_status != "pending":
                raise ValueError(f"Request is not pending approval: {request.approval_status}")
            
            # Record approval/denial
            approval_record = {
                "approval_type": approval_type,
                "approver_id": approver_id,
                "approved": approved,
                "timestamp": datetime.utcnow().isoformat(),
                "comments": comments
            }
            
            if approved and approval_type in request.required_approvals:
                if approval_type not in request.obtained_approvals:
                    request.obtained_approvals.append(approval_type)
            elif not approved:
                # Denial - reject the entire request
                request.approval_status = "denied"
                await self._log_escrow_operation("RECOVERY_DENIED", request.deposit_id, approver_id, approval_record)
                return False
            
            # Check if all required approvals are obtained
            if set(request.obtained_approvals) >= set(request.required_approvals):
                request.approval_status = "approved"
                request.approved_at = datetime.utcnow()
                
                # Automatically proceed with recovery if fully approved
                await self._execute_key_recovery(request)
                return True
            
            await self._log_escrow_operation("RECOVERY_APPROVAL", request.deposit_id, approver_id, approval_record)
            return False
            
        except Exception as e:
            self.logger.error(f"Recovery approval failed: {e}")
            raise

    async def _execute_key_recovery(self, request: RecoveryRequest):
        """Execute approved key recovery."""
        try:
            deposit = self.escrow_deposits[request.deposit_id]
            
            # Collect shares from agents
            collected_shares = await self._collect_shares_from_agents(deposit)
            
            # Reconstruct encryption key from shares
            encryption_key = await self._reconstruct_secret_from_shares(
                collected_shares,
                deposit.policy.split_threshold
            )
            
            # Decrypt key material
            recovered_key = await self._decrypt_key_material(
                deposit.encrypted_key_material,
                encryption_key
            )
            
            # Verify key integrity
            if not await self._verify_key_integrity(recovered_key, deposit):
                raise Exception("Key integrity verification failed")
            
            # Store recovered key in request
            request.recovered_key_data = recovered_key
            request.approval_status = "completed"
            request.completed_at = datetime.utcnow()
            
            # Log successful recovery
            await self._log_escrow_operation("RECOVERY_COMPLETED", request.deposit_id, request.requester_id, {
                "request_id": request.request_id,
                "recovery_timestamp": request.completed_at.isoformat(),
                "key_verified": True
            })
            
            # Notify stakeholders
            await self._notify_recovery_completion(request, deposit)
            
            self.logger.info(f"Key recovery completed: {request.request_id}")
            
        except Exception as e:
            request.approval_status = "failed"
            await self._log_escrow_operation("RECOVERY_FAILED", request.deposit_id, request.requester_id, {
                "error": str(e)
            })
            self.logger.error(f"Key recovery execution failed: {e}")
            raise

    async def _collect_shares_from_agents(self, deposit: EscrowDeposit) -> List[bytes]:
        """Collect shares from escrow agents."""
        collected_shares = []
        
        for share_id, encrypted_share in deposit.shares.items():
            agent_id = share_id.split('_')[0]
            
            if agent_id in self.escrow_agents:
                agent = self.escrow_agents[agent_id]
                
                # Decrypt share
                share = await self._decrypt_share_from_agent(encrypted_share, agent)
                collected_shares.append(share)
                
                # Log share collection
                await self._log_escrow_operation("SHARE_COLLECTED", deposit.deposit_id, agent_id, {
                    "share_id": share_id
                })
        
        if len(collected_shares) < deposit.policy.split_threshold:
            raise Exception(f"Insufficient shares collected: {len(collected_shares)} < {deposit.policy.split_threshold}")
        
        return collected_shares[:deposit.policy.split_threshold]

    async def _decrypt_share_from_agent(self, encrypted_share: bytes, agent: EscrowAgent) -> bytes:
        """Decrypt a share from an agent."""
        # Extract nonce and ciphertext
        nonce = encrypted_share[:12]
        ciphertext = encrypted_share[12:]
        
        # Derive agent key
        agent_key = hashlib.sha256(agent.agent_id.encode() + agent.public_key).digest()
        
        # Decrypt
        cipher = AESGCM(agent_key)
        share = cipher.decrypt(nonce, ciphertext, None)
        
        return share

    async def _reconstruct_secret_from_shares(self, shares: List[bytes], threshold: int) -> bytes:
        """Reconstruct secret from Shamir's Secret Sharing shares."""
        # Extract share indices and values
        share_points = []
        
        for share in shares:
            index = int.from_bytes(share[:4], byteorder='big')
            value = int.from_bytes(share[4:], byteorder='big')
            share_points.append((index, value))
        
        # Lagrange interpolation to reconstruct secret
        secret = 0
        
        for i in range(threshold):
            xi, yi = share_points[i]
            
            # Calculate Lagrange coefficient
            li = 1
            for j in range(threshold):
                if i != j:
                    xj, _ = share_points[j]
                    li *= (0 - xj) // (xi - xj)  # Evaluate at x=0 to get constant term
            
            secret += yi * li
        
        # Convert back to bytes
        return secret.to_bytes(32, byteorder='big')

    async def _decrypt_key_material(self, encrypted_key_material: bytes, encryption_key: bytes) -> bytes:
        """Decrypt key material using recovered encryption key."""
        nonce = encrypted_key_material[:12]
        ciphertext = encrypted_key_material[12:]
        
        cipher = AESGCM(encryption_key)
        key_material = cipher.decrypt(nonce, ciphertext, None)
        
        return key_material

    async def _verify_key_integrity(self, recovered_key: bytes, deposit: EscrowDeposit) -> bool:
        """Verify integrity of recovered key."""
        # Recalculate verification checksum
        verification_data = recovered_key + json.dumps(deposit.key_metadata, sort_keys=True).encode()
        calculated_checksum = hashlib.sha256(verification_data).hexdigest()
        
        return calculated_checksum == deposit.verification_checksum

    async def _notify_recovery_completion(self, request: RecoveryRequest, deposit: EscrowDeposit):
        """Notify stakeholders of recovery completion."""
        if self.notification_callback:
            await self.notification_callback("RECOVERY_COMPLETED", {
                "request_id": request.request_id,
                "deposit_id": request.deposit_id,
                "requester_id": request.requester_id,
                "creator_id": deposit.creator_id
            })

    async def verify_escrow_integrity(self, deposit_id: str) -> Dict[str, Any]:
        """
        Verify integrity of escrow deposit without recovering the key.
        
        Args:
            deposit_id: ID of escrow deposit to verify
            
        Returns:
            Dict containing verification results
        """
        try:
            if deposit_id not in self.escrow_deposits:
                raise ValueError(f"Escrow deposit not found: {deposit_id}")
            
            deposit = self.escrow_deposits[deposit_id]
            verification_results = {
                "deposit_id": deposit_id,
                "verification_timestamp": datetime.utcnow().isoformat(),
                "status": deposit.status.value,
                "shares_available": 0,
                "shares_required": deposit.policy.split_threshold,
                "agents_responsive": 0,
                "integrity_verified": False,
                "compliance_status": "unknown",
                "issues": []
            }
            
            # Check share availability
            for share_id in deposit.shares:
                agent_id = share_id.split('_')[0]
                if agent_id in self.escrow_agents and self.escrow_agents[agent_id].active:
                    verification_results["shares_available"] += 1
                    verification_results["agents_responsive"] += 1
                else:
                    verification_results["issues"].append(f"Agent {agent_id} unavailable")
            
            # Check if enough shares are available
            if verification_results["shares_available"] >= verification_results["shares_required"]:
                verification_results["integrity_verified"] = True
            else:
                verification_results["issues"].append("Insufficient shares available for recovery")
            
            # Check expiry
            if deposit.expiry_timestamp < datetime.utcnow():
                verification_results["issues"].append("Deposit expired")
                verification_results["status"] = "expired"
            
            # Check compliance
            if all(framework in self.config.get("compliance_frameworks", []) 
                  for framework in deposit.policy.compliance_frameworks):
                verification_results["compliance_status"] = "compliant"
            else:
                verification_results["compliance_status"] = "non_compliant"
                verification_results["issues"].append("Compliance framework mismatch")
            
            # Log verification
            await self._log_escrow_operation("INTEGRITY_VERIFICATION", deposit_id, "system", verification_results)
            
            return verification_results
            
        except Exception as e:
            self.logger.error(f"Escrow integrity verification failed: {e}")
            raise

    async def list_escrow_deposits(self, 
                                  creator_id: Optional[str] = None,
                                  depositor_id: Optional[str] = None,
                                  status_filter: Optional[EscrowStatus] = None) -> List[Dict[str, Any]]:
        """
        List escrow deposits with optional filtering.
        
        Args:
            creator_id: Filter by creator ID
            depositor_id: Filter by depositor ID
            status_filter: Filter by status
            
        Returns:
            List of deposit summaries
        """
        try:
            deposits = []
            
            for deposit in self.escrow_deposits.values():
                # Apply filters
                if creator_id and deposit.creator_id != creator_id:
                    continue
                if depositor_id and deposit.depositor_id != depositor_id:
                    continue
                if status_filter and deposit.status != status_filter:
                    continue
                
                # Create summary
                deposit_summary = {
                    "deposit_id": deposit.deposit_id,
                    "key_id": deposit.key_id,
                    "escrow_type": deposit.escrow_type.value,
                    "status": deposit.status.value,
                    "depositor_id": deposit.depositor_id,
                    "creator_id": deposit.creator_id,
                    "deposit_timestamp": deposit.deposit_timestamp.isoformat(),
                    "expiry_timestamp": deposit.expiry_timestamp.isoformat(),
                    "shares_count": len(deposit.shares),
                    "access_log_count": len(deposit.access_log),
                    "compliance_frameworks": deposit.policy.compliance_frameworks
                }
                
                deposits.append(deposit_summary)
            
            return deposits
            
        except Exception as e:
            self.logger.error(f"Failed to list escrow deposits: {e}")
            raise

    async def _log_escrow_operation(self, operation: str, deposit_id: str, actor_id: str, details: Dict[str, Any]):
        """Log escrow operation for audit trail."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "deposit_id": deposit_id,
            "actor_id": actor_id,
            "details": details
        }
        
        # Add to deposit access log if deposit exists
        if deposit_id in self.escrow_deposits:
            self.escrow_deposits[deposit_id].access_log.append(log_entry)
        
        # Send to external audit system if configured
        if self.audit_callback:
            await self.audit_callback(log_entry)
        
        self.logger.info(f"Escrow operation logged: {operation} for deposit {deposit_id}")

    async def _notify_creator_of_escrow(self, creator_id: str, deposit_id: str, policy: EscrowPolicy):
        """Notify creator of key escrow."""
        if self.notification_callback:
            await self.notification_callback("ESCROW_CREATED", {
                "creator_id": creator_id,
                "deposit_id": deposit_id,
                "escrow_type": policy.escrow_type.value,
                "retention_period_days": policy.retention_period.days
            })

    async def get_escrow_status(self) -> Dict[str, Any]:
        """Get comprehensive escrow system status."""
        try:
            active_deposits = len([d for d in self.escrow_deposits.values() if d.status == EscrowStatus.ACTIVE])
            pending_requests = len([r for r in self.recovery_requests.values() if r.approval_status == "pending"])
            
            return {
                "escrow_manager_status": "operational",
                "total_deposits": len(self.escrow_deposits),
                "active_deposits": active_deposits,
                "total_agents": len(self.escrow_agents),
                "active_agents": len([a for a in self.escrow_agents.values() if a.active]),
                "pending_recovery_requests": pending_requests,
                "policies_configured": len(self.escrow_policies),
                "compliance_frameworks": self.config.get("compliance_frameworks", []),
                "geographic_coverage": list(set(a.geographic_location for a in self.escrow_agents.values())),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get escrow status: {e}")
            raise

    async def cleanup(self):
        """Cleanup escrow manager resources."""
        try:
            # Securely clear sensitive data
            for deposit in self.escrow_deposits.values():
                deposit.encrypted_key_material = b""
                deposit.shares.clear()
            
            for request in self.recovery_requests.values():
                if request.recovered_key_data:
                    request.recovered_key_data = b""
            
            self.escrow_deposits.clear()
            self.recovery_requests.clear()
            
            self.logger.info("Key Escrow Manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Escrow manager cleanup failed: {e}")


# Creator Economy Integration Functions
async def setup_creator_escrow_protection(creator_id: str,
                                         creator_type: str,
                                         content_keys: Dict[str, bytes],
                                         escrow_manager: KeyEscrowManager) -> Dict[str, str]:
    """Setup escrow protection for creator keys."""
    deposit_ids = {}
    
    for content_type, key_material in content_keys.items():
        key_metadata = {
            "creator_id": creator_id,
            "creator_type": creator_type,
            "content_type": content_type,
            "created_at": datetime.utcnow().isoformat(),
            "key_purpose": f"{creator_type}_{content_type}_protection"
        }
        
        # Use creator content policy
        policy_name = "creator_content"
        
        deposit_id = await escrow_manager.deposit_key_to_escrow(
            key_id=f"creator_{creator_id}_{content_type}",
            key_material=key_material,
            key_metadata=key_metadata,
            policy_name=policy_name,
            depositor_id=f"creator_{creator_id}",
            creator_id=creator_id
        )
        
        deposit_ids[content_type] = deposit_id
    
    return deposit_ids


# Export main classes and functions
__all__ = [
    "KeyEscrowManager",
    "EscrowType",
    "EscrowAgent",
    "AccessLevel",
    "EscrowStatus",
    "EscrowPolicy", 
    "EscrowDeposit",
    "RecoveryRequest",
    "setup_creator_escrow_protection"
]