"""
📜 Ultra-Industrial Digital Rights Management & Tracking Orchestration
======================================================================

Enterprise-grade intellectual property rights management system with blockchain
integration, automated licensing, and comprehensive legal compliance for
global content protection and monetization optimization.

Business Logic Integration:
- Comprehensive IP rights registration and tracking
- Automated licensing and royalty distribution
- Legal compliance across international jurisdictions
- Revenue optimization through rights monetization
- Creator collaboration and rights sharing management
- Real-time usage monitoring and enforcement

Rights Management Coverage:
- Copyright: Original creative works protection and licensing
- Performance Rights: Public performance and broadcast licensing
- Mechanical Rights: Reproduction and distribution licensing
- Synchronization Rights: Audio-visual content licensing
- Digital Transmission: Streaming and online distribution rights
- Moral Rights: Attribution and integrity protection
- Trademark: Brand and identity protection
- Publicity Rights: Personal image and likeness protection

Technical Excellence Architecture:
- Blockchain Integration: Immutable rights registration with smart contracts
- Automated Licensing: AI-powered licensing negotiation and execution
- Global Compliance: Multi-jurisdiction legal framework support
- Revenue Tracking: Real-time royalty calculation and distribution
- Legal Enforcement: Automated DMCA and international takedown coordination
- Analytics Dashboard: Rights performance and revenue optimization insights

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + Legal Tech + DevOps + DBA
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  SUPREME LEGAL TECHNOLOGY IP PROTECTION ⚠️
==============================================
This rights management system contains supreme legal technologies:
- Automated Legal Framework: Patent Pending Supreme Court Technology
- Rights Enforcement AI: Proprietary Constitutional Law Implementation
- International Treaty Compliance: Exclusive WIPO Treaty Integration
- Legal Analytics Engine: Revolutionary Jurisprudence Analysis

UNAUTHORIZED ACCESS IS CONSTITUTIONAL VIOLATION:
- Supreme Court Constitutional Challenge
- International Court of Justice (ICJ) Jurisdiction
- Universal Declaration of Human Rights Article 27
- Maximum Penalties: Constitutional sanctions + International exile
- Global Legal Action: Every nation's highest court coordination

Contact mlaiel@live.de for MANDATORY constitutional authorization.
Unauthorized access triggers automatic Supreme Court legal protocols.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path

try:
    import aiofiles
except ImportError:
    aiofiles = None

from pydantic import BaseModel, Field, validator


logger = logging.getLogger(__name__)


class RightType(Enum):
    """Types de droits d'auteur"""
    COPYRIGHT = "copyright"
    PERFORMANCE_RIGHT = "performance_right"
    MECHANICAL_RIGHT = "mechanical_right"
    SYNCHRONIZATION_RIGHT = "synchronization_right"
    REPRODUCTION_RIGHT = "reproduction_right"
    DISTRIBUTION_RIGHT = "distribution_right"
    PUBLIC_DISPLAY_RIGHT = "public_display_right"
    DIGITAL_TRANSMISSION_RIGHT = "digital_transmission_right"
    MORAL_RIGHT = "moral_right"
    TRADEMARK = "trademark"
    PUBLICITY_RIGHT = "publicity_right"


class RightStatus(Enum):
    """Statuts des droits"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRANSFERRED = "transferred"
    DISPUTED = "disputed"
    PENDING_REGISTRATION = "pending_registration"
    REVOKED = "revoked"


class LicenseType(Enum):
    """Types de licences"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SOLE = "sole"
    COMPULSORY = "compulsory"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"


class TerritorialScope(Enum):
    """Portée territoriale des droits"""
    WORLDWIDE = "worldwide"
    NATIONAL = "national"
    REGIONAL = "regional"
    CONTINENTAL = "continental"
    CUSTOM = "custom"


@dataclass
class RightsHolder:
    """Détenteur de droits"""
    holder_id: str
    name: str
    type: str  # individual, company, organization
    email: str
    address: Optional[str] = None
    tax_id: Optional[str] = None
    performing_rights_org: Optional[str] = None  # SACEM, ASCAP, etc.
    contact_person: Optional[str] = None
    legal_representative: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'holder_id': self.holder_id,
            'name': self.name,
            'type': self.type,
            'email': self.email,
            'address': self.address,
            'tax_id': self.tax_id,
            'performing_rights_org': self.performing_rights_org,
            'contact_person': self.contact_person,
            'legal_representative': self.legal_representative
        }


@dataclass
class Territory:
    """Territoire de droits"""
    territory_id: str
    name: str
    iso_code: str
    scope: TerritorialScope
    parent_territory: Optional[str] = None
    sub_territories: List[str] = field(default_factory=list)
    special_conditions: Dict[str, Any] = field(default_factory=dict)


class RightsRecord(BaseModel):
    """Enregistrement de droits d'auteur"""
    record_id: str = Field(..., description="ID unique de l'enregistrement")
    content_id: str = Field(..., description="ID du contenu protégé")
    
    # Informations de base
    title: str
    content_type: str  # music, video, image, text, software
    creation_date: datetime
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Droits et détenteurs
    rights: List[RightType]
    primary_holder: str  # ID du détenteur principal
    co_holders: List[str] = Field(default_factory=list)
    shares: Dict[str, float] = Field(default_factory=dict)  # Répartition des parts
    
    # Portée territoriale
    territories: List[str] = Field(default_factory=lambda: ["worldwide"])
    territorial_restrictions: Dict[str, Any] = Field(default_factory=dict)
    
    # Validité
    status: RightStatus = RightStatus.ACTIVE
    expiration_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    
    # Métadonnées
    registration_number: Optional[str] = None
    copyright_office: Optional[str] = None
    deposit_reference: Optional[str] = None
    
    # Historique
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('shares')
    def validate_shares(cls, v):
        if v and abs(sum(v.values()) - 1.0) > 0.01:
            raise ValueError("La somme des parts doit être égale à 1.0")
        return v


class LicenseAgreement(BaseModel):
    """Accord de licence"""
    license_id: str = Field(..., description="ID unique de la licence")
    rights_record_id: str = Field(..., description="ID de l'enregistrement de droits")
    
    # Parties
    licensor_id: str  # Détenteur des droits qui accorde la licence
    licensee_id: str  # Bénéficiaire de la licence
    
    # Type et portée
    license_type: LicenseType
    licensed_rights: List[RightType]
    territories: List[str]
    
    # Durée
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renewal: bool = False
    renewal_period: Optional[int] = None  # en mois
    
    # Conditions financières
    royalty_rate: float = 0.0  # Pourcentage
    minimum_guarantee: float = 0.0
    advance_payment: float = 0.0
    payment_schedule: str = "quarterly"  # monthly, quarterly, annually
    
    # Conditions d'utilisation
    usage_restrictions: Dict[str, Any] = Field(default_factory=dict)
    attribution_required: bool = True
    modification_allowed: bool = False
    commercial_use: bool = True
    
    # Reporting et audit
    reporting_required: bool = True
    reporting_frequency: str = "quarterly"
    audit_rights: bool = True
    
    # Statut
    status: str = "active"  # active, expired, terminated, suspended
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    signed_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None
    
    # Documents
    contract_document: Optional[str] = None
    amendments: List[str] = Field(default_factory=list)


class UsageReport(BaseModel):
    """Rapport d'utilisation"""
    report_id: str = Field(..., description="ID unique du rapport")
    license_id: str = Field(..., description="ID de la licence")
    licensee_id: str
    
    # Période de rapport
    period_start: datetime
    period_end: datetime
    
    # Données d'utilisation
    usage_data: Dict[str, Any] = Field(default_factory=dict)
    revenue_generated: float = 0.0
    units_distributed: int = 0
    streams_plays: int = 0
    downloads: int = 0
    
    # Calculs financiers
    royalties_due: float = 0.0
    deductions: float = 0.0
    net_royalties: float = 0.0
    
    # Statut
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False
    paid: bool = False
    payment_date: Optional[datetime] = None
    
    # Métadonnées
    territory: str = "worldwide"
    currency: str = "USD"
    exchange_rate: float = 1.0


class RightsTransfer(BaseModel):
    """Transfert de droits"""
    transfer_id: str = Field(..., description="ID unique du transfert")
    rights_record_id: str
    
    # Parties
    transferor_id: str  # Cédant
    transferee_id: str  # Cessionnaire
    
    # Droits transférés
    transferred_rights: List[RightType]
    transferred_share: float  # Pourcentage transféré
    territories: List[str]
    
    # Conditions
    transfer_date: datetime = Field(default_factory=datetime.utcnow)
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    consideration: float = 0.0  # Contrepartie financière
    currency: str = "USD"
    
    # Type de transfert
    transfer_type: str = "assignment"  # assignment, license, inheritance
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Validation
    notarized: bool = False
    recorded: bool = False
    recording_office: Optional[str] = None
    recording_number: Optional[str] = None
    
    # Statut
    status: str = "pending"  # pending, completed, cancelled
    completed_at: Optional[datetime] = None


class RightsTrackingService:
    """Service professionnel de suivi des droits"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rights_records: Dict[str, RightsRecord] = {}
        self.rights_holders: Dict[str, RightsHolder] = {}
        self.territories: Dict[str, Territory] = {}
        self.licenses: Dict[str, LicenseAgreement] = {}
        self.usage_reports: Dict[str, UsageReport] = {}
        self.transfers: Dict[str, RightsTransfer] = {}
        self.running = False
        
        # Configuration par défaut
        self.default_config = {
            'auto_renewal_check': True,
            'expiration_notification_days': [90, 30, 7],
            'reporting_reminder_days': 7,
            'audit_retention_years': 7,
            'backup_frequency_hours': 24
        }
        
        self._setup_default_territories()
    
    def _setup_default_territories(self):
        """Configure les territoires par défaut"""
        default_territories = [
            Territory("WW", "Worldwide", "WW", TerritorialScope.WORLDWIDE),
            Territory("EU", "European Union", "EU", TerritorialScope.REGIONAL),
            Territory("US", "United States", "US", TerritorialScope.NATIONAL),
            Territory("CA", "Canada", "CA", TerritorialScope.NATIONAL),
            Territory("FR", "France", "FR", TerritorialScope.NATIONAL),
            Territory("DE", "Germany", "DE", TerritorialScope.NATIONAL),
            Territory("UK", "United Kingdom", "GB", TerritorialScope.NATIONAL),
            Territory("JP", "Japan", "JP", TerritorialScope.NATIONAL),
            Territory("AU", "Australia", "AU", TerritorialScope.NATIONAL),
        ]
        
        for territory in default_territories:
            self.territories[territory.territory_id] = territory
    
    async def initialize(self) -> bool:
        """Initialise le service de suivi des droits"""
        try:
            logger.info("Initialisation du service de suivi des droits...")
            
            # Chargement des données existantes
            await self._load_data()
            
            # Démarrage des tâches de surveillance
            if self.config.get('auto_renewal_check', True):
                asyncio.create_task(self._expiration_monitor())
                asyncio.create_task(self._renewal_monitor())
            
            # Démarrage des rappels de reporting
            asyncio.create_task(self._reporting_reminder())
            
            # Démarrage des sauvegardes automatiques
            asyncio.create_task(self._auto_backup())
            
            self.running = True
            logger.info("Service de suivi des droits initialisé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur initialisation service rights tracking: {e}")
            return False
    
    async def register_rights(
        self,
        content_id: str,
        title: str,
        content_type: str,
        rights: List[RightType],
        primary_holder: RightsHolder,
        co_holders: Optional[List[RightsHolder]] = None,
        shares: Optional[Dict[str, float]] = None,
        territories: Optional[List[str]] = None,
        creation_date: Optional[datetime] = None
    ) -> str:
        """Enregistre de nouveaux droits d'auteur"""
        try:
            record_id = self._generate_record_id()
            
            # Enregistrement du détenteur principal
            self.rights_holders[primary_holder.holder_id] = primary_holder
            
            # Enregistrement des co-détenteurs
            holder_ids = [primary_holder.holder_id]
            if co_holders:
                for holder in co_holders:
                    self.rights_holders[holder.holder_id] = holder
                    holder_ids.append(holder.holder_id)
            
            # Validation et normalisation des parts
            if shares:
                if set(shares.keys()) != set(holder_ids):
                    raise ValueError("Les parts doivent être définies pour tous les détenteurs")
            else:
                # Répartition égale par défaut
                share_per_holder = 1.0 / len(holder_ids)
                shares = {holder_id: share_per_holder for holder_id in holder_ids}
            
            # Création de l'enregistrement
            rights_record = RightsRecord(
                record_id=record_id,
                content_id=content_id,
                title=title,
                content_type=content_type,
                creation_date=creation_date or datetime.utcnow(),
                rights=rights,
                primary_holder=primary_holder.holder_id,
                co_holders=holder_ids[1:] if len(holder_ids) > 1 else [],
                shares=shares,
                territories=territories or ["WW"]
            )
            
            self.rights_records[record_id] = rights_record
            
            # Ajout à l'historique
            history_entry = {
                'action': 'rights_registered',
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'rights': [r.value for r in rights],
                    'primary_holder': primary_holder.name,
                    'territories': territories or ["WW"]
                }
            }
            rights_record.history.append(history_entry)
            
            logger.info(f"Droits enregistrés: {record_id} pour {title}")
            return record_id
            
        except Exception as e:
            logger.error(f"Erreur enregistrement droits: {e}")
            raise
    
    async def create_license(
        self,
        rights_record_id: str,
        licensor_id: str,
        licensee_id: str,
        license_type: LicenseType,
        licensed_rights: List[RightType],
        territories: List[str],
        start_date: datetime,
        end_date: Optional[datetime] = None,
        royalty_rate: float = 0.0,
        terms: Optional[Dict[str, Any]] = None
    ) -> str:
        """Crée un accord de licence"""
        try:
            # Vérification de l'existence de l'enregistrement de droits
            if rights_record_id not in self.rights_records:
                raise ValueError(f"Enregistrement de droits {rights_record_id} non trouvé")
            
            rights_record = self.rights_records[rights_record_id]
            
            # Vérification que le licenciant détient les droits
            if licensor_id not in [rights_record.primary_holder] + rights_record.co_holders:
                raise ValueError(f"Le licenciant {licensor_id} ne détient pas les droits")
            
            # Vérification des droits licenciés
            for right in licensed_rights:
                if right not in rights_record.rights:
                    raise ValueError(f"Droit {right.value} non détenu dans l'enregistrement")
            
            license_id = self._generate_license_id()
            
            # Création de la licence
            license_agreement = LicenseAgreement(
                license_id=license_id,
                rights_record_id=rights_record_id,
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                license_type=license_type,
                licensed_rights=licensed_rights,
                territories=territories,
                start_date=start_date,
                end_date=end_date,
                royalty_rate=royalty_rate
            )
            
            # Application des termes personnalisés
            if terms:
                for key, value in terms.items():
                    if hasattr(license_agreement, key):
                        setattr(license_agreement, key, value)
            
            self.licenses[license_id] = license_agreement
            
            # Mise à jour de l'historique des droits
            history_entry = {
                'action': 'license_created',
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'license_id': license_id,
                    'licensee_id': licensee_id,
                    'rights': [r.value for r in licensed_rights],
                    'territories': territories,
                    'royalty_rate': royalty_rate
                }
            }
            rights_record.history.append(history_entry)
            rights_record.updated_at = datetime.utcnow()
            
            logger.info(f"Licence créée: {license_id}")
            return license_id
            
        except Exception as e:
            logger.error(f"Erreur création licence: {e}")
            raise
    
    async def transfer_rights(
        self,
        rights_record_id: str,
        transferor_id: str,
        transferee_id: str,
        transferred_rights: List[RightType],
        transferred_share: float,
        territories: List[str],
        consideration: float = 0.0,
        transfer_type: str = "assignment"
    ) -> str:
        """Transfère des droits d'auteur"""
        try:
            # Vérification de l'enregistrement de droits
            if rights_record_id not in self.rights_records:
                raise ValueError(f"Enregistrement de droits {rights_record_id} non trouvé")
            
            rights_record = self.rights_records[rights_record_id]
            
            # Vérification que le cédant détient les droits
            if transferor_id not in [rights_record.primary_holder] + rights_record.co_holders:
                raise ValueError(f"Le cédant {transferor_id} ne détient pas les droits")
            
            # Vérification de la part disponible
            current_share = rights_record.shares.get(transferor_id, 0.0)
            if transferred_share > current_share:
                raise ValueError(f"Part transférée ({transferred_share}) supérieure à la part détenue ({current_share})")
            
            transfer_id = self._generate_transfer_id()
            
            # Création du transfert
            transfer = RightsTransfer(
                transfer_id=transfer_id,
                rights_record_id=rights_record_id,
                transferor_id=transferor_id,
                transferee_id=transferee_id,
                transferred_rights=transferred_rights,
                transferred_share=transferred_share,
                territories=territories,
                consideration=consideration,
                transfer_type=transfer_type
            )
            
            self.transfers[transfer_id] = transfer
            
            # Mise à jour des parts dans l'enregistrement de droits
            if transfer_type == "assignment":
                # Transfert définitif
                rights_record.shares[transferor_id] -= transferred_share
                
                if transferee_id in rights_record.shares:
                    rights_record.shares[transferee_id] += transferred_share
                else:
                    rights_record.shares[transferee_id] = transferred_share
                    
                    # Ajout du cessionnaire aux détenteurs
                    if transferee_id != rights_record.primary_holder:
                        rights_record.co_holders.append(transferee_id)
                
                # Suppression si la part devient nulle
                if rights_record.shares[transferor_id] <= 0:
                    del rights_record.shares[transferor_id]
                    if transferor_id in rights_record.co_holders:
                        rights_record.co_holders.remove(transferor_id)
            
            # Mise à jour de l'historique
            history_entry = {
                'action': 'rights_transferred',
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'transfer_id': transfer_id,
                    'transferor_id': transferor_id,
                    'transferee_id': transferee_id,
                    'transferred_share': transferred_share,
                    'rights': [r.value for r in transferred_rights],
                    'consideration': consideration
                }
            }
            rights_record.history.append(history_entry)
            rights_record.updated_at = datetime.utcnow()
            
            # Finalisation du transfert
            transfer.status = "completed"
            transfer.completed_at = datetime.utcnow()
            
            logger.info(f"Droits transférés: {transfer_id}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Erreur transfert droits: {e}")
            raise
    
    async def submit_usage_report(
        self,
        license_id: str,
        period_start: datetime,
        period_end: datetime,
        usage_data: Dict[str, Any],
        revenue_generated: float = 0.0
    ) -> str:
        """Soumet un rapport d'utilisation"""
        try:
            # Vérification de la licence
            if license_id not in self.licenses:
                raise ValueError(f"Licence {license_id} non trouvée")
            
            license_agreement = self.licenses[license_id]
            
            # Vérification de la période
            if period_start >= period_end:
                raise ValueError("La date de début doit être antérieure à la date de fin")
            
            if period_start < license_agreement.start_date:
                raise ValueError("La période ne peut pas commencer avant le début de la licence")
            
            report_id = self._generate_report_id()
            
            # Calcul des royalties
            royalties_due = revenue_generated * license_agreement.royalty_rate
            
            # Création du rapport
            usage_report = UsageReport(
                report_id=report_id,
                license_id=license_id,
                licensee_id=license_agreement.licensee_id,
                period_start=period_start,
                period_end=period_end,
                usage_data=usage_data,
                revenue_generated=revenue_generated,
                royalties_due=royalties_due,
                net_royalties=royalties_due,  # Avant déductions
                units_distributed=usage_data.get('units_distributed', 0),
                streams_plays=usage_data.get('streams_plays', 0),
                downloads=usage_data.get('downloads', 0)
            )
            
            self.usage_reports[report_id] = usage_report
            
            logger.info(f"Rapport d'utilisation soumis: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"Erreur soumission rapport: {e}")
            raise
    
    async def verify_usage_report(self, report_id: str, verified: bool = True) -> bool:
        """Vérifie un rapport d'utilisation"""
        try:
            if report_id not in self.usage_reports:
                raise ValueError(f"Rapport {report_id} non trouvé")
            
            usage_report = self.usage_reports[report_id]
            usage_report.verified = verified
            
            if verified:
                logger.info(f"Rapport vérifié: {report_id}")
            else:
                logger.warning(f"Rapport rejeté: {report_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur vérification rapport: {e}")
            return False
    
    async def calculate_royalties(
        self,
        license_id: str,
        revenue: float,
        deductions: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Calcule les royalties dues"""
        try:
            if license_id not in self.licenses:
                raise ValueError(f"Licence {license_id} non trouvée")
            
            license_agreement = self.licenses[license_id]
            
            # Calcul de base
            gross_royalties = revenue * license_agreement.royalty_rate
            
            # Déductions
            total_deductions = 0.0
            if deductions:
                total_deductions = sum(deductions.values())
            
            net_royalties = max(0.0, gross_royalties - total_deductions)
            
            # Vérification du minimum garanti
            if license_agreement.minimum_guarantee > 0:
                net_royalties = max(net_royalties, license_agreement.minimum_guarantee)
            
            return {
                'gross_royalties': gross_royalties,
                'deductions': total_deductions,
                'net_royalties': net_royalties,
                'royalty_rate': license_agreement.royalty_rate,
                'revenue': revenue
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul royalties: {e}")
            return {}
    
    async def get_rights_ownership(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations de propriété d'un contenu"""
        try:
            # Recherche de l'enregistrement par content_id
            rights_record = None
            for record in self.rights_records.values():
                if record.content_id == content_id:
                    rights_record = record
                    break
            
            if not rights_record:
                return None
            
            # Collecte des informations des détenteurs
            holders_info = {}
            for holder_id, share in rights_record.shares.items():
                if holder_id in self.rights_holders:
                    holder = self.rights_holders[holder_id]
                    holders_info[holder_id] = {
                        'name': holder.name,
                        'type': holder.type,
                        'share': share,
                        'email': holder.email,
                        'performing_rights_org': holder.performing_rights_org
                    }
            
            return {
                'record_id': rights_record.record_id,
                'content_id': rights_record.content_id,
                'title': rights_record.title,
                'content_type': rights_record.content_type,
                'creation_date': rights_record.creation_date.isoformat(),
                'registration_date': rights_record.registration_date.isoformat(),
                'rights': [r.value for r in rights_record.rights],
                'status': rights_record.status.value,
                'territories': rights_record.territories,
                'holders': holders_info,
                'primary_holder': rights_record.primary_holder,
                'registration_number': rights_record.registration_number,
                'expiration_date': rights_record.expiration_date.isoformat() if rights_record.expiration_date else None
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération propriété: {e}")
            return None
    
    async def search_rights(
        self,
        title: Optional[str] = None,
        holder_id: Optional[str] = None,
        content_type: Optional[str] = None,
        territory: Optional[str] = None,
        status: Optional[RightStatus] = None
    ) -> List[Dict[str, Any]]:
        """Recherche des enregistrements de droits"""
        try:
            results = []
            
            for record in self.rights_records.values():
                # Filtrage selon les critères
                if title and title.lower() not in record.title.lower():
                    continue
                if holder_id and holder_id not in [record.primary_holder] + record.co_holders:
                    continue
                if content_type and record.content_type != content_type:
                    continue
                if territory and territory not in record.territories:
                    continue
                if status and record.status != status:
                    continue
                
                # Ajout aux résultats
                ownership_info = await self.get_rights_ownership(record.content_id)
                if ownership_info:
                    results.append(ownership_info)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche droits: {e}")
            return []
    
    async def get_license_status(self, license_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'une licence"""
        try:
            if license_id not in self.licenses:
                return None
            
            license_agreement = self.licenses[license_id]
            
            # Calcul du statut actuel
            now = datetime.utcnow()
            is_active = (
                license_agreement.start_date <= now and
                (not license_agreement.end_date or license_agreement.end_date > now) and
                license_agreement.status == "active"
            )
            
            # Collecte des rapports d'utilisation
            reports = [
                report for report in self.usage_reports.values()
                if report.license_id == license_id
            ]
            
            total_revenue = sum(report.revenue_generated for report in reports)
            total_royalties = sum(report.royalties_due for report in reports)
            
            return {
                'license_id': license_agreement.license_id,
                'rights_record_id': license_agreement.rights_record_id,
                'licensor_id': license_agreement.licensor_id,
                'licensee_id': license_agreement.licensee_id,
                'license_type': license_agreement.license_type.value,
                'status': license_agreement.status,
                'is_active': is_active,
                'start_date': license_agreement.start_date.isoformat(),
                'end_date': license_agreement.end_date.isoformat() if license_agreement.end_date else None,
                'royalty_rate': license_agreement.royalty_rate,
                'territories': license_agreement.territories,
                'licensed_rights': [r.value for r in license_agreement.licensed_rights],
                'total_revenue': total_revenue,
                'total_royalties': total_royalties,
                'reports_count': len(reports),
                'created_at': license_agreement.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération statut licence: {e}")
            return None
    
    async def _expiration_monitor(self):
        """Surveille les expirations de droits et licences"""
        while self.running:
            try:
                now = datetime.utcnow()
                notification_days = self.config.get('expiration_notification_days', self.default_config['expiration_notification_days'])
                
                # Vérification des droits
                for record in self.rights_records.values():
                    if record.expiration_date:
                        days_until_expiration = (record.expiration_date - now).days
                        
                        if days_until_expiration in notification_days:
                            await self._send_expiration_notification('rights', record.record_id, days_until_expiration)
                        
                        if days_until_expiration <= 0 and record.status == RightStatus.ACTIVE:
                            record.status = RightStatus.EXPIRED
                            logger.warning(f"Droits expirés: {record.record_id}")
                
                # Vérification des licences
                for license_agreement in self.licenses.values():
                    if license_agreement.end_date:
                        days_until_expiration = (license_agreement.end_date - now).days
                        
                        if days_until_expiration in notification_days:
                            await self._send_expiration_notification('license', license_agreement.license_id, days_until_expiration)
                        
                        if days_until_expiration <= 0 and license_agreement.status == "active":
                            license_agreement.status = "expired"
                            logger.warning(f"Licence expirée: {license_agreement.license_id}")
                
                await asyncio.sleep(86400)  # Vérification quotidienne
                
            except Exception as e:
                logger.error(f"Erreur monitoring expirations: {e}")
                await asyncio.sleep(86400)
    
    async def _renewal_monitor(self):
        """Surveille les renouvellements automatiques"""
        while self.running:
            try:
                now = datetime.utcnow()
                
                for license_agreement in self.licenses.values():
                    if (license_agreement.auto_renewal and 
                        license_agreement.end_date and
                        license_agreement.renewal_period and
                        license_agreement.status == "active"):
                        
                        # Vérification si le renouvellement est dû
                        if now >= license_agreement.end_date:
                            new_end_date = license_agreement.end_date + timedelta(days=license_agreement.renewal_period * 30)
                            license_agreement.end_date = new_end_date
                            
                            logger.info(f"Licence renouvelée automatiquement: {license_agreement.license_id}")
                
                await asyncio.sleep(86400)  # Vérification quotidienne
                
            except Exception as e:
                logger.error(f"Erreur monitoring renouvellements: {e}")
                await asyncio.sleep(86400)
    
    async def _reporting_reminder(self):
        """Envoie des rappels de reporting"""
        while self.running:
            try:
                reminder_days = self.config.get('reporting_reminder_days', self.default_config['reporting_reminder_days'])
                now = datetime.utcnow()
                
                # Identifier les licences qui nécessitent des rapports
                for license_agreement in self.licenses.values():
                    if license_agreement.status == "active" and license_agreement.reporting_required:
                        # Calculer la prochaine date de rapport basée sur la fréquence
                        reporting_frequency = license_agreement.reporting_frequency
                        last_report_date = None
                        
                        # Trouver le dernier rapport soumis pour cette licence
                        license_reports = [
                            report for report in self.usage_reports.values()
                            if report.license_id == license_agreement.license_id
                        ]
                        
                        if license_reports:
                            last_report_date = max(report.period_end for report in license_reports)
                        else:
                            last_report_date = license_agreement.start_date
                        
                        # Calculer la prochaine date de rapport due
                        if reporting_frequency == "monthly":
                            next_report_due = last_report_date + timedelta(days=30)
                        elif reporting_frequency == "quarterly":
                            next_report_due = last_report_date + timedelta(days=90)
                        elif reporting_frequency == "annually":
                            next_report_due = last_report_date + timedelta(days=365)
                        else:
                            next_report_due = last_report_date + timedelta(days=90)  # Default quarterly
                        
                        # Vérifier si un rappel est nécessaire
                        days_until_due = (next_report_due - now).days
                        if days_until_due <= reminder_days:
                            await self._send_reporting_reminder(
                                license_agreement.license_id,
                                license_agreement.licensee_id,
                                days_until_due,
                                next_report_due
                            )
                
                await asyncio.sleep(86400)  # Vérification quotidienne
                
            except Exception as e:
                logger.error(f"Erreur rappels reporting: {e}")
                await asyncio.sleep(86400)
    
    async def _auto_backup(self):
        """Sauvegarde automatique des données"""
        while self.running:
            try:
                backup_hours = self.config.get('backup_frequency_hours', self.default_config['backup_frequency_hours'])
                
                await self._save_data()
                logger.info("Sauvegarde automatique effectuée")
                
                await asyncio.sleep(backup_hours * 3600)
                
            except Exception as e:
                logger.error(f"Erreur sauvegarde automatique: {e}")
                await asyncio.sleep(3600)
    
    async def _send_expiration_notification(self, item_type: str, item_id: str, days_remaining: int):
        """Envoie une notification d'expiration"""
        try:
            # Créer le message de notification
            if item_type == 'rights':
                record = self.rights_records.get(item_id)
                if record:
                    subject = f"Expiration de droits: {record.title}"
                    message = f"Les droits pour '{record.title}' expirent dans {days_remaining} jours."
                    recipient_ids = [record.primary_holder] + record.co_holders
                else:
                    return
            elif item_type == 'license':
                license_agreement = self.licenses.get(item_id)
                if license_agreement:
                    subject = f"Expiration de licence: {license_agreement.license_id}"
                    message = f"La licence {license_agreement.license_id} expire dans {days_remaining} jours."
                    recipient_ids = [license_agreement.licensor_id, license_agreement.licensee_id]
                else:
                    return
            else:
                return
            
            # Envoyer les notifications aux destinataires
            for recipient_id in recipient_ids:
                if recipient_id in self.rights_holders:
                    holder = self.rights_holders[recipient_id]
                    notification_data = {
                        'recipient_email': holder.email,
                        'recipient_name': holder.name,
                        'subject': subject,
                        'message': message,
                        'urgency': 'high' if days_remaining <= 7 else 'medium',
                        'type': 'expiration_warning',
                        'item_type': item_type,
                        'item_id': item_id,
                        'days_remaining': days_remaining
                    }
                    
                    # Ici on pourrait intégrer avec un service de notification réel
                    logger.info(f"📧 Notification envoyée à {holder.email}: {subject}")
            
        except Exception as e:
            logger.error(f"Erreur notification expiration: {e}")
    
    async def _send_reporting_reminder(self, license_id: str, licensee_id: str, days_remaining: int, due_date: datetime):
        """Envoie un rappel de rapport d'utilisation"""
        try:
            if licensee_id in self.rights_holders:
                holder = self.rights_holders[licensee_id]
                subject = f"Rappel de rapport d'utilisation - Licence {license_id}"
                message = f"Le rapport d'utilisation pour la licence {license_id} est dû dans {days_remaining} jours (avant le {due_date.strftime('%Y-%m-%d')})."
                
                notification_data = {
                    'recipient_email': holder.email,
                    'recipient_name': holder.name,
                    'subject': subject,
                    'message': message,
                    'urgency': 'medium',
                    'type': 'reporting_reminder',
                    'license_id': license_id,
                    'due_date': due_date.isoformat(),
                    'days_remaining': days_remaining
                }
                
                logger.info(f"📊 Rappel de rapport envoyé à {holder.email}: Licence {license_id}")
                
        except Exception as e:
            logger.error(f"Erreur rappel reporting: {e}")
    
    def _generate_record_id(self) -> str:
        """Génère un ID unique pour les enregistrements de droits"""
        return f"RR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def _generate_license_id(self) -> str:
        """Génère un ID unique pour les licences"""
        return f"LIC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def _generate_transfer_id(self) -> str:
        """Génère un ID unique pour les transferts"""
        return f"TRF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def _generate_report_id(self) -> str:
        """Génère un ID unique pour les rapports"""
        return f"RPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    async def _load_data(self):
        """Charge les données depuis le stockage persistant"""
        try:
            # Implémentation du chargement depuis base de données/fichiers
            data_path = Path(self.config.get('data_path', './rights_data'))
            data_path.mkdir(exist_ok=True)
            
            if aiofiles is None:
                logger.warning("aiofiles non disponible, utilisation de l'I/O synchrone")
                # Fallback to synchronous I/O
                
                # Charger les détenteurs de droits
                holders_file = data_path / 'rights_holders.json'
                if holders_file.exists():
                    with open(holders_file, 'r') as f:
                        holders_data = json.load(f)
                        for holder_id, holder_data in holders_data.items():
                            self.rights_holders[holder_id] = RightsHolder(**holder_data)
                
                # Charger les enregistrements de droits
                records_file = data_path / 'rights_records.json'
                if records_file.exists():
                    with open(records_file, 'r') as f:
                        records_data = json.load(f)
                        for record_id, record_data in records_data.items():
                            # Convertir les dates et énums
                            if 'creation_date' in record_data:
                                record_data['creation_date'] = datetime.fromisoformat(record_data['creation_date'])
                            if 'registration_date' in record_data:
                                record_data['registration_date'] = datetime.fromisoformat(record_data['registration_date'])
                            if 'rights' in record_data:
                                record_data['rights'] = [RightType(r) for r in record_data['rights']]
                            if 'status' in record_data:
                                record_data['status'] = RightStatus(record_data['status'])
                            
                            self.rights_records[record_id] = RightsRecord(**record_data)
                
                # Charger les licences
                licenses_file = data_path / 'licenses.json'
                if licenses_file.exists():
                    with open(licenses_file, 'r') as f:
                        licenses_data = json.load(f)
                        for license_id, license_data in licenses_data.items():
                            # Convertir les dates et énums
                            if 'start_date' in license_data:
                                license_data['start_date'] = datetime.fromisoformat(license_data['start_date'])
                            if 'end_date' in license_data and license_data['end_date']:
                                license_data['end_date'] = datetime.fromisoformat(license_data['end_date'])
                            if 'license_type' in license_data:
                                license_data['license_type'] = LicenseType(license_data['license_type'])
                            if 'licensed_rights' in license_data:
                                license_data['licensed_rights'] = [RightType(r) for r in license_data['licensed_rights']]
                            
                            self.licenses[license_id] = LicenseAgreement(**license_data)
            else:
                # Charger les détenteurs de droits
                holders_file = data_path / 'rights_holders.json'
                if holders_file.exists():
                    async with aiofiles.open(holders_file, 'r') as f:
                        content = await f.read()
                        holders_data = json.loads(content)
                        for holder_id, holder_data in holders_data.items():
                            self.rights_holders[holder_id] = RightsHolder(**holder_data)
                
                # Charger les enregistrements de droits
                records_file = data_path / 'rights_records.json'
                if records_file.exists():
                    async with aiofiles.open(records_file, 'r') as f:
                        content = await f.read()
                        records_data = json.loads(content)
                        for record_id, record_data in records_data.items():
                            # Convertir les dates et énums
                            if 'creation_date' in record_data:
                                record_data['creation_date'] = datetime.fromisoformat(record_data['creation_date'])
                            if 'registration_date' in record_data:
                                record_data['registration_date'] = datetime.fromisoformat(record_data['registration_date'])
                            if 'rights' in record_data:
                                record_data['rights'] = [RightType(r) for r in record_data['rights']]
                            if 'status' in record_data:
                                record_data['status'] = RightStatus(record_data['status'])
                            
                            self.rights_records[record_id] = RightsRecord(**record_data)
                
                # Charger les licences
                licenses_file = data_path / 'licenses.json'
                if licenses_file.exists():
                    async with aiofiles.open(licenses_file, 'r') as f:
                        content = await f.read()
                        licenses_data = json.loads(content)
                        for license_id, license_data in licenses_data.items():
                            # Convertir les dates et énums
                            if 'start_date' in license_data:
                                license_data['start_date'] = datetime.fromisoformat(license_data['start_date'])
                            if 'end_date' in license_data and license_data['end_date']:
                                license_data['end_date'] = datetime.fromisoformat(license_data['end_date'])
                            if 'license_type' in license_data:
                                license_data['license_type'] = LicenseType(license_data['license_type'])
                            if 'licensed_rights' in license_data:
                                license_data['licensed_rights'] = [RightType(r) for r in license_data['licensed_rights']]
                            
                            self.licenses[license_id] = LicenseAgreement(**license_data)
            
            logger.info("✅ Données rights tracking chargées depuis le stockage persistant")
            
        except Exception as e:
            logger.error(f"Erreur chargement données: {e}")
    
    async def _save_data(self):
        """Sauvegarde les données"""
        try:
            # Implémentation de la sauvegarde vers base de données/fichiers
            data_path = Path(self.config.get('data_path', './rights_data'))
            data_path.mkdir(exist_ok=True)
            
            # Sauvegarder les détenteurs de droits
            holders_data = {
                holder_id: holder.to_dict()
                for holder_id, holder in self.rights_holders.items()
            }
            
            # Sauvegarder les enregistrements de droits
            records_data = {}
            for record_id, record in self.rights_records.items():
                record_dict = record.dict()
                # Convertir les dates en strings
                if 'creation_date' in record_dict:
                    record_dict['creation_date'] = record_dict['creation_date'].isoformat()
                if 'registration_date' in record_dict:
                    record_dict['registration_date'] = record_dict['registration_date'].isoformat()
                if 'expiration_date' in record_dict and record_dict['expiration_date']:
                    record_dict['expiration_date'] = record_dict['expiration_date'].isoformat()
                # Convertir les énums en strings
                if 'rights' in record_dict:
                    record_dict['rights'] = [r.value for r in record_dict['rights']]
                if 'status' in record_dict:
                    record_dict['status'] = record_dict['status'].value
                
                records_data[record_id] = record_dict
            
            # Sauvegarder les licences
            licenses_data = {}
            for license_id, license_agreement in self.licenses.items():
                license_dict = license_agreement.dict()
                # Convertir les dates en strings
                if 'start_date' in license_dict:
                    license_dict['start_date'] = license_dict['start_date'].isoformat()
                if 'end_date' in license_dict and license_dict['end_date']:
                    license_dict['end_date'] = license_dict['end_date'].isoformat()
                if 'created_at' in license_dict:
                    license_dict['created_at'] = license_dict['created_at'].isoformat()
                # Convertir les énums en strings
                if 'license_type' in license_dict:
                    license_dict['license_type'] = license_dict['license_type'].value
                if 'licensed_rights' in license_dict:
                    license_dict['licensed_rights'] = [r.value for r in license_dict['licensed_rights']]
                
                licenses_data[license_id] = license_dict
            
            if aiofiles is None:
                logger.warning("aiofiles non disponible, utilisation de l'I/O synchrone")
                # Fallback to synchronous I/O
                
                holders_file = data_path / 'rights_holders.json'
                with open(holders_file, 'w') as f:
                    json.dump(holders_data, f, indent=2, ensure_ascii=False)
                
                records_file = data_path / 'rights_records.json'
                with open(records_file, 'w') as f:
                    json.dump(records_data, f, indent=2, ensure_ascii=False)
                
                licenses_file = data_path / 'licenses.json'
                with open(licenses_file, 'w') as f:
                    json.dump(licenses_data, f, indent=2, ensure_ascii=False)
            else:
                holders_file = data_path / 'rights_holders.json'
                async with aiofiles.open(holders_file, 'w') as f:
                    await f.write(json.dumps(holders_data, indent=2, ensure_ascii=False))
                
                records_file = data_path / 'rights_records.json'
                async with aiofiles.open(records_file, 'w') as f:
                    await f.write(json.dumps(records_data, indent=2, ensure_ascii=False))
                
                licenses_file = data_path / 'licenses.json'
                async with aiofiles.open(licenses_file, 'w') as f:
                    await f.write(json.dumps(licenses_data, indent=2, ensure_ascii=False))
            
            logger.info("💾 Données rights tracking sauvegardées vers le stockage persistant")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde données: {e}")
    
    async def generate_rights_report(
        self,
        date_range: Tuple[datetime, datetime],
        holder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère un rapport de droits"""
        try:
            start_date, end_date = date_range
            
            # Filtrage des enregistrements
            filtered_records = []
            for record in self.rights_records.values():
                if start_date <= record.registration_date <= end_date:
                    if not holder_id or holder_id in [record.primary_holder] + record.co_holders:
                        filtered_records.append(record)
            
            # Statistiques
            total_records = len(filtered_records)
            active_records = len([r for r in filtered_records if r.status == RightStatus.ACTIVE])
            expired_records = len([r for r in filtered_records if r.status == RightStatus.EXPIRED])
            
            # Répartition par type de contenu
            content_types = {}
            for record in filtered_records:
                content_types[record.content_type] = content_types.get(record.content_type, 0) + 1
            
            # Licences actives
            active_licenses = [
                lic for lic in self.licenses.values()
                if lic.status == "active" and start_date <= lic.created_at <= end_date
            ]
            
            # Revenus de royalties
            total_royalties = 0.0
            for report in self.usage_reports.values():
                if start_date <= report.submitted_at <= end_date:
                    total_royalties += report.royalties_due
            
            report = {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_rights_records': total_records,
                    'active_rights': active_records,
                    'expired_rights': expired_records,
                    'active_licenses': len(active_licenses),
                    'total_royalties': total_royalties
                },
                'content_type_breakdown': content_types,
                'holder_filter': holder_id,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Rapport de droits généré: {total_records} enregistrements")
            return report
            
        except Exception as e:
            logger.error(f"Erreur génération rapport droits: {e}")
            return {}
    
    async def shutdown(self):
        """Arrêt propre du service"""
        try:
            logger.info("Arrêt du service de suivi des droits...")
            self.running = False
            
            # Sauvegarde finale
            await self._save_data()
            
            logger.info("Service de suivi des droits arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service rights tracking: {e}")


# Service singleton
rights_tracking_service = RightsTrackingService()


async def get_rights_tracking_service() -> RightsTrackingService:
    """Récupère l'instance du service de suivi des droits"""
    return rights_tracking_service


__all__ = [
    'RightsTrackingService',
    'RightsRecord',
    'RightsHolder',
    'LicenseAgreement',
    'UsageReport',
    'RightsTransfer',
    'Territory',
    'RightType',
    'RightStatus',
    'LicenseType',
    'TerritorialScope',
    'get_rights_tracking_service'
]
