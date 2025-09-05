"""Legal Automation Engine

Automated legal action system for copyright enforcement and protection.
Handles DMCA takedowns, legal documentation, and automated enforcement processes.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import re

# Core imports
from .violation_monitoring_system import ViolationDetection, ViolationSeverity
from .ai_protection_orchestrator import ThreatLevel

logger = logging.getLogger(__name__)


class LegalActionType(Enum):
    """Types of legal actions"""
    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    COPYRIGHT_CLAIM = "copyright_claim"
    LAWSUIT_FILING = "lawsuit_filing"
    SETTLEMENT_NEGOTIATION = "settlement_negotiation"
    COURT_INJUNCTION = "court_injunction"
    CRIMINAL_COMPLAINT = "criminal_complaint"
    INTERNATIONAL_ENFORCEMENT = "international_enforcement"


class LegalDocumentType(Enum):
    """Types of legal documents"""
    DMCA_NOTICE = "dmca_notice"
    CEASE_DESIST_LETTER = "cease_desist_letter"
    COPYRIGHT_REGISTRATION = "copyright_registration"
    INFRINGEMENT_COMPLAINT = "infringement_complaint"
    SETTLEMENT_AGREEMENT = "settlement_agreement"
    COURT_FILING = "court_filing"
    EVIDENCE_PACKAGE = "evidence_package"
    AFFIDAVIT = "affidavit"


class LegalJurisdiction(Enum):
    """Legal jurisdictions"""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_GENERAL = "eu_general"
    UK_COURTS = "uk_courts"
    GERMAN_COURTS = "german_courts"
    FRENCH_COURTS = "french_courts"
    CANADIAN_COURTS = "canadian_courts"
    INTERNATIONAL = "international"


class EnforcementStrategy(Enum):
    """Enforcement strategies"""
    AGGRESSIVE = "aggressive"
    DIPLOMATIC = "diplomatic"
    ESCALATING = "escalating"
    SETTLEMENT_FOCUSED = "settlement_focused"
    MAXIMUM_DAMAGES = "maximum_damages"
    QUICK_RESOLUTION = "quick_resolution"


class LegalActionStatus(Enum):
    """Legal action status"""
    INITIATED = "initiated"
    PENDING = "pending"
    SERVED = "served"
    RESPONDED = "responded"
    SETTLED = "settled"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    APPEALED = "appealed"
    COMPLETED = "completed"


@dataclass
class LegalCase:
    """Legal case record"""
    case_id: str
    violation_id: str
    case_type: LegalActionType
    jurisdiction: LegalJurisdiction
    plaintiff_info: Dict[str, Any]
    defendant_info: Dict[str, Any]
    case_details: Dict[str, Any]
    documents: List[str]
    timeline: List[Dict[str, Any]]
    status: LegalActionStatus
    estimated_damages: float
    legal_costs: float
    success_probability: float
    created_date: datetime
    last_updated: datetime


@dataclass
class LegalDocument:
    """Legal document specification"""
    document_id: str
    document_type: LegalDocumentType
    case_id: str
    title: str
    content: str
    metadata: Dict[str, Any]
    generated_by: str
    reviewed_by: Optional[str]
    filed_date: Optional[datetime]
    effective_date: Optional[datetime]
    expiration_date: Optional[datetime]
    legal_validity: bool
    created_date: datetime


@dataclass
class DMCANotice:
    """DMCA takedown notice"""
    notice_id: str
    case_id: str
    copyright_owner: Dict[str, Any]
    authorized_agent: Dict[str, Any]
    infringing_urls: List[str]
    original_work_description: str
    infringement_description: str
    good_faith_statement: str
    accuracy_statement: str
    signature: str
    contact_information: Dict[str, Any]
    created_date: datetime
    served_date: Optional[datetime]
    response_deadline: datetime


@dataclass
class SettlementOffer:
    """Settlement offer specification"""
    offer_id: str
    case_id: str
    offering_party: str
    receiving_party: str
    settlement_amount: float
    terms_and_conditions: List[str]
    deadline: datetime
    acceptance_required: bool
    confidentiality_clause: bool
    non_admission_clause: bool
    future_compliance_terms: List[str]
    created_date: datetime


@dataclass
class LegalActionResult:
    """Legal action execution result"""
    action_id: str
    case_id: str
    action_type: LegalActionType
    success: bool
    documents_generated: List[str]
    actions_taken: List[str]
    costs_incurred: float
    timeline_impact: Dict[str, Any]
    next_steps: List[str]
    errors: List[str]
    execution_time: float
    created_date: datetime


class DMCAProcessor:
    """DMCA takedown processing engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.templates = self._load_dmca_templates()
        
    def _load_dmca_templates(self) -> Dict[str, str]:
        """Load DMCA notice templates"""
        return {
            'standard_notice': """
DMCA TAKEDOWN NOTICE

To: {service_provider}
From: {copyright_owner}
Date: {notice_date}

I, {owner_name}, am the copyright owner of the work(s) described below.

1. IDENTIFICATION OF COPYRIGHTED WORK:
{work_description}

2. IDENTIFICATION OF INFRINGING MATERIAL:
The following URLs contain material that infringes my copyright:
{infringing_urls}

3. CONTACT INFORMATION:
Name: {owner_name}
Address: {owner_address}
Phone: {owner_phone}
Email: {owner_email}

4. GOOD FAITH STATEMENT:
I have a good faith belief that use of the copyrighted materials described above on the allegedly infringing web pages is not authorized by the copyright owner, its agent, or the law.

5. ACCURACY STATEMENT:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.

Signature: {signature}
Date: {signature_date}
            """,
            
            'formal_notice': """
FORMAL DMCA TAKEDOWN NOTICE
(Digital Millennium Copyright Act - 17 U.S.C. § 512)

TO: {service_provider_legal_name}
ATTENTION: DMCA Designated Agent
{service_provider_address}

FROM: {copyright_owner_legal_name}
{copyright_owner_address}

DATE: {formal_date}

SUBJECT: Notice of Infringement under Digital Millennium Copyright Act

Dear Sir or Madam:

This is a formal notice of infringement under the Digital Millennium Copyright Act (DMCA), 17 U.S.C. § 512, served upon you as the designated agent for {service_provider_legal_name}.

1. IDENTIFICATION OF COPYRIGHTED WORK CLAIMED TO HAVE BEEN INFRINGED:
{detailed_work_description}
Registration Number: {copyright_registration}
Date of Creation: {creation_date}
Date of Publication: {publication_date}

2. IDENTIFICATION OF MATERIAL CLAIMED TO BE INFRINGING:
{detailed_infringement_description}

Infringing URLs:
{formatted_infringing_urls}

3. INFORMATION SUFFICIENT TO PERMIT CONTACT OF COMPLAINING PARTY:
{complete_contact_information}

4. GOOD FAITH BELIEF STATEMENT:
I have a good faith belief that use of the copyrighted materials described above on the allegedly infringing web pages is not authorized by the copyright owner, its agent, or the law. I have taken fair use into consideration in my analysis.

5. ACCURACY AND AUTHORITY STATEMENT:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner, or am authorized to act on behalf of the owner, of an exclusive right that is allegedly infringed.

6. ELECTRONIC SIGNATURE:
{electronic_signature}

Respectfully submitted,
{authorized_signature}
{title}
{date_of_service}

NOTICE: This communication may contain attorney-client privileged information. If you have received this in error, please notify the sender immediately and delete all copies.
            """
        }
    
    async def generate_dmca_notice(self, violation: ViolationDetection, 
                                 copyright_owner: Dict[str, Any],
                                 case_details: Dict[str, Any]) -> DMCANotice:
        """Generate DMCA takedown notice"""
        try:
            notice_id = str(uuid.uuid4())
            case_id = case_details.get('case_id', str(uuid.uuid4()))
            
            # Determine service provider from URL
            service_provider = self._identify_service_provider(violation.detected_url)
            
            # Generate notice content
            template_type = case_details.get('template_type', 'standard_notice')
            template = self.templates.get(template_type, self.templates['standard_notice'])
            
            notice_content = self._populate_dmca_template(
                template, violation, copyright_owner, service_provider, case_details
            )
            
            dmca_notice = DMCANotice(
                notice_id=notice_id,
                case_id=case_id,
                copyright_owner=copyright_owner,
                authorized_agent=case_details.get('authorized_agent', copyright_owner),
                infringing_urls=[violation.detected_url],
                original_work_description=case_details.get('work_description', ''),
                infringement_description=self._generate_infringement_description(violation),
                good_faith_statement="I have a good faith belief that use of the copyrighted materials described above is not authorized by the copyright owner, its agent, or the law.",
                accuracy_statement="I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner.",
                signature=case_details.get('signature', copyright_owner.get('name', '')),
                contact_information=copyright_owner,
                created_date=datetime.utcnow(),
                served_date=None,
                response_deadline=datetime.utcnow() + timedelta(days=14)
            )
            
            return dmca_notice
            
        except Exception as e:
            logger.error(f"DMCA notice generation failed: {e}")
            raise
    
    def _identify_service_provider(self, url: str) -> Dict[str, Any]:
        """Identify service provider from URL"""
        domain = re.findall(r'://([^/]+)', url)
        if domain:
            domain = domain[0].lower()
            
            # Known service providers
            providers = {
                'youtube.com': {
                    'name': 'YouTube LLC',
                    'legal_name': 'Google LLC',
                    'dmca_agent': 'copyright@youtube.com',
                    'address': '901 Cherry Ave, San Bruno, CA 94066'
                },
                'facebook.com': {
                    'name': 'Facebook Inc.',
                    'legal_name': 'Meta Platforms Inc.',
                    'dmca_agent': 'ip@fb.com',
                    'address': '1601 Willow Road, Menlo Park, CA 94025'
                },
                'instagram.com': {
                    'name': 'Instagram LLC',
                    'legal_name': 'Meta Platforms Inc.',
                    'dmca_agent': 'ip@fb.com',
                    'address': '1601 Willow Road, Menlo Park, CA 94025'
                },
                'twitter.com': {
                    'name': 'Twitter Inc.',
                    'legal_name': 'X Corp.',
                    'dmca_agent': 'copyright@twitter.com',
                    'address': '1355 Market Street, Suite 900, San Francisco, CA 94103'
                }
            }
            
            for provider_domain, info in providers.items():
                if provider_domain in domain:
                    return info
        
        # Default provider info
        return {
            'name': 'Service Provider',
            'legal_name': 'Unknown Service Provider',
            'dmca_agent': 'dmca@example.com',
            'address': 'Unknown Address'
        }
    
    def _populate_dmca_template(self, template: str, violation: ViolationDetection,
                              copyright_owner: Dict[str, Any], service_provider: Dict[str, Any],
                              case_details: Dict[str, Any]) -> str:
        """Populate DMCA template with case data"""
        
        current_date = datetime.utcnow()
        
        template_vars = {
            'service_provider': service_provider.get('name', 'Service Provider'),
            'service_provider_legal_name': service_provider.get('legal_name', 'Service Provider'),
            'service_provider_address': service_provider.get('address', 'Unknown Address'),
            'copyright_owner': copyright_owner.get('name', 'Copyright Owner'),
            'copyright_owner_legal_name': copyright_owner.get('legal_name', copyright_owner.get('name', '')),
            'copyright_owner_address': copyright_owner.get('address', ''),
            'owner_name': copyright_owner.get('name', ''),
            'owner_address': copyright_owner.get('address', ''),
            'owner_phone': copyright_owner.get('phone', ''),
            'owner_email': copyright_owner.get('email', ''),
            'notice_date': current_date.strftime('%B %d, %Y'),
            'formal_date': current_date.strftime('%B %d, %Y'),
            'signature_date': current_date.strftime('%B %d, %Y'),
            'date_of_service': current_date.strftime('%B %d, %Y'),
            'work_description': case_details.get('work_description', 'Copyrighted work'),
            'detailed_work_description': case_details.get('detailed_work_description', case_details.get('work_description', '')),
            'infringement_description': self._generate_infringement_description(violation),
            'detailed_infringement_description': self._generate_detailed_infringement_description(violation),
            'infringing_urls': violation.detected_url,
            'formatted_infringing_urls': f"- {violation.detected_url}",
            'copyright_registration': case_details.get('copyright_registration', 'Pending'),
            'creation_date': case_details.get('creation_date', 'Unknown'),
            'publication_date': case_details.get('publication_date', 'Unknown'),
            'complete_contact_information': self._format_contact_information(copyright_owner),
            'signature': case_details.get('signature', copyright_owner.get('name', '')),
            'electronic_signature': f"/s/ {copyright_owner.get('name', '')}",
            'authorized_signature': copyright_owner.get('name', ''),
            'title': copyright_owner.get('title', 'Copyright Owner')
        }
        
        # Replace template variables
        populated_template = template
        for key, value in template_vars.items():
            populated_template = populated_template.replace(f'{{{key}}}', str(value))
        
        return populated_template
    
    def _generate_infringement_description(self, violation: ViolationDetection) -> str:
        """Generate infringement description"""
        return f"Unauthorized reproduction and distribution of copyrighted material detected at {violation.detected_url} with {violation.confidence_score:.2%} confidence."
    
    def _generate_detailed_infringement_description(self, violation: ViolationDetection) -> str:
        """Generate detailed infringement description"""
        description = f"""
The infringing material located at {violation.detected_url} contains unauthorized copies of the copyright-protected work. 

Violation Details:
- Detection Method: {violation.detection_method}
- Confidence Score: {violation.confidence_score:.2%}
- Violation Type: {violation.violation_type.value}
- Severity: {violation.severity.value}
- Detection Date: {violation.detection_timestamp.strftime('%B %d, %Y at %I:%M %p UTC')}

The infringing use is not authorized by the copyright owner, its agent, or the law, and does not fall under fair use or any other exception.
        """
        
        return description.strip()
    
    def _format_contact_information(self, copyright_owner: Dict[str, Any]) -> str:
        """Format complete contact information"""
        info_parts = []
        
        if copyright_owner.get('name'):
            info_parts.append(f"Name: {copyright_owner['name']}")
        if copyright_owner.get('title'):
            info_parts.append(f"Title: {copyright_owner['title']}")
        if copyright_owner.get('company'):
            info_parts.append(f"Company: {copyright_owner['company']}")
        if copyright_owner.get('address'):
            info_parts.append(f"Address: {copyright_owner['address']}")
        if copyright_owner.get('phone'):
            info_parts.append(f"Phone: {copyright_owner['phone']}")
        if copyright_owner.get('email'):
            info_parts.append(f"Email: {copyright_owner['email']}")
        
        return '\n'.join(info_parts)
    
    async def submit_dmca_notice(self, dmca_notice: DMCANotice) -> bool:
        """Submit DMCA notice to service provider"""
        try:
            # In production, this would actually submit the notice
            # For now, we simulate successful submission
            
            logger.info(f"DMCA notice {dmca_notice.notice_id} submitted for case {dmca_notice.case_id}")
            
            # Update served date
            dmca_notice.served_date = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"DMCA notice submission failed: {e}")
            return False


class LegalDocumentGenerator:
    """Legal document generation engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.templates = self._load_document_templates()
    
    def _load_document_templates(self) -> Dict[str, str]:
        """Load legal document templates"""
        return {
            'cease_desist': """
CEASE AND DESIST LETTER

{date}

{recipient_name}
{recipient_address}

Re: Copyright Infringement - Demand for Immediate Cessation

Dear {recipient_salutation}:

I am writing on behalf of {client_name}, the exclusive owner of copyrights in {work_description} (the "Work").

It has come to our attention that you are using, reproducing, and/or distributing the Work without authorization. Specifically, the infringing material can be found at: {infringing_location}

This unauthorized use constitutes copyright infringement under federal law, specifically 17 U.S.C. § 501 et seq. Your actions have caused and continue to cause substantial harm to our client.

DEMAND FOR IMMEDIATE CESSATION:
We hereby demand that you:
1. Immediately cease and desist from all unauthorized use of the Work
2. Remove all infringing material from your platforms
3. Provide written confirmation of compliance within 10 days
4. Preserve all records related to the infringement

LEGAL CONSEQUENCES:
If you fail to comply with this demand, our client will pursue all available legal remedies, including but not limited to:
- Filing a federal copyright infringement lawsuit
- Seeking monetary damages up to $150,000 per work infringed
- Recovering attorney's fees and costs
- Obtaining injunctive relief

This letter serves as formal notice of the infringement and our client's intent to protect their rights.

Sincerely,

{attorney_signature}
{attorney_name}
{attorney_title}
{law_firm_name}
            """,
            
            'settlement_agreement': """
SETTLEMENT AGREEMENT AND RELEASE

This Settlement Agreement and Release ("Agreement") is entered into on {date} by and between {plaintiff_name} ("Plaintiff") and {defendant_name} ("Defendant").

RECITALS:
WHEREAS, Plaintiff alleges copyright infringement by Defendant;
WHEREAS, Defendant denies liability but wishes to resolve this matter;
WHEREAS, the parties desire to settle all claims without admission of wrongdoing;

NOW, THEREFORE, the parties agree as follows:

1. SETTLEMENT PAYMENT:
Defendant shall pay Plaintiff the sum of ${settlement_amount} within {payment_terms}.

2. CESSATION OF INFRINGEMENT:
Defendant agrees to immediately cease all unauthorized use of Plaintiff's copyrighted works.

3. FUTURE COMPLIANCE:
Defendant agrees to implement procedures to prevent future infringement.

4. RELEASE:
Upon payment, Plaintiff releases all claims against Defendant related to this matter.

5. NON-ADMISSION:
This agreement shall not constitute an admission of liability by any party.

6. CONFIDENTIALITY:
{confidentiality_clause}

7. GOVERNING LAW:
This Agreement shall be governed by the laws of {governing_jurisdiction}.

IN WITNESS WHEREOF, the parties execute this Agreement.

{plaintiff_signature}          {defendant_signature}
{plaintiff_name}               {defendant_name}
Date: ___________              Date: ___________
            """
        }
    
    async def generate_document(self, document_type: LegalDocumentType,
                              case: LegalCase, additional_data: Dict[str, Any]) -> LegalDocument:
        """Generate legal document"""
        try:
            document_id = str(uuid.uuid4())
            
            # Select appropriate template
            template_key = document_type.value
            if template_key not in self.templates:
                raise ValueError(f"No template found for document type: {document_type}")
            
            template = self.templates[template_key]
            
            # Generate document content
            content = await self._populate_document_template(
                template, case, additional_data, document_type
            )
            
            # Generate title
            title = self._generate_document_title(document_type, case)
            
            document = LegalDocument(
                document_id=document_id,
                document_type=document_type,
                case_id=case.case_id,
                title=title,
                content=content,
                metadata={
                    'case_type': case.case_type.value,
                    'jurisdiction': case.jurisdiction.value,
                    'template_used': template_key,
                    'generated_automatically': True
                },
                generated_by='LegalAutomationEngine',
                reviewed_by=None,
                filed_date=None,
                effective_date=datetime.utcnow(),
                expiration_date=None,
                legal_validity=True,
                created_date=datetime.utcnow()
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            raise
    
    async def _populate_document_template(self, template: str, case: LegalCase,
                                        additional_data: Dict[str, Any],
                                        document_type: LegalDocumentType) -> str:
        """Populate document template with case data"""
        
        current_date = datetime.utcnow()
        
        # Extract case information
        plaintiff_info = case.plaintiff_info
        defendant_info = case.defendant_info
        case_details = case.case_details
        
        template_vars = {
            'date': current_date.strftime('%B %d, %Y'),
            'client_name': plaintiff_info.get('name', 'Client'),
            'plaintiff_name': plaintiff_info.get('legal_name', plaintiff_info.get('name', '')),
            'defendant_name': defendant_info.get('legal_name', defendant_info.get('name', 'Defendant')),
            'recipient_name': defendant_info.get('name', 'Recipient'),
            'recipient_address': defendant_info.get('address', 'Unknown Address'),
            'recipient_salutation': defendant_info.get('salutation', 'Sir/Madam'),
            'work_description': case_details.get('work_description', 'copyrighted work'),
            'infringing_location': case_details.get('infringing_url', 'unknown location'),
            'attorney_name': additional_data.get('attorney_name', 'Legal Representative'),
            'attorney_title': additional_data.get('attorney_title', 'Attorney'),
            'attorney_signature': additional_data.get('attorney_signature', '/s/ Legal Representative'),
            'law_firm_name': additional_data.get('law_firm_name', 'Legal Firm'),
            'settlement_amount': f"{case.estimated_damages:,.2f}",
            'payment_terms': additional_data.get('payment_terms', '30 days'),
            'confidentiality_clause': additional_data.get('confidentiality_clause', 'The terms of this agreement shall remain confidential.'),
            'governing_jurisdiction': case.jurisdiction.value.replace('_', ' ').title(),
            'plaintiff_signature': f"/s/ {plaintiff_info.get('name', '')}",
            'defendant_signature': '[Defendant Signature Required]'
        }
        
        # Replace template variables
        populated_template = template
        for key, value in template_vars.items():
            populated_template = populated_template.replace(f'{{{key}}}', str(value))
        
        return populated_template
    
    def _generate_document_title(self, document_type: LegalDocumentType, case: LegalCase) -> str:
        """Generate document title"""
        titles = {
            LegalDocumentType.DMCA_NOTICE: f"DMCA Takedown Notice - Case {case.case_id[:8]}",
            LegalDocumentType.CEASE_DESIST_LETTER: f"Cease and Desist Letter - {case.defendant_info.get('name', 'Defendant')}",
            LegalDocumentType.COPYRIGHT_REGISTRATION: f"Copyright Registration Application - {case.case_details.get('work_title', 'Work')}",
            LegalDocumentType.INFRINGEMENT_COMPLAINT: f"Copyright Infringement Complaint - Case {case.case_id[:8]}",
            LegalDocumentType.SETTLEMENT_AGREEMENT: f"Settlement Agreement - {case.plaintiff_info.get('name', 'Plaintiff')} v. {case.defendant_info.get('name', 'Defendant')}",
            LegalDocumentType.COURT_FILING: f"Court Filing - Case {case.case_id[:8]}",
            LegalDocumentType.EVIDENCE_PACKAGE: f"Evidence Package - Case {case.case_id[:8]}",
            LegalDocumentType.AFFIDAVIT: f"Affidavit of Copyright Ownership - Case {case.case_id[:8]}"
        }
        
        return titles.get(document_type, f"Legal Document - Case {case.case_id[:8]}")


class SettlementNegotiator:
    """Automated settlement negotiation engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.negotiation_strategies = self._load_negotiation_strategies()
    
    def _load_negotiation_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Load negotiation strategies"""
        return {
            'aggressive': {
                'initial_demand_multiplier': 3.0,
                'minimum_settlement_ratio': 0.7,
                'escalation_threshold': 0.3,
                'negotiation_rounds': 3,
                'deadline_pressure': True
            },
            'diplomatic': {
                'initial_demand_multiplier': 1.5,
                'minimum_settlement_ratio': 0.4,
                'escalation_threshold': 0.6,
                'negotiation_rounds': 5,
                'deadline_pressure': False
            },
            'quick_resolution': {
                'initial_demand_multiplier': 1.2,
                'minimum_settlement_ratio': 0.3,
                'escalation_threshold': 0.8,
                'negotiation_rounds': 2,
                'deadline_pressure': True
            }
        }
    
    async def initiate_settlement_negotiation(self, case: LegalCase, 
                                            strategy: EnforcementStrategy) -> SettlementOffer:
        """Initiate automated settlement negotiation"""
        try:
            offer_id = str(uuid.uuid4())
            
            # Select negotiation strategy
            strategy_name = strategy.value if strategy.value in self.negotiation_strategies else 'diplomatic'
            strategy_config = self.negotiation_strategies[strategy_name]
            
            # Calculate settlement amount
            base_damages = case.estimated_damages
            initial_multiplier = strategy_config['initial_demand_multiplier']
            settlement_amount = base_damages * initial_multiplier
            
            # Generate terms and conditions
            terms = self._generate_settlement_terms(case, strategy_config)
            
            # Calculate deadline
            deadline_days = 14 if strategy_config['deadline_pressure'] else 30
            deadline = datetime.utcnow() + timedelta(days=deadline_days)
            
            settlement_offer = SettlementOffer(
                offer_id=offer_id,
                case_id=case.case_id,
                offering_party=case.plaintiff_info.get('name', 'Plaintiff'),
                receiving_party=case.defendant_info.get('name', 'Defendant'),
                settlement_amount=settlement_amount,
                terms_and_conditions=terms,
                deadline=deadline,
                acceptance_required=True,
                confidentiality_clause=True,
                non_admission_clause=True,
                future_compliance_terms=self._generate_compliance_terms(case),
                created_date=datetime.utcnow()
            )
            
            return settlement_offer
            
        except Exception as e:
            logger.error(f"Settlement negotiation initiation failed: {e}")
            raise
    
    def _generate_settlement_terms(self, case: LegalCase, strategy_config: Dict[str, Any]) -> List[str]:
        """Generate settlement terms and conditions"""
        terms = [
            "Payment of the settlement amount within 30 days of agreement execution",
            "Immediate cessation of all infringing activities",
            "Removal of all infringing material from defendant's platforms",
            "Acknowledgment of plaintiff's copyright ownership",
            "Agreement not to challenge the validity of plaintiff's copyrights"
        ]
        
        # Add strategy-specific terms
        if strategy_config.get('deadline_pressure'):
            terms.append("Time is of the essence - failure to respond by deadline constitutes rejection")
        
        if case.estimated_damages > 10000:
            terms.append("Payment plan options available for amounts over $10,000")
        
        return terms
    
    def _generate_compliance_terms(self, case: LegalCase) -> List[str]:
        """Generate future compliance terms"""
        return [
            "Implementation of copyright compliance procedures",
            "Regular audits of content usage practices",
            "Staff training on copyright law and fair use",
            "Immediate notification of any potential future infringement claims",
            "Cooperation with ongoing monitoring of compliance"
        ]
    
    async def evaluate_counter_offer(self, original_offer: SettlementOffer,
                                   counter_offer_amount: float,
                                   counter_terms: List[str]) -> Dict[str, Any]:
        """Evaluate counter offer using AI decision making"""
        try:
            original_amount = original_offer.settlement_amount
            reduction_percentage = (original_amount - counter_offer_amount) / original_amount
            
            # Get strategy for the case
            strategy_name = 'diplomatic'  # Default strategy
            strategy_config = self.negotiation_strategies[strategy_name]
            
            minimum_ratio = strategy_config['minimum_settlement_ratio']
            minimum_acceptable = original_amount * minimum_ratio
            
            evaluation = {
                'counter_offer_id': str(uuid.uuid4()),
                'original_amount': original_amount,
                'counter_amount': counter_offer_amount,
                'reduction_percentage': reduction_percentage,
                'minimum_acceptable': minimum_acceptable,
                'recommendation': 'reject',
                'reasoning': '',
                'next_offer_amount': 0.0,
                'continue_negotiation': False
            }
            
            if counter_offer_amount >= minimum_acceptable:
                evaluation['recommendation'] = 'accept'
                evaluation['reasoning'] = f"Counter offer meets minimum threshold ({minimum_ratio:.1%} of original)"
                evaluation['continue_negotiation'] = False
            elif reduction_percentage < 0.5:  # Less than 50% reduction
                # Make counter-counter offer
                evaluation['recommendation'] = 'counter'
                evaluation['reasoning'] = "Counter offer reasonable but below minimum - negotiate further"
                evaluation['next_offer_amount'] = (counter_offer_amount + minimum_acceptable) / 2
                evaluation['continue_negotiation'] = True
            else:
                evaluation['recommendation'] = 'reject'
                evaluation['reasoning'] = "Counter offer too low - exceeds acceptable reduction threshold"
                evaluation['continue_negotiation'] = False
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Counter offer evaluation failed: {e}")
            raise


class LegalAutomationEngine:
    """
    Comprehensive Legal Automation Engine
    
    Provides automated legal action capabilities including DMCA takedowns,
    legal document generation, settlement negotiation, and court filing automation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize legal automation engine"""
        self.config = config or {}
        
        # Core components
        self.dmca_processor = DMCAProcessor(self.config.get('dmca', {}))
        self.document_generator = LegalDocumentGenerator(self.config.get('documents', {}))
        self.settlement_negotiator = SettlementNegotiator(self.config.get('settlement', {}))
        
        # Case management
        self.active_cases: Dict[str, LegalCase] = {}
        self.case_documents: Dict[str, List[LegalDocument]] = {}
        self.settlement_offers: Dict[str, SettlementOffer] = {}
        
        # Performance tracking
        self.automation_metrics: Dict[str, Any] = {}
        self.action_history: List[Dict[str, Any]] = {}
        
        logger.info("Legal Automation Engine initialized")
    
    async def initiate_legal_action(self, violation: ViolationDetection,
                                  action_type: LegalActionType,
                                  copyright_owner: Dict[str, Any],
                                  enforcement_strategy: EnforcementStrategy = EnforcementStrategy.DIPLOMATIC) -> LegalActionResult:
        """Initiate automated legal action"""
        try:
            start_time = time.time()
            case_id = str(uuid.uuid4())
            action_id = str(uuid.uuid4())
            
            # Create legal case
            legal_case = await self._create_legal_case(
                case_id, violation, action_type, copyright_owner, enforcement_strategy
            )
            
            # Store case
            self.active_cases[case_id] = legal_case
            self.case_documents[case_id] = []
            
            # Execute action-specific workflows
            documents_generated = []
            actions_taken = []
            costs_incurred = 0.0
            errors = []
            
            try:
                if action_type == LegalActionType.DMCA_TAKEDOWN:
                    result = await self._execute_dmca_takedown(legal_case, violation)
                    documents_generated.extend(result.get('documents', []))
                    actions_taken.extend(result.get('actions', []))
                    costs_incurred += result.get('costs', 0.0)
                    
                elif action_type == LegalActionType.CEASE_DESIST:
                    result = await self._execute_cease_desist(legal_case)
                    documents_generated.extend(result.get('documents', []))
                    actions_taken.extend(result.get('actions', []))
                    costs_incurred += result.get('costs', 0.0)
                    
                elif action_type == LegalActionType.SETTLEMENT_NEGOTIATION:
                    result = await self._execute_settlement_negotiation(legal_case, enforcement_strategy)
                    documents_generated.extend(result.get('documents', []))
                    actions_taken.extend(result.get('actions', []))
                    costs_incurred += result.get('costs', 0.0)
                    
                elif action_type == LegalActionType.LAWSUIT_FILING:
                    result = await self._execute_lawsuit_filing(legal_case)
                    documents_generated.extend(result.get('documents', []))
                    actions_taken.extend(result.get('actions', []))
                    costs_incurred += result.get('costs', 0.0)
                    
                else:
                    errors.append(f"Unsupported action type: {action_type}")
                
                # Update case status
                legal_case.status = LegalActionStatus.INITIATED if not errors else LegalActionStatus.FAILED
                legal_case.legal_costs += costs_incurred
                legal_case.last_updated = datetime.utcnow()
                
                # Generate next steps
                next_steps = self._generate_next_steps(legal_case, action_type, enforcement_strategy)
                
                action_result = LegalActionResult(
                    action_id=action_id,
                    case_id=case_id,
                    action_type=action_type,
                    success=len(errors) == 0,
                    documents_generated=documents_generated,
                    actions_taken=actions_taken,
                    costs_incurred=costs_incurred,
                    timeline_impact={
                        'estimated_resolution_days': self._estimate_resolution_time(action_type, enforcement_strategy),
                        'next_action_date': (datetime.utcnow() + timedelta(days=14)).isoformat()
                    },
                    next_steps=next_steps,
                    errors=errors,
                    execution_time=time.time() - start_time,
                    created_date=datetime.utcnow()
                )
                
                # Update metrics
                await self._update_automation_metrics(action_result)
                
                return action_result
                
            except Exception as action_error:
                errors.append(str(action_error))
                legal_case.status = LegalActionStatus.FAILED
                
                return LegalActionResult(
                    action_id=action_id,
                    case_id=case_id,
                    action_type=action_type,
                    success=False,
                    documents_generated=[],
                    actions_taken=[],
                    costs_incurred=0.0,
                    timeline_impact={},
                    next_steps=['Review and manual intervention required'],
                    errors=errors,
                    execution_time=time.time() - start_time,
                    created_date=datetime.utcnow()
                )
                
        except Exception as e:
            logger.error(f"Legal action initiation failed: {e}")
            raise
    
    async def _create_legal_case(self, case_id: str, violation: ViolationDetection,
                               action_type: LegalActionType, copyright_owner: Dict[str, Any],
                               enforcement_strategy: EnforcementStrategy) -> LegalCase:
        """Create legal case record"""
        
        # Determine jurisdiction
        jurisdiction = self._determine_jurisdiction(violation, copyright_owner)
        
        # Extract defendant information from violation
        defendant_info = self._extract_defendant_info(violation)
        
        # Calculate estimated damages
        estimated_damages = self._calculate_estimated_damages(violation, action_type)
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(violation, action_type, jurisdiction)
        
        legal_case = LegalCase(
            case_id=case_id,
            violation_id=violation.violation_id,
            case_type=action_type,
            jurisdiction=jurisdiction,
            plaintiff_info=copyright_owner,
            defendant_info=defendant_info,
            case_details={
                'violation_url': violation.detected_url,
                'violation_type': violation.violation_type.value,
                'confidence_score': violation.confidence_score,
                'detection_method': violation.detection_method,
                'work_description': 'Copyrighted multimedia content',
                'infringement_analysis': violation.evidence
            },
            documents=[],
            timeline=[{
                'event': 'Case Created',
                'date': datetime.utcnow().isoformat(),
                'description': f'Legal case created for {action_type.value}'
            }],
            status=LegalActionStatus.INITIATED,
            estimated_damages=estimated_damages,
            legal_costs=0.0,
            success_probability=success_probability,
            created_date=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        return legal_case
    
    def _determine_jurisdiction(self, violation: ViolationDetection, 
                              copyright_owner: Dict[str, Any]) -> LegalJurisdiction:
        """Determine appropriate legal jurisdiction"""
        
        # Default to owner's jurisdiction
        owner_country = copyright_owner.get('country', 'US').upper()
        
        jurisdiction_mapping = {
            'US': LegalJurisdiction.US_FEDERAL,
            'DE': LegalJurisdiction.GERMAN_COURTS,
            'FR': LegalJurisdiction.FRENCH_COURTS,
            'UK': LegalJurisdiction.UK_COURTS,
            'CA': LegalJurisdiction.CANADIAN_COURTS
        }
        
        return jurisdiction_mapping.get(owner_country, LegalJurisdiction.INTERNATIONAL)
    
    def _extract_defendant_info(self, violation: ViolationDetection) -> Dict[str, Any]:
        """Extract defendant information from violation"""
        
        # Extract domain from URL
        domain_match = re.search(r'://([^/]+)', violation.detected_url)
        domain = domain_match.group(1) if domain_match else 'unknown'
        
        return {
            'name': f'Operator of {domain}',
            'legal_name': f'Unknown Entity operating {domain}',
            'platform': violation.platform_id,
            'infringing_url': violation.detected_url,
            'contact_method': 'platform_support',
            'address': 'To be determined through discovery',
            'salutation': 'To Whom It May Concern'
        }
    
    def _calculate_estimated_damages(self, violation: ViolationDetection, 
                                   action_type: LegalActionType) -> float:
        """Calculate estimated damages for the case"""
        
        # Base damages by violation severity
        base_damages_by_severity = {
            ViolationSeverity.INFORMATIONAL: 500.0,
            ViolationSeverity.LOW: 1500.0,
            ViolationSeverity.MEDIUM: 5000.0,
            ViolationSeverity.HIGH: 15000.0,
            ViolationSeverity.CRITICAL: 50000.0,
            ViolationSeverity.EMERGENCY: 150000.0
        }
        
        base_damages = base_damages_by_severity.get(violation.severity, 5000.0)
        
        # Adjust by confidence score
        confidence_multiplier = 0.5 + (violation.confidence_score * 0.5)
        adjusted_damages = base_damages * confidence_multiplier
        
        # Adjust by action type
        action_multipliers = {
            LegalActionType.DMCA_TAKEDOWN: 0.3,
            LegalActionType.CEASE_DESIST: 0.5,
            LegalActionType.COPYRIGHT_CLAIM: 0.7,
            LegalActionType.SETTLEMENT_NEGOTIATION: 0.8,
            LegalActionType.LAWSUIT_FILING: 1.0,
            LegalActionType.COURT_INJUNCTION: 1.2
        }
        
        action_multiplier = action_multipliers.get(action_type, 1.0)
        final_damages = adjusted_damages * action_multiplier
        
        return round(final_damages, 2)
    
    def _calculate_success_probability(self, violation: ViolationDetection,
                                     action_type: LegalActionType,
                                     jurisdiction: LegalJurisdiction) -> float:
        """Calculate probability of successful legal action"""
        
        # Base probability by confidence score
        base_probability = violation.confidence_score * 0.8
        
        # Adjust by action type complexity
        action_success_rates = {
            LegalActionType.DMCA_TAKEDOWN: 0.95,
            LegalActionType.CEASE_DESIST: 0.85,
            LegalActionType.COPYRIGHT_CLAIM: 0.75,
            LegalActionType.SETTLEMENT_NEGOTIATION: 0.70,
            LegalActionType.LAWSUIT_FILING: 0.60,
            LegalActionType.COURT_INJUNCTION: 0.50
        }
        
        action_rate = action_success_rates.get(action_type, 0.60)
        
        # Adjust by jurisdiction
        jurisdiction_factors = {
            LegalJurisdiction.US_FEDERAL: 1.0,
            LegalJurisdiction.EU_GENERAL: 0.9,
            LegalJurisdiction.UK_COURTS: 0.9,
            LegalJurisdiction.GERMAN_COURTS: 0.85,
            LegalJurisdiction.INTERNATIONAL: 0.7
        }
        
        jurisdiction_factor = jurisdiction_factors.get(jurisdiction, 0.7)
        
        final_probability = min(0.95, base_probability * action_rate * jurisdiction_factor)
        
        return round(final_probability, 3)
    
    async def _execute_dmca_takedown(self, case: LegalCase, violation: ViolationDetection) -> Dict[str, Any]:
        """Execute DMCA takedown process"""
        try:
            result = {
                'documents': [],
                'actions': [],
                'costs': 0.0
            }
            
            # Generate DMCA notice
            dmca_notice = await self.dmca_processor.generate_dmca_notice(
                violation, case.plaintiff_info, case.case_details
            )
            
            # Create legal document record
            dmca_document = LegalDocument(
                document_id=str(uuid.uuid4()),
                document_type=LegalDocumentType.DMCA_NOTICE,
                case_id=case.case_id,
                title=f"DMCA Takedown Notice - {case.case_id[:8]}",
                content=f"DMCA Notice {dmca_notice.notice_id}",
                metadata={'notice_id': dmca_notice.notice_id},
                generated_by='DMCAProcessor',
                reviewed_by=None,
                filed_date=None,
                effective_date=datetime.utcnow(),
                expiration_date=dmca_notice.response_deadline,
                legal_validity=True,
                created_date=datetime.utcnow()
            )
            
            # Store document
            self.case_documents[case.case_id].append(dmca_document)
            result['documents'].append(dmca_document.document_id)
            
            # Submit DMCA notice
            submission_success = await self.dmca_processor.submit_dmca_notice(dmca_notice)
            
            if submission_success:
                result['actions'].append('dmca_notice_submitted')
                case.timeline.append({
                    'event': 'DMCA Notice Submitted',
                    'date': datetime.utcnow().isoformat(),
                    'description': f'DMCA notice {dmca_notice.notice_id} submitted to platform'
                })
            else:
                result['actions'].append('dmca_notice_failed')
            
            # Minimal cost for automated DMCA
            result['costs'] = 50.0
            
            return result
            
        except Exception as e:
            logger.error(f"DMCA takedown execution failed: {e}")
            raise
    
    async def _execute_cease_desist(self, case: LegalCase) -> Dict[str, Any]:
        """Execute cease and desist process"""
        try:
            result = {
                'documents': [],
                'actions': [],
                'costs': 0.0
            }
            
            # Generate cease and desist letter
            cease_desist_document = await self.document_generator.generate_document(
                LegalDocumentType.CEASE_DESIST_LETTER,
                case,
                {
                    'attorney_name': 'AI Legal Assistant',
                    'attorney_title': 'Automated Legal Representative',
                    'law_firm_name': 'Ainflue Legal Automation'
                }
            )
            
            # Store document
            self.case_documents[case.case_id].append(cease_desist_document)
            result['documents'].append(cease_desist_document.document_id)
            
            # Send letter (simulated)
            result['actions'].append('cease_desist_sent')
            case.timeline.append({
                'event': 'Cease and Desist Letter Sent',
                'date': datetime.utcnow().isoformat(),
                'description': 'Cease and desist letter sent to defendant'
            })
            
            # Legal document generation cost
            result['costs'] = 150.0
            
            return result
            
        except Exception as e:
            logger.error(f"Cease and desist execution failed: {e}")
            raise
    
    async def _execute_settlement_negotiation(self, case: LegalCase, 
                                            enforcement_strategy: EnforcementStrategy) -> Dict[str, Any]:
        """Execute settlement negotiation process"""
        try:
            result = {
                'documents': [],
                'actions': [],
                'costs': 0.0
            }
            
            # Initiate settlement offer
            settlement_offer = await self.settlement_negotiator.initiate_settlement_negotiation(
                case, enforcement_strategy
            )
            
            # Store settlement offer
            self.settlement_offers[settlement_offer.offer_id] = settlement_offer
            
            # Generate settlement agreement template
            settlement_document = await self.document_generator.generate_document(
                LegalDocumentType.SETTLEMENT_AGREEMENT,
                case,
                {
                    'settlement_amount': settlement_offer.settlement_amount,
                    'payment_terms': '30 days',
                    'confidentiality_clause': 'Standard confidentiality provisions apply'
                }
            )
            
            # Store document
            self.case_documents[case.case_id].append(settlement_document)
            result['documents'].append(settlement_document.document_id)
            
            result['actions'].append('settlement_offer_sent')
            case.timeline.append({
                'event': 'Settlement Offer Sent',
                'date': datetime.utcnow().isoformat(),
                'description': f'Settlement offer of ${settlement_offer.settlement_amount:,.2f} sent'
            })
            
            # Settlement negotiation cost
            result['costs'] = 300.0
            
            return result
            
        except Exception as e:
            logger.error(f"Settlement negotiation execution failed: {e}")
            raise
    
    async def _execute_lawsuit_filing(self, case: LegalCase) -> Dict[str, Any]:
        """Execute lawsuit filing process"""
        try:
            result = {
                'documents': [],
                'actions': [],
                'costs': 0.0
            }
            
            # Generate infringement complaint
            complaint_document = await self.document_generator.generate_document(
                LegalDocumentType.INFRINGEMENT_COMPLAINT,
                case,
                {
                    'attorney_name': 'AI Legal Assistant',
                    'court_name': f'{case.jurisdiction.value.replace("_", " ").title()} Court'
                }
            )
            
            # Generate evidence package
            evidence_document = await self.document_generator.generate_document(
                LegalDocumentType.EVIDENCE_PACKAGE,
                case,
                {
                    'evidence_summary': 'Comprehensive digital evidence of infringement'
                }
            )
            
            # Store documents
            self.case_documents[case.case_id].extend([complaint_document, evidence_document])
            result['documents'].extend([complaint_document.document_id, evidence_document.document_id])
            
            result['actions'].append('lawsuit_filed')
            case.timeline.append({
                'event': 'Lawsuit Filed',
                'date': datetime.utcnow().isoformat(),
                'description': 'Copyright infringement lawsuit filed in court'
            })
            
            # Lawsuit filing cost
            result['costs'] = 1500.0
            
            return result
            
        except Exception as e:
            logger.error(f"Lawsuit filing execution failed: {e}")
            raise
    
    def _generate_next_steps(self, case: LegalCase, action_type: LegalActionType,
                           enforcement_strategy: EnforcementStrategy) -> List[str]:
        """Generate recommended next steps"""
        
        next_steps = []
        
        if action_type == LegalActionType.DMCA_TAKEDOWN:
            next_steps.extend([
                'Monitor for compliance within 14 days',
                'Escalate to cease and desist if no response',
                'Document platform response for evidence'
            ])
            
        elif action_type == LegalActionType.CEASE_DESIST:
            next_steps.extend([
                'Wait for response within 10 business days',
                'Prepare settlement negotiation if partial compliance',
                'Consider lawsuit filing if no response'
            ])
            
        elif action_type == LegalActionType.SETTLEMENT_NEGOTIATION:
            next_steps.extend([
                'Monitor for settlement response',
                'Prepare counter-offer strategy',
                'Set deadline for negotiation completion'
            ])
            
        elif action_type == LegalActionType.LAWSUIT_FILING:
            next_steps.extend([
                'Serve defendant with court papers',
                'Prepare for discovery phase',
                'Monitor court schedule and deadlines'
            ])
        
        # Add strategy-specific steps
        if enforcement_strategy == EnforcementStrategy.AGGRESSIVE:
            next_steps.append('Prepare immediate escalation options')
        elif enforcement_strategy == EnforcementStrategy.SETTLEMENT_FOCUSED:
            next_steps.append('Explore additional settlement opportunities')
        
        return next_steps
    
    def _estimate_resolution_time(self, action_type: LegalActionType,
                                enforcement_strategy: EnforcementStrategy) -> int:
        """Estimate resolution time in days"""
        
        base_times = {
            LegalActionType.DMCA_TAKEDOWN: 14,
            LegalActionType.CEASE_DESIST: 30,
            LegalActionType.COPYRIGHT_CLAIM: 45,
            LegalActionType.SETTLEMENT_NEGOTIATION: 60,
            LegalActionType.LAWSUIT_FILING: 180,
            LegalActionType.COURT_INJUNCTION: 90
        }
        
        base_time = base_times.get(action_type, 60)
        
        # Adjust by strategy
        if enforcement_strategy == EnforcementStrategy.AGGRESSIVE:
            return int(base_time * 0.7)
        elif enforcement_strategy == EnforcementStrategy.QUICK_RESOLUTION:
            return int(base_time * 0.5)
        elif enforcement_strategy == EnforcementStrategy.DIPLOMATIC:
            return int(base_time * 1.3)
        
        return base_time
    
    async def _update_automation_metrics(self, action_result: LegalActionResult):
        """Update automation performance metrics"""
        try:
            action_type = action_result.action_type.value
            
            # Update action-specific metrics
            if action_type not in self.automation_metrics:
                self.automation_metrics[action_type] = {
                    'total_actions': 0,
                    'successful_actions': 0,
                    'avg_execution_time': 0.0,
                    'avg_cost': 0.0,
                    'success_rate': 0.0
                }
            
            metrics = self.automation_metrics[action_type]
            
            # Update counters
            metrics['total_actions'] += 1
            if action_result.success:
                metrics['successful_actions'] += 1
            
            # Update averages
            metrics['avg_execution_time'] = (
                metrics['avg_execution_time'] * 0.9 + action_result.execution_time * 0.1
            )
            metrics['avg_cost'] = (
                metrics['avg_cost'] * 0.9 + action_result.costs_incurred * 0.1
            )
            metrics['success_rate'] = metrics['successful_actions'] / metrics['total_actions']
            
            # Add to action history
            self.action_history[action_result.action_id] = {
                'action_type': action_type,
                'case_id': action_result.case_id,
                'success': action_result.success,
                'execution_time': action_result.execution_time,
                'costs': action_result.costs_incurred,
                'timestamp': action_result.created_date.isoformat()
            }
            
            # Keep history manageable
            if len(self.action_history) > 1000:
                # Keep only the most recent 500 entries
                recent_items = sorted(
                    self.action_history.items(),
                    key=lambda x: x[1]['timestamp'],
                    reverse=True
                )[:500]
                self.action_history = dict(recent_items)
                
        except Exception as e:
            logger.error(f"Metrics update failed: {e}")
    
    async def get_case_status(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive case status"""
        try:
            if case_id not in self.active_cases:
                return None
            
            case = self.active_cases[case_id]
            documents = self.case_documents.get(case_id, [])
            
            return {
                'case_id': case_id,
                'case_type': case.case_type.value,
                'status': case.status.value,
                'jurisdiction': case.jurisdiction.value,
                'estimated_damages': case.estimated_damages,
                'legal_costs': case.legal_costs,
                'success_probability': case.success_probability,
                'documents_count': len(documents),
                'timeline_events': len(case.timeline),
                'created_date': case.created_date.isoformat(),
                'last_updated': case.last_updated.isoformat(),
                'next_actions': self._get_pending_actions(case)
            }
            
        except Exception as e:
            logger.error(f"Case status retrieval failed: {e}")
            return None
    
    def _get_pending_actions(self, case: LegalCase) -> List[str]:
        """Get pending actions for case"""
        if case.status == LegalActionStatus.INITIATED:
            return ['Monitor initial response', 'Prepare escalation if needed']
        elif case.status == LegalActionStatus.PENDING:
            return ['Wait for response', 'Document compliance status']
        elif case.status == LegalActionStatus.SERVED:
            return ['Monitor deadline', 'Prepare next phase']
        else:
            return ['No pending actions']
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        return {
            'engine_id': id(self),
            'active_cases': len(self.active_cases),
            'total_documents': sum(len(docs) for docs in self.case_documents.values()),
            'pending_settlements': len(self.settlement_offers),
            'automation_metrics': self.automation_metrics.copy(),
            'action_history_size': len(self.action_history),
            'last_updated': datetime.utcnow().isoformat()
        }


# Factory function for easy instantiation
def create_legal_automation_engine(config: Optional[Dict[str, Any]] = None) -> LegalAutomationEngine:
    """
    Factory function to create Legal Automation Engine
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured LegalAutomationEngine instance
    """
    return LegalAutomationEngine(config)


# Export all public classes and functions
__all__ = [
    'LegalAutomationEngine',
    'DMCAProcessor',
    'LegalDocumentGenerator',
    'SettlementNegotiator',
    'LegalCase',
    'LegalDocument',
    'DMCANotice',
    'SettlementOffer',
    'LegalActionResult',
    'LegalActionType',
    'LegalDocumentType',
    'LegalJurisdiction',
    'EnforcementStrategy',
    'LegalActionStatus',
    'create_legal_automation_engine'
]