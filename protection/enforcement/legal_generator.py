"""
Legal Document Generation System
Professional automated generation of legal documents for copyright enforcement
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import aiofiles

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types of legal documents that can be generated"""
    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    LEGAL_NOTICE = "legal_notice"
    DEMAND_LETTER = "demand_letter"
    SETTLEMENT_OFFER = "settlement_offer"
    COPYRIGHT_REGISTRATION = "copyright_registration"
    LICENSING_AGREEMENT = "licensing_agreement"
    INFRINGEMENT_REPORT = "infringement_report"
    COUNTER_NOTICE_RESPONSE = "counter_notice_response"
    COURT_FILING = "court_filing"


class DocumentStatus(Enum):
    """Status of generated documents"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    DISPUTED = "disputed"
    EXPIRED = "expired"


class JurisdictionType(Enum):
    """Legal jurisdictions supported"""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_GDPR = "eu_gdpr"
    UK_COPYRIGHT = "uk_copyright"
    CANADA_FEDERAL = "canada_federal"
    AUSTRALIA_COPYRIGHT = "australia_copyright"
    GERMANY_UWG = "germany_uwg"
    FRANCE_CPI = "france_cpi"
    INTERNATIONAL = "international"


@dataclass
class LegalEntity:
    """Legal entity information"""
    name: str
    legal_name: Optional[str] = None
    entity_type: str = "individual"  # individual, corporation, partnership, etc.
    address_line1: str = ""
    address_line2: str = ""
    city: str = ""
    state_province: str = ""
    postal_code: str = ""
    country: str = ""
    email: str = ""
    phone: str = ""
    
    # Legal identifiers
    tax_id: Optional[str] = None
    business_registration: Optional[str] = None
    copyright_registration_numbers: List[str] = field(default_factory=list)
    
    # Representative information
    legal_representative: Optional[str] = None
    attorney_name: Optional[str] = None
    attorney_bar_number: Optional[str] = None
    attorney_contact: Optional[str] = None


@dataclass
class InfringementDetails:
    """Details of copyright infringement"""
    infringing_url: str
    infringing_title: str
    infringing_description: str = ""
    platform: str = ""
    uploader_username: str = ""
    upload_date: Optional[datetime] = None
    discovery_date: datetime = field(default_factory=datetime.utcnow)
    
    # Original work details
    original_title: str = ""
    original_url: str = ""
    original_creation_date: Optional[datetime] = None
    original_publication_date: Optional[datetime] = None
    copyright_registration: Optional[str] = None
    
    # Evidence references
    evidence_package_id: str = ""
    similarity_score: float = 0.0
    infringement_type: str = "exact_copy"  # exact_copy, partial_copy, derivative, etc.
    
    # Damages and impact
    estimated_damages: float = 0.0
    currency: str = "USD"
    impact_description: str = ""


@dataclass
class DocumentContext:
    """Context data for document generation"""
    document_type: DocumentType
    case_id: str
    copyright_owner: LegalEntity
    infringement: InfringementDetails
    jurisdiction: JurisdictionType = JurisdictionType.US_FEDERAL
    
    # Optional entities
    accused_infringer: Optional[LegalEntity] = None
    platform_operator: Optional[LegalEntity] = None
    
    # Request details
    requested_action: str = "immediate_removal"
    response_deadline: Optional[datetime] = None
    settlement_amount: Optional[float] = None
    
    # Additional context
    template_variables: Dict[str, Any] = field(default_factory=dict)
    custom_clauses: List[str] = field(default_factory=list)
    priority_level: str = "normal"  # low, normal, high, urgent


@dataclass
class GeneratedDocument:
    """Generated legal document"""
    id: str
    document_type: DocumentType
    case_id: str
    title: str
    content: str
    file_path: Optional[str] = None
    
    # Metadata
    jurisdiction: JurisdictionType = JurisdictionType.US_FEDERAL
    status: DocumentStatus = DocumentStatus.DRAFT
    template_used: str = ""
    generation_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Validity and tracking
    valid_until: Optional[datetime] = None
    sent_timestamp: Optional[datetime] = None
    recipient_email: Optional[str] = None
    tracking_id: Optional[str] = None
    
    # Legal compliance
    compliance_checked: bool = False
    attorney_reviewed: bool = False
    digital_signature: Optional[str] = None
    
    # Document hash for integrity
    content_hash: str = field(init=False)
    
    def __post_init__(self):
        self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


class DMCATemplateGenerator:
    """Generator for DMCA takedown notices"""
    
    def __init__(self):
        self.template_content = self._get_dmca_template()
    
    def _get_dmca_template(self) -> str:
        """DMCA takedown notice template"""



        return """
DMCA TAKEDOWN NOTICE

To: {{ platform_operator.name }}
{{ platform_operator.address_line1 }}
{% if platform_operator.address_line2 %}{{ platform_operator.address_line2 }}{% endif %}
{{ platform_operator.city }}, {{ platform_operator.state_province }} {{ platform_operator.postal_code }}
{{ platform_operator.country }}

Date: {{ current_date }}

Re: DMCA Takedown Notice - Case {{ case_id }}

Dear Copyright Agent,

I am writing to notify you of copyright infringement occurring on your platform pursuant to the Digital Millennium Copyright Act ("DMCA"), 17 U.S.C. § 512(c)(3).

I. IDENTIFICATION OF COPYRIGHTED WORK

The copyrighted work at issue is:
- Title: "{{ infringement.original_title }}"
- Original URL: {{ infringement.original_url }}
- Creation Date: {{ infringement.original_creation_date.strftime('%B %d, %Y') if infringement.original_creation_date else 'N/A' }}
{% if infringement.copyright_registration %}
- Copyright Registration: {{ infringement.copyright_registration }}
{% endif %}

II. IDENTIFICATION OF INFRINGING MATERIAL

The infringing material is located at:
- Infringing URL: {{ infringement.infringing_url }}
- Platform: {{ infringement.platform }}
- Infringing Title: "{{ infringement.infringing_title }}"
- Upload Date: {{ infringement.upload_date.strftime('%B %d, %Y') if infringement.upload_date else 'Unknown' }}
- Uploader: {{ infringement.uploader_username }}

III. STATEMENT OF GOOD FAITH BELIEF

I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

IV. STATEMENT OF ACCURACY

I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the copyright owner of an exclusive right that is allegedly infringed.

V. AUTHORIZATION AND CONTACT INFORMATION

I am authorized to act on behalf of the copyright owner. My contact information is:

{{ copyright_owner.name }}
{% if copyright_owner.legal_representative %}
Acting through: {{ copyright_owner.legal_representative }}
{% endif %}
{{ copyright_owner.address_line1 }}
{% if copyright_owner.address_line2 %}{{ copyright_owner.address_line2 }}{% endif %}
{{ copyright_owner.city }}, {{ copyright_owner.state_province }} {{ copyright_owner.postal_code }}
{{ copyright_owner.country }}
Email: {{ copyright_owner.email }}
Phone: {{ copyright_owner.phone }}

VI. REQUESTED ACTION

Please remove or disable access to the infringing material immediately. This notice serves as an official request under the DMCA for immediate removal of the identified infringing content.

{% if response_deadline %}
Please confirm removal within {{ response_deadline.strftime('%B %d, %Y') }}.
{% endif %}

Thank you for your prompt attention to this matter.

{% if copyright_owner.attorney_name %}
/s/ {{ copyright_owner.attorney_name }}
{{ copyright_owner.attorney_name }}, Esq.
Bar Number: {{ copyright_owner.attorney_bar_number }}
Attorney for {{ copyright_owner.name }}
{% else %}
/s/ {{ copyright_owner.name }}
{{ copyright_owner.name }}
Copyright Owner
{% endif %}

---
This notice was generated automatically by IA Influencer Agent Content Protection System
Case ID: {{ case_id }}
Generation Date: {{ generation_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') }}
        """.strip()
    
    async def generate(self, context: DocumentContext) -> GeneratedDocument:
        """Generate DMCA takedown notice"""



        try:
            template = Template(self.template_content)
            
            # Prepare template variables
            template_vars = {
                'case_id': context.case_id,
                'copyright_owner': context.copyright_owner,
                'infringement': context.infringement,
                'platform_operator': context.platform_operator,
                'current_date': datetime.utcnow().strftime('%B %d, %Y'),
                'generation_timestamp': datetime.utcnow(),
                'response_deadline': context.response_deadline,
                **context.template_variables
            }
            
            # Generate content
            content = template.render(**template_vars)
            
            # Create document
            doc_id = f"DMCA-{context.case_id}-{int(datetime.utcnow().timestamp())}"
            
            document = GeneratedDocument(
                id=doc_id,
                document_type=DocumentType.DMCA_TAKEDOWN,
                case_id=context.case_id,
                title=f"DMCA Takedown Notice - Case {context.case_id}",
                content=content,
                jurisdiction=context.jurisdiction,
                template_used="dmca_standard_v1",
                valid_until=datetime.utcnow() + timedelta(days=30)
            )
            
            logger.info(f"Generated DMCA takedown notice: {doc_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error generating DMCA takedown notice: {e}")
            raise


class CeaseDesistGenerator:
    """Generator for cease and desist letters"""
    
    def __init__(self):
        self.template_content = self._get_cease_desist_template()
    
    def _get_cease_desist_template(self) -> str:
        """Cease and desist letter template"""



        return """
CEASE AND DESIST LETTER

{{ current_date }}

{{ accused_infringer.name if accused_infringer else 'Infringing Party' }}
{% if accused_infringer %}
{{ accused_infringer.address_line1 }}
{% if accused_infringer.address_line2 %}{{ accused_infringer.address_line2 }}{% endif %}
{{ accused_infringer.city }}, {{ accused_infringer.state_province }} {{ accused_infringer.postal_code }}
{{ accused_infringer.country }}
{% endif %}

Re: CEASE AND DESIST - Copyright Infringement - Case {{ case_id }}

Dear {{ accused_infringer.name if accused_infringer else 'Sir/Madam' }},

I represent {{ copyright_owner.name }} ("Copyright Owner") in connection with the unauthorized use of copyrighted material. This letter serves as formal notice to CEASE AND DESIST from all copyright infringement activities.

COPYRIGHTED WORK

The copyrighted work at issue is:
- Title: "{{ infringement.original_title }}"
- Original URL: {{ infringement.original_url }}
- Creation Date: {{ infringement.original_creation_date.strftime('%B %d, %Y') if infringement.original_creation_date else 'N/A' }}
{% if infringement.copyright_registration %}
- Copyright Registration: {{ infringement.copyright_registration }}
{% endif %}

INFRINGING ACTIVITY

Your unauthorized use of this copyrighted material includes:
- Location: {{ infringement.infringing_url }}
- Platform: {{ infringement.platform }}
- Infringement Type: {{ infringement.infringement_type }}
- Discovery Date: {{ infringement.discovery_date.strftime('%B %d, %Y') }}

{% if infringement.estimated_damages > 0 %}
DAMAGES

The unauthorized use has caused and continues to cause significant damages to our client, including but not limited to:
- Estimated monetary damages: {{ '${:,.2f}'.format(infringement.estimated_damages) }} {{ infringement.currency }}
- Loss of licensing revenue
- Damage to reputation and brand
- Disruption of business operations

{% endif %}

LEGAL BASIS

This unauthorized use constitutes copyright infringement under:
- United States Copyright Act (17 U.S.C. § 101 et seq.)
- Digital Millennium Copyright Act (17 U.S.C. § 512)
{% if jurisdiction == JurisdictionType.EU_GDPR %}
- European Union Copyright Directive (2001/29/EC)
{% elif jurisdiction == JurisdictionType.GERMANY_UWG %}
- German Copyright Act (Urheberrechtsgesetz)
{% endif %}

DEMAND FOR CESSATION

YOU ARE HEREBY DEMANDED TO:

1. IMMEDIATELY cease and desist from all unauthorized use, reproduction, distribution, or display of the copyrighted work;

2. REMOVE all infringing content from {{ infringement.platform }} and any other platforms under your control;

3. PROVIDE written confirmation of compliance within {{ (response_deadline or (datetime.utcnow() + timedelta(days=10))).strftime('%B %d, %Y') }};

{% if settlement_amount %}
4. PAY damages in the amount of ${{ '{:,.2f}'.format(settlement_amount) }} {{ infringement.currency }} to compensate for the infringement;
{% endif %}

5. REFRAIN from any future infringement of our client's copyrighted works.

CONSEQUENCES OF NON-COMPLIANCE

Failure to comply with this demand may result in:
- Federal copyright infringement lawsuit seeking injunctive relief
- Monetary damages, including actual damages and profits or statutory damages up to $150,000 per work
- Attorney's fees and court costs
- Potential criminal penalties for willful infringement

This letter is not intended as a complete statement of the facts or law applicable to this matter and does not constitute a waiver of any rights or remedies, all of which are expressly reserved.

PRESERVATION OF EVIDENCE

You are hereby directed to preserve all evidence related to your use of the copyrighted work, including but not limited to communications, financial records, and technical data.

{% if response_deadline %}
We demand your response by {{ response_deadline.strftime('%B %d, %Y at %I:%M %p') }}.
{% else %}
We demand your response within ten (10) days of receipt of this letter.
{% endif %}

Please direct all correspondence to:

{% if copyright_owner.attorney_name %}
{{ copyright_owner.attorney_name }}, Esq.
Attorney for {{ copyright_owner.name }}
Bar Number: {{ copyright_owner.attorney_bar_number }}
{{ copyright_owner.attorney_contact }}
{% else %}
{{ copyright_owner.name }}
{{ copyright_owner.email }}
{{ copyright_owner.phone }}
{% endif %}

Sincerely,

{% if copyright_owner.attorney_name %}
/s/ {{ copyright_owner.attorney_name }}
{{ copyright_owner.attorney_name }}, Esq.
Attorney for {{ copyright_owner.name }}
{% else %}
/s/ {{ copyright_owner.name }}
{{ copyright_owner.name }}
Copyright Owner
{% endif %}

---
Document ID: {{ document_id }}
Case Reference: {{ case_id }}
Generated: {{ generation_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') }}
        """.strip()
    
    async def generate(self, context: DocumentContext) -> GeneratedDocument:
        """Generate cease and desist letter"""



        try:
            template = Template(self.template_content)
            
            # Prepare template variables
            template_vars = {
                'case_id': context.case_id,
                'copyright_owner': context.copyright_owner,
                'infringement': context.infringement,
                'accused_infringer': context.accused_infringer,
                'current_date': datetime.utcnow().strftime('%B %d, %Y'),
                'generation_timestamp': datetime.utcnow(),
                'response_deadline': context.response_deadline,
                'settlement_amount': context.settlement_amount,
                'jurisdiction': context.jurisdiction,
                'document_id': f"CD-{context.case_id}-{int(datetime.utcnow().timestamp())}",
                **context.template_variables
            }
            
            # Generate content
            content = template.render(**template_vars)
            
            # Create document
            doc_id = f"CEASE-DESIST-{context.case_id}-{int(datetime.utcnow().timestamp())}"
            
            document = GeneratedDocument(
                id=doc_id,
                document_type=DocumentType.CEASE_DESIST,
                case_id=context.case_id,
                title=f"Cease and Desist Letter - Case {context.case_id}",
                content=content,
                jurisdiction=context.jurisdiction,
                template_used="cease_desist_standard_v1",
                valid_until=datetime.utcnow() + timedelta(days=60)
            )
            
            logger.info(f"Generated cease and desist letter: {doc_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error generating cease and desist letter: {e}")
            raise


class LegalNoticeGenerator:
    """Generator for legal notices"""
    
    def __init__(self):
        self.template_content = self._get_legal_notice_template()
    
    def _get_legal_notice_template(self) -> str:
        """Legal notice template"""



        return """
LEGAL NOTICE OF COPYRIGHT INFRINGEMENT

{{ current_date }}

TO: {{ accused_infringer.name if accused_infringer else 'Content Platform/Operator' }}

CASE REFERENCE: {{ case_id }}

NOTICE TO CEASE COPYRIGHT INFRINGEMENT

{{ copyright_owner.name }} ("Copyright Owner") hereby provides formal notice of copyright infringement occurring within your platform or under your control.

COPYRIGHTED WORK IDENTIFICATION

Work Title: "{{ infringement.original_title }}"
Original Location: {{ infringement.original_url }}
{% if infringement.copyright_registration %}
Copyright Registration: {{ infringement.copyright_registration }}
{% endif %}
Owner: {{ copyright_owner.name }}

INFRINGING CONTENT IDENTIFICATION

The following content constitutes unauthorized use of the above copyrighted work:

URL: {{ infringement.infringing_url }}
Platform: {{ infringement.platform }}
Content Title: "{{ infringement.infringing_title }}"
{% if infringement.uploader_username %}
Posted by: {{ infringement.uploader_username }}
{% endif %}
{% if infringement.upload_date %}
Upload Date: {{ infringement.upload_date.strftime('%B %d, %Y') }}
{% endif %}
Discovery Date: {{ infringement.discovery_date.strftime('%B %d, %Y') }}

INFRINGEMENT ANALYSIS

Our analysis indicates:
- Similarity Score: {{ (infringement.similarity_score * 100)|round(1) }}%
- Infringement Type: {{ infringement.infringement_type }}
- Evidence Package: {{ infringement.evidence_package_id }}

LEGAL AUTHORITY

This notice is served under the authority of:
{% if jurisdiction == JurisdictionType.US_FEDERAL %}
- Digital Millennium Copyright Act (17 U.S.C. § 512)
- United States Copyright Act (17 U.S.C. § 101 et seq.)
{% elif jurisdiction == JurisdictionType.EU_GDPR %}
- EU Copyright Directive (2001/29/EC)
- EU Digital Single Market Directive (2019/790)
{% elif jurisdiction == JurisdictionType.GERMANY_UWG %}
- Urheberrechtsgesetz (UrhG)
- Telemediengesetz (TMG)
{% endif %}

REQUIRED ACTION

You are hereby required to:

1. IMMEDIATELY remove or disable access to the infringing content
2. PREVENT re-uploading of the same or substantially similar content
3. PROVIDE written confirmation of removal within 48 hours
4. IMPLEMENT measures to prevent future infringement

GOOD FAITH STATEMENT

I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

ACCURACY STATEMENT

Under penalty of perjury, I declare that the information in this notice is accurate and that I am authorized to act on behalf of the copyright owner.

CONTACT INFORMATION

{{ copyright_owner.name }}
{{ copyright_owner.address_line1 }}
{% if copyright_owner.address_line2 %}{{ copyright_owner.address_line2 }}{% endif %}
{{ copyright_owner.city }}, {{ copyright_owner.state_province }} {{ copyright_owner.postal_code }}
{{ copyright_owner.country }}
Email: {{ copyright_owner.email }}
Phone: {{ copyright_owner.phone }}

{% if copyright_owner.attorney_name %}
Legal Representative:
{{ copyright_owner.attorney_name }}, Esq.
Bar Number: {{ copyright_owner.attorney_bar_number }}
{{ copyright_owner.attorney_contact }}
{% endif %}

TIME SENSITIVITY

This matter requires immediate attention. Failure to respond promptly may result in escalated legal action.

{% if response_deadline %}
Response Required By: {{ response_deadline.strftime('%B %d, %Y at %I:%M %p') }}
{% endif %}

Respectfully submitted,

{% if copyright_owner.attorney_name %}
/s/ {{ copyright_owner.attorney_name }}
{{ copyright_owner.attorney_name }}, Esq.
{% else %}
/s/ {{ copyright_owner.name }}
{{ copyright_owner.name }}
{% endif %}

---
Generated by IA Influencer Agent Legal System
Document ID: {{ document_id }}
Case ID: {{ case_id }}
Timestamp: {{ generation_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') }}
        """.strip()
    
    async def generate(self, context: DocumentContext) -> GeneratedDocument:
        """Generate legal notice"""



        try:
            template = Template(self.template_content)
            
            # Prepare template variables
            template_vars = {
                'case_id': context.case_id,
                'copyright_owner': context.copyright_owner,
                'infringement': context.infringement,
                'accused_infringer': context.accused_infringer,
                'current_date': datetime.utcnow().strftime('%B %d, %Y'),
                'generation_timestamp': datetime.utcnow(),
                'response_deadline': context.response_deadline,
                'jurisdiction': context.jurisdiction,
                'document_id': f"LN-{context.case_id}-{int(datetime.utcnow().timestamp())}",
                **context.template_variables
            }
            
            # Generate content
            content = template.render(**template_vars)
            
            # Create document
            doc_id = f"LEGAL-NOTICE-{context.case_id}-{int(datetime.utcnow().timestamp())}"
            
            document = GeneratedDocument(
                id=doc_id,
                document_type=DocumentType.LEGAL_NOTICE,
                case_id=context.case_id,
                title=f"Legal Notice - Case {context.case_id}",
                content=content,
                jurisdiction=context.jurisdiction,
                template_used="legal_notice_standard_v1",
                valid_until=datetime.utcnow() + timedelta(days=30)
            )
            
            logger.info(f"Generated legal notice: {doc_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error generating legal notice: {e}")
            raise


class LegalDocumentGenerator:
    """Main service for generating legal documents"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize generators
        self.dmca_generator = DMCATemplateGenerator()
        self.cease_desist_generator = CeaseDesistGenerator()
        self.legal_notice_generator = LegalNoticeGenerator()
        
        # Storage configuration
        self.storage_path = Path(self.config.get('storage_path', 'legal_documents'))
        self.storage_path.mkdir(exist_ok=True)
        
        # Document settings
        self.auto_save = self.config.get('auto_save', True)
        self.require_review = self.config.get('require_review', True)
        self.default_jurisdiction = JurisdictionType(self.config.get('default_jurisdiction', 'us_federal'))
        
        # Generated documents cache
        self.generated_documents: Dict[str, GeneratedDocument] = {}
        
        logger.info("Legal document generator initialized")
    
    async def generate_document(
        self,
        document_type: DocumentType,
        context: DocumentContext
    ) -> GeneratedDocument:
        """Generate legal document based on type and context"""



        try:
            logger.info(f"Generating {document_type.value} document for case {context.case_id}")
            
            # Validate context
            self._validate_context(context)
            
            # Set default response deadline if not provided
            if not context.response_deadline:
                if document_type == DocumentType.DMCA_TAKEDOWN:
                    context.response_deadline = datetime.utcnow() + timedelta(days=7)
                elif document_type == DocumentType.CEASE_DESIST:
                    context.response_deadline = datetime.utcnow() + timedelta(days=10)
                elif document_type == DocumentType.LEGAL_NOTICE:
                    context.response_deadline = datetime.utcnow() + timedelta(days=3)
            
            # Generate document based on type
            if document_type == DocumentType.DMCA_TAKEDOWN:
                document = await self.dmca_generator.generate(context)
            elif document_type == DocumentType.CEASE_DESIST:
                document = await self.cease_desist_generator.generate(context)
            elif document_type == DocumentType.LEGAL_NOTICE:
                document = await self.legal_notice_generator.generate(context)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Set review status
            if self.require_review:
                document.status = DocumentStatus.REVIEW
            else:
                document.status = DocumentStatus.APPROVED
            
            # Cache generated document
            self.generated_documents[document.id] = document
            
            # Auto-save if enabled
            if self.auto_save:
                await self._save_document(document)
            
            logger.info(f"Successfully generated {document_type.value}: {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"Error generating {document_type.value} document: {e}")
            raise
    
    def _validate_context(self, context: DocumentContext):
        """Validate document context"""
        required_fields = {
            'case_id': context.case_id,
            'copyright_owner.name': context.copyright_owner.name,
            'copyright_owner.email': context.copyright_owner.email,
            'infringement.infringing_url': context.infringement.infringing_url,
            'infringement.original_title': context.infringement.original_title
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value:
                raise ValueError(f"Required field '{field_name}' is missing or empty")
        
        # Document-specific validation
        if context.document_type == DocumentType.DMCA_TAKEDOWN:
            if not context.platform_operator:
                raise ValueError("Platform operator information required for DMCA takedown")
        
        if context.document_type == DocumentType.CEASE_DESIST:
            if not context.accused_infringer and not context.infringement.uploader_username:
                raise ValueError("Accused infringer information required for cease and desist")
    
    async def _save_document(self, document: GeneratedDocument):
        """Save document to persistent storage"""



        try:
            case_dir = self.storage_path / document.case_id
            case_dir.mkdir(exist_ok=True)
            
            # Save document content
            filename = f"{document.id}.txt"
            file_path = case_dir / filename
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(document.content)
            
            document.file_path = str(file_path)
            
            # Save document metadata
            metadata = {
                'id': document.id,
                'document_type': document.document_type.value,
                'case_id': document.case_id,
                'title': document.title,
                'file_path': document.file_path,
                'jurisdiction': document.jurisdiction.value,
                'status': document.status.value,
                'template_used': document.template_used,
                'generation_timestamp': document.generation_timestamp.isoformat(),
                'valid_until': document.valid_until.isoformat() if document.valid_until else None,
                'sent_timestamp': document.sent_timestamp.isoformat() if document.sent_timestamp else None,
                'recipient_email': document.recipient_email,
                'tracking_id': document.tracking_id,
                'compliance_checked': document.compliance_checked,
                'attorney_reviewed': document.attorney_reviewed,
                'digital_signature': document.digital_signature,
                'content_hash': document.content_hash
            }
            
            metadata_file = case_dir / f"{document.id}_metadata.json"
            async with aiofiles.open(metadata_file, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
            
            logger.debug(f"Document saved: {document.id}")
            
        except Exception as e:
            logger.error(f"Error saving document {document.id}: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[GeneratedDocument]:
        """Retrieve generated document"""



        try:
            # Check cache first
            if document_id in self.generated_documents:
                return self.generated_documents[document_id]
            
            # Search in storage
            for case_dir in self.storage_path.iterdir():
                if case_dir.is_dir():
                    metadata_file = case_dir / f"{document_id}_metadata.json"
                    if metadata_file.exists():
                        # Load metadata
                        async with aiofiles.open(metadata_file, 'r') as f:
                            metadata = json.loads(await f.read())
                        
                        # Load content
                        content_file = Path(metadata['file_path'])
                        if content_file.exists():
                            async with aiofiles.open(content_file, 'r', encoding='utf-8') as f:
                                content = await f.read()
                            
                            # Reconstruct document
                            document = GeneratedDocument(
                                id=metadata['id'],
                                document_type=DocumentType(metadata['document_type']),
                                case_id=metadata['case_id'],
                                title=metadata['title'],
                                content=content,
                                file_path=metadata['file_path'],
                                jurisdiction=JurisdictionType(metadata['jurisdiction']),
                                status=DocumentStatus(metadata['status']),
                                template_used=metadata['template_used'],
                                generation_timestamp=datetime.fromisoformat(metadata['generation_timestamp']),
                                valid_until=datetime.fromisoformat(metadata['valid_until']) if metadata.get('valid_until') else None,
                                sent_timestamp=datetime.fromisoformat(metadata['sent_timestamp']) if metadata.get('sent_timestamp') else None,
                                recipient_email=metadata.get('recipient_email'),
                                tracking_id=metadata.get('tracking_id'),
                                compliance_checked=metadata.get('compliance_checked', False),
                                attorney_reviewed=metadata.get('attorney_reviewed', False),
                                digital_signature=metadata.get('digital_signature')
                            )
                            
                            # Verify content hash
                            if document.content_hash != metadata['content_hash']:
                                logger.warning(f"Content hash mismatch for document {document_id}")
                            
                            # Cache document
                            self.generated_documents[document_id] = document
                            return document
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None
    
    async def update_document_status(
        self,
        document_id: str,
        new_status: DocumentStatus,
        notes: Optional[str] = None
    ) -> bool:
        """Update document status"""



        try:
            document = await self.get_document(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            old_status = document.status
            document.status = new_status
            
            # Handle status-specific updates
            if new_status == DocumentStatus.SENT:
                document.sent_timestamp = datetime.utcnow()
            elif new_status == DocumentStatus.APPROVED:
                document.attorney_reviewed = True
            
            # Save updated document
            if self.auto_save:
                await self._save_document(document)
            
            logger.info(f"Document {document_id} status updated: {old_status.value} -> {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document status: {e}")
            return False
    
    async def mark_document_sent(
        self,
        document_id: str,
        recipient_email: str,
        tracking_id: Optional[str] = None
    ) -> bool:
        """Mark document as sent"""



        try:
            document = await self.get_document(document_id)
            if not document:
                return False
            
            document.status = DocumentStatus.SENT
            document.sent_timestamp = datetime.utcnow()
            document.recipient_email = recipient_email
            document.tracking_id = tracking_id
            
            if self.auto_save:
                await self._save_document(document)
            
            logger.info(f"Document {document_id} marked as sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking document as sent: {e}")
            return False
    
    async def get_documents_by_case(self, case_id: str) -> List[GeneratedDocument]:
        """Get all documents for a specific case"""



        try:
            documents = []
            
            case_dir = self.storage_path / case_id
            if case_dir.exists():
                for metadata_file in case_dir.glob("*_metadata.json"):
                    document_id = metadata_file.stem.replace("_metadata", "")
                    document = await self.get_document(document_id)
                    if document:
                        documents.append(document)
            
            # Sort by generation timestamp
            documents.sort(key=lambda d: d.generation_timestamp, reverse=True)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents for case {case_id}: {e}")
            return []
    
    async def check_document_validity(self, document_id: str) -> Dict[str, Any]:
        """Check if document is still valid"""



        try:
            document = await self.get_document(document_id)
            if not document:
                return {'valid': False, 'reason': 'Document not found'}
            
            now = datetime.utcnow()
            
            # Check expiration
            if document.valid_until and now > document.valid_until:
                return {'valid': False, 'reason': 'Document expired'}
            
            # Check status
            if document.status in [DocumentStatus.EXPIRED, DocumentStatus.DISPUTED]:
                return {'valid': False, 'reason': f'Document status: {document.status.value}'}
            
            return {
                'valid': True,
                'status': document.status.value,
                'expires': document.valid_until.isoformat() if document.valid_until else None,
                'age_days': (now - document.generation_timestamp).days
            }
            
        except Exception as e:
            logger.error(f"Error checking document validity: {e}")
            return {'valid': False, 'reason': str(e)}
    
    async def cleanup_expired_documents(self):
        """Clean up expired documents"""



        try:
            cleaned_count = 0
            cutoff_date = datetime.utcnow() - timedelta(days=365)  # Keep for 1 year
            
            for case_dir in self.storage_path.iterdir():
                if case_dir.is_dir():
                    for metadata_file in case_dir.glob("*_metadata.json"):
                        try:
                            async with aiofiles.open(metadata_file, 'r') as f:
                                metadata = json.loads(await f.read())
                            
                            generation_date = datetime.fromisoformat(metadata['generation_timestamp'])
                            
                            # Check if document should be cleaned up
                            should_cleanup = (
                                generation_date < cutoff_date or
                                metadata.get('status') == DocumentStatus.EXPIRED.value
                            )
                            
                            if should_cleanup:
                                # Remove files
                                document_id = metadata['id']
                                content_file = Path(metadata['file_path'])
                                
                                if content_file.exists():
                                    content_file.unlink()
                                
                                metadata_file.unlink()
                                
                                # Remove from cache
                                if document_id in self.generated_documents:
                                    del self.generated_documents[document_id]
                                
                                cleaned_count += 1
                                
                        except Exception as e:
                            logger.error(f"Error processing {metadata_file}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} expired documents")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired documents: {e}")
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """Get document generation statistics"""



        try:
            stats = {
                'total_documents': len(self.generated_documents),
                'by_type': {},
                'by_status': {},
                'by_jurisdiction': {},
                'storage_path': str(self.storage_path),
                'auto_save_enabled': self.auto_save,
                'review_required': self.require_review
            }
            
            # Count by type, status, and jurisdiction
            for document in self.generated_documents.values():
                doc_type = document.document_type.value
                stats['by_type'][doc_type] = stats['by_type'].get(doc_type, 0) + 1
                
                status = document.status.value
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                jurisdiction = document.jurisdiction.value
                stats['by_jurisdiction'][jurisdiction] = stats['by_jurisdiction'].get(jurisdiction, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting generation statistics: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown document generator"""



        try:
            # Save all cached documents
            for document in self.generated_documents.values():
                if self.auto_save:
                    await self._save_document(document)
            
            self.generated_documents.clear()
            logger.info("Legal document generator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down document generator: {e}")


# Global instance
document_generator = LegalDocumentGenerator()


async def get_document_generator() -> LegalDocumentGenerator:
    """Get the global legal document generator instance"""



    return document_generator


__all__ = [
    'LegalDocumentGenerator',
    'DocumentContext',
    'GeneratedDocument',
    'LegalEntity',
    'InfringementDetails',
    'DocumentType',
    'DocumentStatus',
    'JurisdictionType',
    'DMCATemplateGenerator',
    'CeaseDesistGenerator',
    'LegalNoticeGenerator',
    'get_document_generator'
]
