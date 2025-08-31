"""📋 Licensing Model - IA Influencer Agent Platform Enterprise
===========================================================
Module: backend/data_management/models/licensing_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Licensing Model - Production-Ready
Responsibility: Content licensing and rights management
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Content Creation → Rights Definition → License Generation → 
Contract Management → Revenue Distribution → Compliance Monitoring
"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

class LicenseType(Enum):
    """Types de licences disponibles"""    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    CUSTOM = "custom"

class LicenseStatus(Enum):
    """Statuts des licences"""    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    RENEWED = "renewed"
    REVOKED = "revoked"

class PaymentStructure(Enum):
    """Structures de paiement"""    ONE_TIME = "one_time"
    ROYALTY = "royalty"
    SUBSCRIPTION = "subscription"
    PER_USE = "per_use"
    REVENUE_SHARE = "revenue_share"

@dataclass
class LicenseTerms:
    """Termes et conditions de la licence"""    usage_rights: List[str] = field(default_factory=list)
    geographical_restrictions: List[str] = field(default_factory=list)
    duration_months: Optional[int] = None
    max_uses: Optional[int] = None
    attribution_required: bool = True
    modification_allowed: bool = False
    commercial_use: bool = False
    resale_allowed: bool = False
    exclusive_territory: List[str] = field(default_factory=list)

@dataclass
class RoyaltyStructure:
    """Structure des royalties"""    percentage: float = 0.0
    minimum_amount: float = 0.0
    payment_frequency: str = "monthly"
    payment_threshold: float = 50.0
    currency: str = "EUR"
    splits: Dict[str, float] = field(default_factory=dict)

@dataclass
class LicensingModel:
    """    🏛️ Modèle de licensing pour la gestion des droits de contenu
    
    Architecture complète pour:
    - Gestion des licences de contenu
    - Contrats et accords
    - Structures de paiement et royalties
    - Conformité légale
    - Suivi des performances
    """    
    # Identification
    license_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    creator_id: str = ""
    client_id: str = ""
    
    # Informations de base
    title: str = ""
    description: str = ""
    license_type: LicenseType = LicenseType.NON_EXCLUSIVE
    status: LicenseStatus = LicenseStatus.DRAFT
    
    # Termes de la licence
    terms: LicenseTerms = field(default_factory=LicenseTerms)
    
    # Structure financière
    payment_structure: PaymentStructure = PaymentStructure.ONE_TIME
    price: float = 0.0
    currency: str = "EUR"
    royalty_structure: Optional[RoyaltyStructure] = None
    
    # Dates importantes
    created_at: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    
    # Documents légaux
    contract_url: Optional[str] = None
    signature_status: Dict[str, bool] = field(default_factory=dict)
    legal_documents: List[str] = field(default_factory=list)
    
    # Métriques et performance
    usage_count: int = 0
    revenue_generated: float = 0.0
    compliance_score: float = 100.0
    
    # Métadonnées
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialisation avec validations"""        if not self.start_date:
            self.start_date = datetime.now()
        
        if not self.end_date and self.terms.duration_months:
            self.end_date = self.start_date + timedelta(days=self.terms.duration_months * 30)
    
    def is_active(self) -> bool:
        """Vérifie si la licence est active"""        now = datetime.now()
        return (
            self.status == LicenseStatus.ACTIVE and
            (not self.start_date or self.start_date <= now) and
            (not self.end_date or self.end_date > now)
        )
    
    def is_expired(self) -> bool:
        """Vérifie si la licence a expiré"""        if not self.end_date:
            return False
        return datetime.now() > self.end_date
    
    def calculate_royalty(self, revenue: float) -> float:
        """Calcule les royalties basées sur le revenu"""        if not self.royalty_structure:
            return 0.0
        
        royalty = revenue * (self.royalty_structure.percentage / 100)
        return max(royalty, self.royalty_structure.minimum_amount)
    
    def can_be_used(self, use_case: str) -> bool:
        """Vérifie si la licence permet un usage spécifique"""        if not self.is_active():
            return False
        
        if self.terms.max_uses and self.usage_count >= self.terms.max_uses:
            return False
        
        return use_case in self.terms.usage_rights
    
    def record_usage(self, revenue: float = 0.0):
        """Enregistre un usage de la licence"""        self.usage_count += 1
        if revenue > 0:
            self.revenue_generated += revenue
            
            # Mettre à jour les métriques de compliance
            if self.usage_count > (self.terms.max_uses or float('inf')):
                self.compliance_score *= 0.9  # Pénalité pour dépassement
    
    def renew_license(self, duration_months: int = None):
        """Renouvelle la licence"""        if duration_months:
            self.terms.duration_months = duration_months
        
        self.start_date = datetime.now()
        if self.terms.duration_months:
            self.end_date = self.start_date + timedelta(days=self.terms.duration_months * 30)
        
        self.status = LicenseStatus.ACTIVE
        self.renewal_date = datetime.now()
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Génère un rapport de conformité"""        return {
            "license_id": self.license_id,
            "status": self.status.value,
            "compliance_score": self.compliance_score,
            "usage_count": self.usage_count,
            "max_uses": self.terms.max_uses,
            "revenue_generated": self.revenue_generated,
            "is_active": self.is_active(),
            "is_expired": self.is_expired(),
            "days_remaining": (self.end_date - datetime.now()).days if self.end_date else None,
            "signature_status": self.signature_status,
            "last_updated": datetime.now().isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire"""        return {
            "license_id": self.license_id,
            "content_id": self.content_id,
            "creator_id": self.creator_id,
            "client_id": self.client_id,
            "title": self.title,
            "description": self.description,
            "license_type": self.license_type.value,
            "status": self.status.value,
            "terms": self.terms.__dict__,
            "payment_structure": self.payment_structure.value,
            "price": self.price,
            "currency": self.currency,
            "royalty_structure": self.royalty_structure.__dict__ if self.royalty_structure else None,
            "created_at": self.created_at.isoformat(),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "renewal_date": self.renewal_date.isoformat() if self.renewal_date else None,
            "contract_url": self.contract_url,
            "signature_status": self.signature_status,
            "legal_documents": self.legal_documents,
            "usage_count": self.usage_count,
            "revenue_generated": self.revenue_generated,
            "compliance_score": self.compliance_score,
            "tags": self.tags,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LicensingModel':
        """Crée une instance depuis un dictionnaire"""        # Conversion des enums
        if 'license_type' in data:
            data['license_type'] = LicenseType(data['license_type'])
        if 'status' in data:
            data['status'] = LicenseStatus(data['status'])
        if 'payment_structure' in data:
            data['payment_structure'] = PaymentStructure(data['payment_structure'])
        
        # Conversion des dates
        for date_field in ['created_at', 'start_date', 'end_date', 'renewal_date']:
            if date_field in data and data[date_field]:
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        # Reconstruction des objets complexes
        if 'terms' in data and isinstance(data['terms'], dict):
            data['terms'] = LicenseTerms(**data['terms'])
        
        if 'royalty_structure' in data and data['royalty_structure']:
            data['royalty_structure'] = RoyaltyStructure(**data['royalty_structure'])
        
        return cls(**data)

# Alias pour compatibilité
License = LicensingModel
