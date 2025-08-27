"""
📄 Contract Manager - Digital Contract Management System
======================================================

Professional contract lifecycle management system:
- Digital contract creation and storage
- Automated contract execution
- Compliance monitoring
- Amendment and modification tracking
- Performance analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Legal Tech Specialist + Contract Specialist + Blockchain Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class ContractStatus(Enum):
    """Contract lifecycle status"""
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    BREACHED = "breached"

class ContractType(Enum):
    """Types of contracts"""
    LICENSING_AGREEMENT = "licensing_agreement"
    DISTRIBUTION_AGREEMENT = "distribution_agreement"
    MANAGEMENT_AGREEMENT = "management_agreement"
    PUBLISHING_AGREEMENT = "publishing_agreement"
    RECORDING_AGREEMENT = "recording_agreement"
    SYNC_AGREEMENT = "sync_agreement"

class AmendmentType(Enum):
    """Types of contract amendments"""
    TERM_EXTENSION = "term_extension"
    REVENUE_MODIFICATION = "revenue_modification"
    TERRITORY_CHANGE = "territory_change"
    RIGHTS_MODIFICATION = "rights_modification"
    GENERAL_AMENDMENT = "general_amendment"

@dataclass
class ContractParty:
    """Contract party information"""
    party_id: str
    name: str
    role: str  # licensor, licensee, manager, etc.
    contact_info: Dict[str, Any]
    legal_entity_type: str
    jurisdiction: str
    signature_status: bool
    signature_date: Optional[datetime]

@dataclass
class ContractTerms:
    """Contract terms and conditions"""
    effective_date: datetime
    expiration_date: Optional[datetime]
    territory: str
    exclusivity: bool
    revenue_terms: Dict[str, Any]
    performance_obligations: List[str]
    termination_conditions: List[str]
    amendment_procedures: Dict[str, Any]

@dataclass
class ContractRecord:
    """Complete contract record"""
    contract_id: str
    license_id: str
    contract_type: ContractType
    status: ContractStatus
    parties: List[ContractParty]
    terms: ContractTerms
    document_hash: str
    version: str
    created_at: datetime
    last_modified: datetime
    amendments: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]

class ContractManager:
    """
    🚀 Professional contract management system
    
    Advanced system for managing digital contracts with automated
    lifecycle management and compliance monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize contract manager with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Contract storage
        self.contracts = {}  # In production, this would be a database
        self.contract_templates = {}
        
        # Digital signature integration
        self.signature_providers = {}
        
        # Blockchain integration for immutable records
        self.blockchain_enabled = config.get('blockchain_enabled', False)
        self.blockchain_contracts = {}
        
        # Performance monitoring
        self.performance_metrics = {
            'contracts_created': 0,
            'contracts_executed': 0,
            'amendments_processed': 0,
            'breaches_detected': 0,
            'average_execution_time': 0.0
        }
        
        self._initialize_signature_providers()
        self._load_contract_templates()
    
    def _initialize_signature_providers(self):
        """Initialize digital signature service integrations."""
        try:
            # DocuSign integration
            if self.config.get('docusign_enabled', False):
                from .integrations.docusign_provider import DocuSignProvider
                self.signature_providers['docusign'] = DocuSignProvider(
                    self.config.get('docusign_config', {})
                )
            
            # Adobe Sign integration
            if self.config.get('adobe_sign_enabled', False):
                from .integrations.adobe_sign_provider import AdobeSignProvider
                self.signature_providers['adobe_sign'] = AdobeSignProvider(
                    self.config.get('adobe_sign_config', {})
                )
            
            # EU qualified electronic signature
            if self.config.get('qualified_signature_enabled', False):
                from .integrations.qualified_signature_provider import QualifiedSignatureProvider
                self.signature_providers['qualified'] = QualifiedSignatureProvider(
                    self.config.get('qualified_signature_config', {})
                )
            
            self.logger.info(f"Initialized {len(self.signature_providers)} signature providers")
            
        except ImportError as e:
            self.logger.warning(f"Some signature providers not available: {e}")
        except Exception as e:
            self.logger.error(f"Failed to initialize signature providers: {e}")
    
    def _load_contract_templates(self):
        """Load contract templates."""
        template_path = Path(self.config.get('template_path', 'templates/contracts'))
        
        if not template_path.exists():
            template_path.mkdir(parents=True, exist_ok=True)
            self._create_default_contract_templates(template_path)
        
        for template_file in template_path.glob("*.json"):
            contract_type = template_file.stem
            with open(template_file, 'r', encoding='utf-8') as f:
                self.contract_templates[contract_type] = json.load(f)
        
        self.logger.info(f"Loaded {len(self.contract_templates)} contract templates")
    
    def _create_default_contract_templates(self, template_path: Path):
        """Create default contract templates."""
        templates = {
            'licensing_agreement': {
                'name': 'Music Licensing Agreement',
                'required_parties': ['licensor', 'licensee'],
                'required_terms': [
                    'effective_date',
                    'territory',
                    'revenue_split',
                    'duration'
                ],
                'standard_clauses': [
                    'grant_of_rights',
                    'revenue_sharing',
                    'territory_restrictions',
                    'performance_obligations',
                    'termination_conditions'
                ]
            },
            'distribution_agreement': {
                'name': 'Music Distribution Agreement',
                'required_parties': ['artist', 'distributor'],
                'required_terms': [
                    'distribution_territory',
                    'distribution_channels',
                    'revenue_split',
                    'reporting_requirements'
                ],
                'standard_clauses': [
                    'distribution_rights',
                    'revenue_accounting',
                    'marketing_obligations',
                    'quality_standards'
                ]
            }
        }
        
        for template_name, template_data in templates.items():
            template_file = template_path / f"{template_name}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
    
    async def register_license(
        self,
        license_data: Dict[str, Any],
        royalty_structure: Dict[str, Any],
        smart_contract_address: Optional[str] = None
    ) -> str:
        """
        📝 Register a new license as a digital contract
        
        Args:
            license_data: Complete license information
            royalty_structure: Revenue sharing configuration
            smart_contract_address: Blockchain contract address if applicable
            
        Returns:
            contract_id: Unique contract identifier
        """
        try:
            contract_id = str(uuid.uuid4())
            license_id = license_data.get('metadata', {}).get('license_id', str(uuid.uuid4()))
            
            self.logger.info(f"Registering license as contract: {contract_id}")
            
            # Extract parties from license data
            parties = await self._extract_contract_parties(license_data)
            
            # Create contract terms from license
            terms = await self._create_contract_terms(license_data, royalty_structure)
            
            # Calculate document hash
            document_hash = self._calculate_contract_hash(license_data)
            
            # Create contract record
            contract = ContractRecord(
                contract_id=contract_id,
                license_id=license_id,
                contract_type=ContractType.LICENSING_AGREEMENT,
                status=ContractStatus.DRAFT,
                parties=parties,
                terms=terms,
                document_hash=document_hash,
                version="1.0",
                created_at=datetime.now(),
                last_modified=datetime.now(),
                amendments=[],
                performance_metrics={}
            )
            
            # Store contract
            self.contracts[contract_id] = contract
            
            # Store on blockchain if enabled
            if self.blockchain_enabled and smart_contract_address:
                await self._store_on_blockchain(contract, smart_contract_address)
            
            # Initiate signature process
            if self.config.get('auto_signature_workflow', True):
                await self._initiate_signature_workflow(contract)
            
            self.performance_metrics['contracts_created'] += 1
            
            return contract_id
            
        except Exception as e:
            self.logger.error(f"Failed to register license: {e}")
            raise
    
    async def _extract_contract_parties(self, license_data: Dict[str, Any]) -> List[ContractParty]:
        """Extract contract parties from license data."""
        parties = []
        
        # Licensor (content creator)
        licensor_info = license_data.get('content_info', {})
        licensor = ContractParty(
            party_id=licensor_info.get('creator_id', 'unknown'),
            name=licensor_info.get('creator_name', 'Unknown Creator'),
            role='licensor',
            contact_info=licensor_info.get('contact_info', {}),
            legal_entity_type=licensor_info.get('entity_type', 'individual'),
            jurisdiction=license_data.get('metadata', {}).get('jurisdiction', 'international'),
            signature_status=False,
            signature_date=None
        )
        parties.append(licensor)
        
        # Licensee (content user)
        licensee_info = license_data.get('licensee_info', {})
        if licensee_info:
            licensee = ContractParty(
                party_id=licensee_info.get('licensee_id', 'unknown'),
                name=licensee_info.get('licensee_name', 'Unknown Licensee'),
                role='licensee',
                contact_info=licensee_info.get('contact_info', {}),
                legal_entity_type=licensee_info.get('entity_type', 'individual'),
                jurisdiction=licensee_info.get('jurisdiction', 'international'),
                signature_status=False,
                signature_date=None
            )
            parties.append(licensee)
        
        return parties
    
    async def _create_contract_terms(
        self,
        license_data: Dict[str, Any],
        royalty_structure: Dict[str, Any]
    ) -> ContractTerms:
        """Create contract terms from license and royalty data."""
        license_terms = license_data.get('terms', {})
        license_metadata = license_data.get('metadata', {})
        
        return ContractTerms(
            effective_date=datetime.fromisoformat(license_metadata.get('created_at', datetime.now().isoformat())),
            expiration_date=datetime.fromisoformat(license_metadata['expires_at']) if license_metadata.get('expires_at') else None,
            territory=license_terms.get('territory', 'worldwide'),
            exclusivity=license_terms.get('exclusivity', False),
            revenue_terms=royalty_structure,
            performance_obligations=license_terms.get('performance_obligations', []),
            termination_conditions=license_terms.get('termination_conditions', []),
            amendment_procedures={
                'notice_period': '30 days',
                'approval_required': True,
                'documentation_required': True
            }
        )
    
    def _calculate_contract_hash(self, contract_data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of contract for integrity verification."""
        contract_string = json.dumps(contract_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(contract_string.encode()).hexdigest()
    
    async def _store_on_blockchain(self, contract: ContractRecord, smart_contract_address: str):
        """Store contract hash on blockchain for immutability."""
        try:
            # This would integrate with actual blockchain
            blockchain_record = {
                'contract_id': contract.contract_id,
                'document_hash': contract.document_hash,
                'timestamp': contract.created_at.isoformat(),
                'smart_contract_address': smart_contract_address
            }
            
            self.blockchain_contracts[contract.contract_id] = blockchain_record
            self.logger.info(f"Contract {contract.contract_id} stored on blockchain")
            
        except Exception as e:
            self.logger.error(f"Failed to store contract on blockchain: {e}")
            # Don't fail the entire registration for blockchain issues
    
    async def _initiate_signature_workflow(self, contract: ContractRecord):
        """Initiate digital signature workflow."""
        try:
            # Get preferred signature provider
            provider_name = self.config.get('default_signature_provider', 'docusign')
            provider = self.signature_providers.get(provider_name)
            
            if not provider:
                self.logger.warning(f"Signature provider {provider_name} not available")
                return
            
            # Create signature request
            signature_request = await provider.create_signature_request(
                contract_id=contract.contract_id,
                parties=contract.parties,
                document_data=asdict(contract)
            )
            
            # Update contract status
            contract.status = ContractStatus.PENDING_SIGNATURE
            contract.last_modified = datetime.now()
            
            self.logger.info(f"Signature workflow initiated for contract {contract.contract_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initiate signature workflow: {e}")
    
    async def update_license(
        self,
        license_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔄 Update an existing license contract
        
        Args:
            license_id: License identifier to update
            updates: Dictionary of updates to apply
            
        Returns:
            updated_contract: Updated contract information
        """
        try:
            # Find contract by license_id
            contract = None
            for c in self.contracts.values():
                if c.license_id == license_id:
                    contract = c
                    break
            
            if not contract:
                raise ValueError(f"Contract not found for license {license_id}")
            
            self.logger.info(f"Updating contract for license: {license_id}")
            
            # Create amendment record
            amendment = {
                'amendment_id': str(uuid.uuid4()),
                'amendment_type': AmendmentType.GENERAL_AMENDMENT.value,
                'changes': updates,
                'created_at': datetime.now().isoformat(),
                'status': 'pending_approval'
            }
            
            # Apply updates to contract terms
            if 'expiration_date' in updates:
                contract.terms.expiration_date = datetime.fromisoformat(updates['expiration_date'])
                amendment['amendment_type'] = AmendmentType.TERM_EXTENSION.value
            
            if 'revenue_terms' in updates:
                contract.terms.revenue_terms.update(updates['revenue_terms'])
                amendment['amendment_type'] = AmendmentType.REVENUE_MODIFICATION.value
            
            if 'territory' in updates:
                contract.terms.territory = updates['territory']
                amendment['amendment_type'] = AmendmentType.TERRITORY_CHANGE.value
            
            # Update contract metadata
            contract.amendments.append(amendment)
            contract.last_modified = datetime.now()
            contract.version = f"{float(contract.version) + 0.1:.1f}"
            
            # Recalculate document hash
            contract.document_hash = self._calculate_contract_hash(updates)
            
            # Update blockchain record if enabled
            if self.blockchain_enabled and contract.contract_id in self.blockchain_contracts:
                await self._update_blockchain_record(contract)
            
            self.performance_metrics['amendments_processed'] += 1
            
            return asdict(contract)
            
        except Exception as e:
            self.logger.error(f"Failed to update license: {e}")
            raise
    
    async def _update_blockchain_record(self, contract: ContractRecord):
        """Update blockchain record with new contract hash."""
        try:
            blockchain_record = self.blockchain_contracts.get(contract.contract_id)
            if blockchain_record:
                blockchain_record.update({
                    'document_hash': contract.document_hash,
                    'last_updated': datetime.now().isoformat(),
                    'version': contract.version
                })
                
                self.logger.info(f"Blockchain record updated for contract {contract.contract_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to update blockchain record: {e}")
    
    async def transfer_license(
        self,
        license_id: str,
        new_owner: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔄 Transfer license ownership
        
        Args:
            license_id: License identifier to transfer
            new_owner: New owner information
            
        Returns:
            transfer_result: Transfer operation result
        """
        try:
            # Find contract
            contract = None
            for c in self.contracts.values():
                if c.license_id == license_id:
                    contract = c
                    break
            
            if not contract:
                raise ValueError(f"Contract not found for license {license_id}")
            
            self.logger.info(f"Transferring license ownership: {license_id}")
            
            # Create new party record for new owner
            new_party = ContractParty(
                party_id=new_owner.get('id', str(uuid.uuid4())),
                name=new_owner.get('name', 'Unknown'),
                role='licensee',
                contact_info=new_owner.get('contact_info', {}),
                legal_entity_type=new_owner.get('entity_type', 'individual'),
                jurisdiction=new_owner.get('jurisdiction', 'international'),
                signature_status=False,
                signature_date=None
            )
            
            # Find and replace current licensee
            for i, party in enumerate(contract.parties):
                if party.role == 'licensee':
                    contract.parties[i] = new_party
                    break
            else:
                # No existing licensee, add new one
                contract.parties.append(new_party)
            
            # Create transfer amendment
            transfer_amendment = {
                'amendment_id': str(uuid.uuid4()),
                'amendment_type': 'ownership_transfer',
                'new_owner': asdict(new_party),
                'transfer_date': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            contract.amendments.append(transfer_amendment)
            contract.last_modified = datetime.now()
            contract.version = f"{float(contract.version) + 0.1:.1f}"
            
            # Generate transfer ID
            transfer_id = str(uuid.uuid4())
            
            return {
                'transfer_id': transfer_id,
                'license_id': license_id,
                'new_owner': asdict(new_party),
                'transfer_date': datetime.now().isoformat(),
                'status': 'completed'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to transfer license: {e}")
            raise
    
    def get_license_info(self, license_id: str) -> Optional[Dict[str, Any]]:
        """Get license information by license ID."""
        for contract in self.contracts.values():
            if contract.license_id == license_id:
                return asdict(contract)
        return None
    
    async def calculate_expiration_date(
        self,
        current_expiration: str,
        renewal_period: str
    ) -> str:
        """Calculate new expiration date for license renewal."""
        try:
            current_date = datetime.fromisoformat(current_expiration)
            
            # Parse renewal period
            if 'year' in renewal_period.lower():
                years = int(renewal_period.split()[0])
                new_date = current_date + timedelta(days=years * 365)
            elif 'month' in renewal_period.lower():
                months = int(renewal_period.split()[0])
                new_date = current_date + timedelta(days=months * 30)
            elif 'day' in renewal_period.lower():
                days = int(renewal_period.split()[0])
                new_date = current_date + timedelta(days=days)
            else:
                raise ValueError(f"Unable to parse renewal period: {renewal_period}")
            
            return new_date.isoformat()
            
        except Exception as e:
            self.logger.error(f"Failed to calculate expiration date: {e}")
            raise
    
    def get_active_license_count(self) -> int:
        """Get count of active licenses."""
        return len([c for c in self.contracts.values() if c.status == ContractStatus.ACTIVE])
    
    async def monitor_contract_performance(self, contract_id: str) -> Dict[str, Any]:
        """Monitor contract performance and compliance."""
        contract = self.contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        
        # Performance metrics would be calculated based on actual usage
        performance_data = {
            'contract_id': contract_id,
            'status': contract.status.value,
            'days_active': (datetime.now() - contract.created_at).days,
            'amendments_count': len(contract.amendments),
            'parties_signed': sum(1 for party in contract.parties if party.signature_status),
            'compliance_score': 0.95,  # Would be calculated based on actual performance
            'revenue_generated': 0.0,  # Would be calculated from actual revenue data
            'last_activity': contract.last_modified.isoformat()
        }
        
        # Update contract performance metrics
        contract.performance_metrics.update(performance_data)
        
        return performance_data
    
    def get_contract_metrics(self) -> Dict[str, Any]:
        """Get comprehensive contract management metrics."""
        active_contracts = [c for c in self.contracts.values() if c.status == ContractStatus.ACTIVE]
        expired_contracts = [c for c in self.contracts.values() if c.status == ContractStatus.EXPIRED]
        
        return {
            **self.performance_metrics,
            'total_contracts': len(self.contracts),
            'active_contracts': len(active_contracts),
            'expired_contracts': len(expired_contracts),
            'pending_signatures': len([c for c in self.contracts.values() if c.status == ContractStatus.PENDING_SIGNATURE]),
            'average_contract_duration': self._calculate_average_duration(active_contracts),
            'signature_providers': list(self.signature_providers.keys()),
            'blockchain_enabled': self.blockchain_enabled,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_average_duration(self, contracts: List[ContractRecord]) -> float:
        """Calculate average contract duration in days."""
        if not contracts:
            return 0.0
        
        durations = []
        for contract in contracts:
            if contract.terms.expiration_date:
                duration = (contract.terms.expiration_date - contract.terms.effective_date).days
                durations.append(duration)
        
        return sum(durations) / len(durations) if durations else 0.0
