"""
Contract Management Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔐 CONTRACT MANAGEMENT SERVICE
=============================

Advanced contract management and automation service for the Ainflue platform.
Handles collaboration contracts, licensing agreements, and legal document automation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis.asyncio as redis
from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractType(Enum):
    """Contract type enumeration"""
    COLLABORATION = "collaboration"
    LICENSING = "licensing"
    SPONSORSHIP = "sponsorship"
    REVENUE_SHARE = "revenue_share"
    EXCLUSIVE_CONTENT = "exclusive_content"
    BRAND_PARTNERSHIP = "brand_partnership"
    DISTRIBUTION = "distribution"
    EMPLOYMENT = "employment"
    NDA = "nda"
    SERVICE_AGREEMENT = "service_agreement"

class ContractStatus(Enum):
    """Contract status enumeration"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    DISPUTED = "disputed"

class SignatureStatus(Enum):
    """Signature status enumeration"""
    PENDING = "pending"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"

@dataclass
class ContractParty:
    """Contract party definition"""
    id: str
    name: str
    email: str
    role: str  # "creator", "collaborator", "brand", "platform"
    signature_status: SignatureStatus = SignatureStatus.PENDING
    signed_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    digital_signature: Optional[str] = None

@dataclass
class ContractTerm:
    """Contract term definition"""
    id: str
    title: str
    description: str
    value: Any
    is_negotiable: bool = True
    negotiated_value: Optional[Any] = None
    negotiated_by: Optional[str] = None
    negotiated_at: Optional[datetime] = None

@dataclass
class ContractMilestone:
    """Contract milestone definition"""
    id: str
    title: str
    description: str
    due_date: datetime
    deliverables: List[str]
    payment_amount: float = 0.0
    status: str = "pending"  # "pending", "in_progress", "completed", "overdue"
    completed_at: Optional[datetime] = None

@dataclass
class Contract:
    """Contract definition"""
    id: str
    title: str
    description: str
    contract_type: ContractType
    status: ContractStatus
    parties: List[ContractParty]
    terms: List[ContractTerm]
    milestones: List[ContractMilestone]
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = False
    renewal_period: Optional[timedelta] = None
    total_value: float = 0.0
    currency: str = "USD"
    template_id: Optional[str] = None
    generated_document: Optional[str] = None
    created_by: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ContractTemplate:
    """Contract template definition"""
    id: str
    name: str
    description: str
    contract_type: ContractType
    template_content: str
    variables: List[str]
    default_terms: List[Dict[str, Any]]
    jurisdictions: List[str]
    created_by: str
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ContractAnalytics:
    """Contract analytics and metrics"""
    total_contracts: int = 0
    active_contracts: int = 0
    pending_signatures: int = 0
    contracts_by_type: Dict[str, int] = None
    avg_completion_time: float = 0.0
    revenue_under_contract: float = 0.0
    upcoming_renewals: int = 0
    
    def __post_init__(self) -> None:
        if self.contracts_by_type is None:
            self.contracts_by_type = {}

class ContractManagementService:
    """Enterprise contract management service"""
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.redis_url = redis_url
        self.contracts: Dict[str, Contract] = {}
        self.templates: Dict[str, ContractTemplate] = {}
        self.pending_signatures: Dict[str, str] = {}  # signature_id -> contract_id
        self.analytics = ContractAnalytics()
        self.running = False
        self.redis_client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default templates
        self._init_default_templates()
    
    async def start(self) -> None:
        """Start the contract management service"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.running = True
            self.logger.info("🚀 Contract Management Service started")
            
            # Start background tasks
            asyncio.create_task(self._contract_monitor())
            asyncio.create_task(self._analytics_collector())
            asyncio.create_task(self._renewal_notifier())
            
        except Exception as e:
            self.logger.error(f"❌ Error starting contract management service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the contract management service"""
        try:
            self.running = False
            if self.redis_client:
                await self.redis_client.close()
            
            self.logger.info("🛑 Contract Management Service stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping contract management service: {e}")
    
    def _init_default_templates(self) -> None:
        """Initialize default contract templates"""
        # Collaboration Contract Template
        collaboration_template = ContractTemplate(
            id="collaboration_template",
            name="Creator Collaboration Agreement",
            description="Standard collaboration agreement between creators",
            contract_type=ContractType.COLLABORATION,
            template_content="""
            CREATOR COLLABORATION AGREEMENT
            
            This agreement is made between {{creator_1_name}} and {{creator_2_name}} 
            for the collaboration project titled "{{project_title}}".
            
            TERMS:
            1. Project Duration: {{project_duration}} days
            2. Revenue Split: {{revenue_split}}
            3. Content Ownership: {{content_ownership}}
            4. Delivery Date: {{delivery_date}}
            
            RESPONSIBILITIES:
            Creator 1: {{creator_1_responsibilities}}
            Creator 2: {{creator_2_responsibilities}}
            
            This agreement is effective from {{start_date}} to {{end_date}}.
            """,
            variables=[
                "creator_1_name", "creator_2_name", "project_title", 
                "project_duration", "revenue_split", "content_ownership",
                "delivery_date", "creator_1_responsibilities", "creator_2_responsibilities",
                "start_date", "end_date"
            ],
            default_terms=[
                {"title": "Revenue Split", "value": "50/50", "is_negotiable": True},
                {"title": "Content Ownership", "value": "Joint ownership", "is_negotiable": True},
                {"title": "Exclusivity", "value": "Non-exclusive", "is_negotiable": True}
            ],
            jurisdictions=["US", "EU", "CA"],
            created_by="system"
        )
        
        self.templates[collaboration_template.id] = collaboration_template
        
        # Revenue Share Template
        revenue_share_template = ContractTemplate(
            id="revenue_share_template",
            name="Revenue Sharing Agreement",
            description="Revenue sharing agreement for content monetization",
            contract_type=ContractType.REVENUE_SHARE,
            template_content="""
            REVENUE SHARING AGREEMENT
            
            Agreement between {{platform_name}} and {{creator_name}}.
            
            REVENUE TERMS:
            - Creator Share: {{creator_percentage}}%
            - Platform Share: {{platform_percentage}}%
            - Minimum Payout: ${{minimum_payout}}
            - Payment Schedule: {{payment_schedule}}
            
            PERFORMANCE METRICS:
            - Target Revenue: ${{target_revenue}}
            - Performance Bonus: {{performance_bonus}}%
            
            Term: {{contract_duration}} months
            """,
            variables=[
                "platform_name", "creator_name", "creator_percentage",
                "platform_percentage", "minimum_payout", "payment_schedule",
                "target_revenue", "performance_bonus", "contract_duration"
            ],
            default_terms=[
                {"title": "Creator Revenue Share", "value": "70", "is_negotiable": True},
                {"title": "Minimum Payout", "value": "100", "is_negotiable": False},
                {"title": "Payment Schedule", "value": "Monthly", "is_negotiable": True}
            ],
            jurisdictions=["US", "EU"],
            created_by="system"
        )
        
        self.templates[revenue_share_template.id] = revenue_share_template
    
    async def create_contract(
        self,
        title: str,
        description: str,
        contract_type: ContractType,
        parties: List[Dict[str, Any]],
        terms: List[Dict[str, Any]],
        start_date: datetime,
        end_date: Optional[datetime] = None,
        template_id: Optional[str] = None,
        created_by: str = "",
        milestones: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Create a new contract"""
        try:
            contract_id = str(uuid.uuid4())
            
            # Create contract parties
            contract_parties = []
            for party_data in parties:
                party = ContractParty(
                    id=str(uuid.uuid4()),
                    name=party_data["name"],
                    email=party_data["email"],
                    role=party_data["role"]
                )
                contract_parties.append(party)
            
            # Create contract terms
            contract_terms = []
            for term_data in terms:
                term = ContractTerm(
                    id=str(uuid.uuid4()),
                    title=term_data["title"],
                    description=term_data.get("description", ""),
                    value=term_data["value"],
                    is_negotiable=term_data.get("is_negotiable", True)
                )
                contract_terms.append(term)
            
            # Create milestones if provided
            contract_milestones = []
            if milestones:
                for milestone_data in milestones:
                    milestone = ContractMilestone(
                        id=str(uuid.uuid4()),
                        title=milestone_data["title"],
                        description=milestone_data.get("description", ""),
                        due_date=datetime.fromisoformat(milestone_data["due_date"]),
                        deliverables=milestone_data.get("deliverables", []),
                        payment_amount=milestone_data.get("payment_amount", 0.0)
                    )
                    contract_milestones.append(milestone)
            
            # Generate contract document
            generated_document = await self._generate_contract_document(
                contract_type, template_id, {
                    "title": title,
                    "parties": parties,
                    "terms": terms,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat() if end_date else None
                }
            )
            
            contract = Contract(
                id=contract_id,
                title=title,
                description=description,
                contract_type=contract_type,
                status=ContractStatus.DRAFT,
                parties=contract_parties,
                terms=contract_terms,
                milestones=contract_milestones,
                start_date=start_date,
                end_date=end_date,
                template_id=template_id,
                generated_document=generated_document,
                created_by=created_by
            )
            
            self.contracts[contract_id] = contract
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"contract:{contract_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(contract), default=str)
                )
            
            self.logger.info(f"✅ Created contract {contract_id}: {title}")
            return contract_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating contract: {e}")
            raise
    
    async def _generate_contract_document(
        self,
        contract_type: ContractType,
        template_id: Optional[str],
        variables: Dict[str, Any]
    ) -> str:
        """Generate contract document from template"""
        try:
            # Get template
            template = None
            if template_id:
                template = self.templates.get(template_id)
            else:
                # Find default template for contract type
                for tmpl in self.templates.values():
                    if tmpl.contract_type == contract_type:
                        template = tmpl
                        break
            
            if not template:
                return f"Contract document for {contract_type.value} - Generated on {datetime.utcnow()}"
            
            # Render template
            jinja_template = Template(template.template_content)
            document = jinja_template.render(**variables)
            
            return document
            
        except Exception as e:
            self.logger.error(f"❌ Error generating contract document: {e}")
            return f"Error generating document: {e}"
    
    async def send_for_signature(self, contract_id: str, party_emails: List[str]) -> List[str]:
        """Send contract for digital signature"""
        try:
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            if contract.status != ContractStatus.DRAFT:
                raise ValueError(f"Contract must be in draft status to send for signature")
            
            signature_ids = []
            
            for email in party_emails:
                # Find party by email
                party = next((p for p in contract.parties if p.email == email), None)
                if not party:
                    self.logger.warning(f"Party with email {email} not found in contract")
                    continue
                
                # Generate signature ID
                signature_id = str(uuid.uuid4())
                signature_ids.append(signature_id)
                
                # Store signature mapping
                self.pending_signatures[signature_id] = contract_id
                
                # Update party status
                party.signature_status = SignatureStatus.PENDING
                
                self.logger.info(f"📧 Sent signature request to {email}")
            
            # Update contract status
            contract.status = ContractStatus.PENDING_SIGNATURE
            contract.updated_at = datetime.utcnow()
            
            return signature_ids
            
        except Exception as e:
            self.logger.error(f"❌ Error sending contract for signature: {e}")
            raise
    
    async def sign_contract(
        self,
        signature_id: str,
        party_email: str,
        digital_signature: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """Sign a contract digitally"""
        try:
            contract_id = self.pending_signatures.get(signature_id)
            if not contract_id:
                raise ValueError(f"Invalid signature ID: {signature_id}")
            
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            # Find party by email
            party = next((p for p in contract.parties if p.email == party_email), None)
            if not party:
                raise ValueError(f"Party with email {party_email} not found")
            
            # Update signature
            party.signature_status = SignatureStatus.SIGNED
            party.signed_at = datetime.utcnow()
            party.digital_signature = digital_signature
            party.ip_address = ip_address
            
            # Remove from pending signatures
            del self.pending_signatures[signature_id]
            
            # Check if all parties have signed
            all_signed = all(p.signature_status == SignatureStatus.SIGNED for p in contract.parties)
            
            if all_signed:
                contract.status = ContractStatus.ACTIVE
                contract.updated_at = datetime.utcnow()
                self.logger.info(f"✅ Contract {contract_id} is now active - all parties signed")
            
            self.logger.info(f"✅ Contract {contract_id} signed by {party_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error signing contract: {e}")
            return False
    
    async def negotiate_term(
        self,
        contract_id: str,
        term_id: str,
        new_value: Any,
        negotiated_by: str
    ) -> bool:
        """Negotiate a contract term"""
        try:
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            if contract.status not in [ContractStatus.DRAFT, ContractStatus.PENDING_REVIEW]:
                raise ValueError("Contract cannot be negotiated in current status")
            
            # Find term
            term = next((t for t in contract.terms if t.id == term_id), None)
            if not term:
                raise ValueError(f"Term {term_id} not found")
            
            if not term.is_negotiable:
                raise ValueError("Term is not negotiable")
            
            # Update term
            term.negotiated_value = new_value
            term.negotiated_by = negotiated_by
            term.negotiated_at = datetime.utcnow()
            
            # Update contract
            contract.status = ContractStatus.PENDING_REVIEW
            contract.updated_at = datetime.utcnow()
            
            self.logger.info(f"🔄 Term '{term.title}' negotiated in contract {contract_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error negotiating term: {e}")
            return False
    
    async def update_milestone_status(
        self,
        contract_id: str,
        milestone_id: str,
        status: str,
        completion_notes: Optional[str] = None
    ) -> bool:
        """Update milestone status"""
        try:
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            # Find milestone
            milestone = next((m for m in contract.milestones if m.id == milestone_id), None)
            if not milestone:
                raise ValueError(f"Milestone {milestone_id} not found")
            
            milestone.status = status
            if status == "completed":
                milestone.completed_at = datetime.utcnow()
            
            contract.updated_at = datetime.utcnow()
            
            self.logger.info(f"✅ Milestone '{milestone.title}' status updated to {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating milestone: {e}")
            return False
    
    async def terminate_contract(
        self,
        contract_id: str,
        reason: str,
        terminated_by: str
    ) -> bool:
        """Terminate an active contract"""
        try:
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            if contract.status != ContractStatus.ACTIVE:
                raise ValueError("Only active contracts can be terminated")
            
            contract.status = ContractStatus.TERMINATED
            contract.updated_at = datetime.utcnow()
            contract.metadata["termination"] = {
                "reason": reason,
                "terminated_by": terminated_by,
                "terminated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"🚫 Contract {contract_id} terminated by {terminated_by}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error terminating contract: {e}")
            return False
    
    async def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract details"""
        try:
            contract = self.contracts.get(contract_id)
            if contract:
                return asdict(contract)
            
            # Try Redis cache
            if self.redis_client:
                cached = await self.redis_client.get(f"contract:{contract_id}")
                if cached:
                    return json.loads(cached)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting contract: {e}")
            return None
    
    async def get_contracts_by_party(self, party_email: str) -> List[Dict[str, Any]]:
        """Get contracts for a specific party"""
        try:
            party_contracts = []
            
            for contract in self.contracts.values():
                if any(p.email == party_email for p in contract.parties):
                    party_contracts.append(asdict(contract))
            
            return party_contracts
            
        except Exception as e:
            self.logger.error(f"❌ Error getting contracts for party: {e}")
            return []
    
    async def _contract_monitor(self) -> None:
        """Monitor contract statuses and deadlines"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for contract in self.contracts.values():
                    # Check for expired contracts
                    if contract.end_date and contract.end_date <= current_time:
                        if contract.status == ContractStatus.ACTIVE:
                            if contract.auto_renew and contract.renewal_period:
                                # Auto-renew contract
                                contract.end_date = current_time + contract.renewal_period
                                self.logger.info(f"🔄 Auto-renewed contract {contract.id}")
                            else:
                                contract.status = ContractStatus.EXPIRED
                                self.logger.info(f"⏰ Contract {contract.id} expired")
                    
                    # Check milestone deadlines
                    for milestone in contract.milestones:
                        if (milestone.due_date <= current_time and 
                            milestone.status == "pending"):
                            milestone.status = "overdue"
                            self.logger.warning(f"⚠️ Milestone '{milestone.title}' is overdue")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in contract monitor: {e}")
                await asyncio.sleep(300)
    
    async def _analytics_collector(self) -> None:
        """Collect contract analytics"""
        while self.running:
            try:
                # Update analytics
                self.analytics.total_contracts = len(self.contracts)
                self.analytics.active_contracts = sum(
                    1 for c in self.contracts.values() if c.status == ContractStatus.ACTIVE
                )
                self.analytics.pending_signatures = len(self.pending_signatures)
                
                # Count by type
                self.analytics.contracts_by_type = {}
                for contract in self.contracts.values():
                    contract_type = contract.contract_type.value
                    if contract_type not in self.analytics.contracts_by_type:
                        self.analytics.contracts_by_type[contract_type] = 0
                    self.analytics.contracts_by_type[contract_type] += 1
                
                # Calculate revenue under contract
                self.analytics.revenue_under_contract = sum(
                    c.total_value for c in self.contracts.values() 
                    if c.status == ContractStatus.ACTIVE
                )
                
                # Store in Redis
                if self.redis_client:
                    await self.redis_client.setex(
                        "contract_management:analytics",
                        300,  # 5 minutes
                        json.dumps(asdict(self.analytics), default=str)
                    )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting analytics: {e}")
                await asyncio.sleep(60)
    
    async def _renewal_notifier(self) -> None:
        """Notify about upcoming contract renewals"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                notification_threshold = current_time + timedelta(days=30)
                
                for contract in self.contracts.values():
                    if (contract.status == ContractStatus.ACTIVE and 
                        contract.end_date and 
                        contract.end_date <= notification_threshold):
                        
                        self.logger.info(f"📅 Contract {contract.id} expires in 30 days")
                        # In real implementation, send notifications to parties
                
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                self.logger.error(f"❌ Error in renewal notifier: {e}")
                await asyncio.sleep(3600)
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get contract analytics"""
        return asdict(self.analytics)


# Example usage and testing
async def main() -> None:
    """Test the contract management service"""
    service = ContractManagementService()
    
    try:
        await service.start()
        
        # Create a collaboration contract
        contract_id = await service.create_contract(
            "Music Video Collaboration",
            "Collaboration between two creators for a music video project",
            ContractType.COLLABORATION,
            [
                {"name": "Creator A", "email": "creator.a@example.com", "role": "creator"},
                {"name": "Creator B", "email": "creator.b@example.com", "role": "collaborator"}
            ],
            [
                {"title": "Revenue Split", "value": "50/50", "is_negotiable": True},
                {"title": "Project Duration", "value": "30 days", "is_negotiable": True},
                {"title": "Content Ownership", "value": "Joint", "is_negotiable": False}
            ],
            datetime.utcnow(),
            datetime.utcnow() + timedelta(days=90),
            "collaboration_template",
            "system_admin",
            [
                {
                    "title": "Video Production",
                    "description": "Complete video production and editing",
                    "due_date": (datetime.utcnow() + timedelta(days=20)).isoformat(),
                    "deliverables": ["Raw footage", "Edited video"],
                    "payment_amount": 5000.0
                }
            ]
        )
        
        # Send for signature
        signature_ids = await service.send_for_signature(
            contract_id,
            ["creator.a@example.com", "creator.b@example.com"]
        )
        
        # Simulate signatures
        await service.sign_contract(
            signature_ids[0],
            "creator.a@example.com",
            "digital_signature_data_a",
            "192.168.1.1"
        )
        
        await service.sign_contract(
            signature_ids[1],
            "creator.b@example.com",
            "digital_signature_data_b",
            "192.168.1.2"
        )
        
        # Get contract details
        contract_details = await service.get_contract(contract_id)
        print(f"Contract Status: {contract_details['status']}")
        
        # Get analytics
        analytics = await service.get_analytics()
        print(f"Analytics: {analytics}")
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())