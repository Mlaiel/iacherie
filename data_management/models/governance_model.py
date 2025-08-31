"""🏛️ Governance Model - IA Influencer Agent Platform Enterprise
==============================================================
Module: backend/data_management/models/governance_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid

@dataclass
class GovernanceModel:
    governance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    policy_type: str = "data_retention"
    policy_name: str = ""
    rules: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "governance_id": self.governance_id,
            "tenant_id": self.tenant_id,
            "policy_type": self.policy_type,
            "policy_name": self.policy_name,
            "rules": self.rules,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class ComplianceModel:
    compliance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    regulation: str = "GDPR"
    status: str = "compliant"
    last_audit_date: Optional[datetime] = None
    next_audit_date: Optional[datetime] = None
    findings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "compliance_id": self.compliance_id,
            "tenant_id": self.tenant_id,
            "regulation": self.regulation,
            "status": self.status,
            "last_audit_date": self.last_audit_date.isoformat() if self.last_audit_date else None,
            "next_audit_date": self.next_audit_date.isoformat() if self.next_audit_date else None,
            "findings": self.findings,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class PolicyModel:
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    policy_type: str = ""
    policy_content: str = ""
    version: str = "1.0"
    effective_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "tenant_id": self.tenant_id,
            "policy_type": self.policy_type,
            "policy_content": self.policy_content,
            "version": self.version,
            "effective_date": self.effective_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
