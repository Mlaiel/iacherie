"""🌐 Platform & Audit Models - IA Influencer Agent Platform Enterprise
====================================================================
Module: backend/data_management/models/platform_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
====================================================================

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
class PlatformModel:
    platform_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform_name: str = ""
    platform_type: str = "streaming"
    api_endpoint: str = ""
    supports_fingerprinting: bool = False
    supports_takedown: bool = False
    rate_limit: int = 1000
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "platform_type": self.platform_type,
            "api_endpoint": self.api_endpoint,
            "supports_fingerprinting": self.supports_fingerprinting,
            "supports_takedown": self.supports_takedown,
            "rate_limit": self.rate_limit,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class IntegrationModel:
    integration_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    platform_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "integration_id": self.integration_id,
            "creator_id": self.creator_id,
            "platform_id": self.platform_id,
            "access_token": "***hidden***",
            "refresh_token": "***hidden***",
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class APIModel:
    api_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    api_key: str = ""
    rate_limit: int = 1000
    calls_made: int = 0
    last_call_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_id": self.api_id,
            "creator_id": self.creator_id,
            "api_key": "***hidden***",
            "rate_limit": self.rate_limit,
            "calls_made": self.calls_made,
            "last_call_at": self.last_call_at.isoformat() if self.last_call_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
