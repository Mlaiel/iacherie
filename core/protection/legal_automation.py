"""
Legal Automation System for Content Protection

This module provides comprehensive legal automation capabilities:
- Automated DMCA takedown notice generation and submission
- Legal document templates and processing
- International copyright law compliance
- Evidence packaging for legal proceedings
- Digital signatures and chain of custody

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import uuid
from pathlib import Path
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor

# Document generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Digital signatures
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Email and notifications
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, ViolationCase
from ...database.models.legal import DMCARequest, LegalCase, CopyrightClaim
from ...config.settings import get_settings
from .evidence_collector import EvidenceCollector

logger = get_logger(__name__)
settings = get_settings()


class LegalJurisdiction(Enum):
    """Legal jurisdictions for copyright enforcement"""
    US_DMCA = "us_dmca"                    # US Digital Millennium Copyright Act
    EU_COPYRIGHT = "eu_copyright"          # EU Copyright Directive
    UK_COPYRIGHT = "uk_copyright"          # UK Copyright, Designs and Patents Act
    CANADA_COPYRIGHT = "canada_copyright"  # Canadian Copyright Act
    AUSTRALIA_COPYRIGHT = "australia_copyright"  # Australian Copyright Act
    INTERNATIONAL = "international"        # International copyright treaties


class LegalDocumentType(Enum):
    """Types of legal documents"""
    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    COPYRIGHT_CLAIM = "copyright_claim"
    LICENSING_AGREEMENT = "licensing_agreement"
    SETTLEMENT_OFFER = "settlement_offer"
    COURT_FILING = "court_filing"
    EVIDENCE_PACKAGE = "evidence_package"


class LegalActionType(Enum):
    """Types of legal actions"""
    TAKEDOWN_REQUEST = "takedown_request"
    MONETIZATION_CLAIM = "monetization_claim"
    LICENSING_DEMAND = "licensing_demand"
    LEGAL_NOTICE = "legal_notice"
    COURT_ACTION = "court_action"


@dataclass
class LegalEntity:
    """Legal entity information"""
    name: str
    legal_type: str  # individual, corporation, LLC, etc.
    address: str
    city: str
    state_province: str
    postal_code: str
    country: str
    email: str
    phone: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None


@dataclass
class CopyrightInformation:
    """Copyright ownership information"""
    owner: LegalEntity
    registration_number: Optional[str] = None
    registration_date: Optional[datetime] = None
    creation_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    copyright_notice: str = ""
    work_title: str = ""
    work_description: str = ""
    work_category: str = ""  # musical, literary, artistic, etc.


@dataclass
class ViolationDetails:
    """Details of copyright violation"""
    infringing_url: str
    platform: str
    violator_info: Optional[Dict[str, Any]] = None
    violation_type: str = "unauthorized_reproduction"
    violation_description: str = ""
    evidence_urls: List[str] = field(default_factory=list)
    screenshot_paths: List[str] = field(default_factory=list)
    detection_date: datetime = field(default_factory=datetime.utcnow)
    similarity_score: Optional[float] = None


@dataclass
class LegalDocumentTemplate:
    """Template for legal documents"""
    document_type: LegalDocumentType
    jurisdiction: LegalJurisdiction
    template_path: str
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    language: str = "en"


class LegalAutomation:
    """
    Legal automation system for content protection
    
    Provides automated generation and submission of legal documents
    for copyright enforcement and violation response.
    """
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates" / "legal"
        self.evidence_collector = EvidenceCollector()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Digital signature setup
        self._private_key = None
        self._public_key = None
        self._load_signing_keys()
        
        logger.info("Legal automation system initialized")
    
    async def generate_dmca_takedown(self, copyright_info: CopyrightInformation, 
                                   violation: ViolationDetails) -> Dict[str, Any]:
        """Generate DMCA takedown notice"""
        try:
            # Prepare document data
            document_data = {
                'copyright_owner': copyright_info.owner.__dict__,
                'work_title': copyright_info.work_title,
                'work_description': copyright_info.work_description,
                'infringing_url': violation.infringing_url,
                'platform': violation.platform,
                'violation_description': violation.violation_description,
                'detection_date': violation.detection_date.isoformat(),
                'similarity_score': violation.similarity_score,
                'good_faith_statement': self._generate_good_faith_statement(),
                'perjury_statement': self._generate_perjury_statement(),
                'signature_date': datetime.utcnow().isoformat(),
                'document_id': str(uuid.uuid4())
            }
            
            # Generate PDF document
            pdf_path = await self._generate_pdf_document(
                LegalDocumentType.DMCA_TAKEDOWN,
                document_data
            )
            
            # Create evidence package
            evidence_package = await self._create_evidence_package(violation)
            
            # Digital signature
            signature = await self._sign_document(pdf_path)
            
            # Prepare submission data
            submission_data = {
                'document_path': pdf_path,
                'evidence_package': evidence_package,
                'digital_signature': signature,
                'submission_ready': True,
                'generated_at': datetime.utcnow(),
                'document_hash': await self._calculate_file_hash(pdf_path)
            }
            
            logger.info(f"DMCA takedown notice generated: {document_data['document_id']}")
            return submission_data
            
        except Exception as e:
            logger.error(f"DMCA takedown generation failed: {e}")
            return {}
    
    async def submit_dmca_takedown(self, takedown_data: Dict[str, Any], platform: str) -> bool:
        """Submit DMCA takedown notice to platform"""
        try:
            if platform.lower() == "youtube":
                return await self._submit_youtube_dmca(takedown_data)
            elif platform.lower() == "instagram":
                return await self._submit_instagram_dmca(takedown_data)
            elif platform.lower() == "facebook":
                return await self._submit_facebook_dmca(takedown_data)
            elif platform.lower() == "tiktok":
                return await self._submit_tiktok_dmca(takedown_data)
            else:
                # Generic email submission
                return await self._submit_generic_dmca(takedown_data, platform)
                
        except Exception as e:
            logger.error(f"DMCA submission failed for {platform}: {e}")
            return False
    
    async def generate_cease_desist_letter(self, copyright_info: CopyrightInformation,
                                         violation: ViolationDetails,
                                         recipient: LegalEntity) -> Dict[str, Any]:
        """Generate cease and desist letter"""
        try:
            document_data = {
                'copyright_owner': copyright_info.owner.__dict__,
                'recipient': recipient.__dict__,
                'work_title': copyright_info.work_title,
                'infringing_url': violation.infringing_url,
                'violation_description': violation.violation_description,
                'demand_actions': self._generate_cease_desist_demands(),
                'legal_consequences': self._generate_legal_consequences_text(),
                'response_deadline': (datetime.utcnow() + timedelta(days=10)).isoformat(),
                'document_id': str(uuid.uuid4()),
                'signature_date': datetime.utcnow().isoformat()
            }
            
            pdf_path = await self._generate_pdf_document(
                LegalDocumentType.CEASE_DESIST,
                document_data
            )
            
            signature = await self._sign_document(pdf_path)
            
            return {
                'document_path': pdf_path,
                'digital_signature': signature,
                'document_data': document_data,
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Cease and desist generation failed: {e}")
            return {}
    
    async def generate_licensing_agreement(self, copyright_info: CopyrightInformation,
                                         licensee: LegalEntity,
                                         license_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Generate licensing agreement"""
        try:
            document_data = {
                'licensor': copyright_info.owner.__dict__,
                'licensee': licensee.__dict__,
                'work_title': copyright_info.work_title,
                'license_type': license_terms.get('type', 'commercial'),
                'license_duration': license_terms.get('duration', '1 year'),
                'license_fee': license_terms.get('fee', 'TBD'),
                'usage_restrictions': license_terms.get('restrictions', []),
                'territory': license_terms.get('territory', 'Worldwide'),
                'effective_date': license_terms.get('effective_date', datetime.utcnow().isoformat()),
                'document_id': str(uuid.uuid4())
            }
            
            pdf_path = await self._generate_pdf_document(
                LegalDocumentType.LICENSING_AGREEMENT,
                document_data
            )
            
            return {
                'document_path': pdf_path,
                'document_data': document_data,
                'requires_signature': True,
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Licensing agreement generation failed: {e}")
            return {}
    
    async def _generate_pdf_document(self, doc_type: LegalDocumentType, data: Dict[str, Any]) -> str:
        """Generate PDF document from template and data"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Create PDF document
            doc = SimpleDocTemplate(temp_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            if doc_type == LegalDocumentType.DMCA_TAKEDOWN:
                story = self._build_dmca_content(data, styles)
            elif doc_type == LegalDocumentType.CEASE_DESIST:
                story = self._build_cease_desist_content(data, styles)
            elif doc_type == LegalDocumentType.LICENSING_AGREEMENT:
                story = self._build_licensing_content(data, styles)
            
            doc.build(story)
            
            logger.info(f"PDF document generated: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _build_dmca_content(self, data: Dict[str, Any], styles) -> List:
        """Build DMCA takedown notice content"""
        story = []
        
        # Header
        story.append(Paragraph("DMCA TAKEDOWN NOTICE", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Copyright owner information
        story.append(Paragraph("COPYRIGHT OWNER INFORMATION", styles['Heading2']))
        owner = data['copyright_owner']
        story.append(Paragraph(f"Name: {owner['name']}", styles['Normal']))
        story.append(Paragraph(f"Address: {owner['address']}, {owner['city']}, {owner['state_province']} {owner['postal_code']}", styles['Normal']))
        story.append(Paragraph(f"Email: {owner['email']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Copyrighted work information
        story.append(Paragraph("COPYRIGHTED WORK INFORMATION", styles['Heading2']))
        story.append(Paragraph(f"Title: {data['work_title']}", styles['Normal']))
        story.append(Paragraph(f"Description: {data['work_description']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Infringing material
        story.append(Paragraph("INFRINGING MATERIAL", styles['Heading2']))
        story.append(Paragraph(f"Infringing URL: {data['infringing_url']}", styles['Normal']))
        story.append(Paragraph(f"Platform: {data['platform']}", styles['Normal']))
        story.append(Paragraph(f"Description of Infringement: {data['violation_description']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Legal statements
        story.append(Paragraph("LEGAL STATEMENTS", styles['Heading2']))
        story.append(Paragraph(data['good_faith_statement'], styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(data['perjury_statement'], styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Signature
        story.append(Paragraph(f"Signature: {owner['name']}", styles['Normal']))
        story.append(Paragraph(f"Date: {data['signature_date']}", styles['Normal']))
        story.append(Paragraph(f"Document ID: {data['document_id']}", styles['Normal']))
        
        return story
    
    def _build_cease_desist_content(self, data: Dict[str, Any], styles) -> List:
        """Build cease and desist letter content"""
        story = []
        
        # Header
        story.append(Paragraph("CEASE AND DESIST LETTER", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Date and recipient
        story.append(Paragraph(f"Date: {data['signature_date']}", styles['Normal']))
        story.append(Spacer(1, 6))
        
        recipient = data['recipient']
        story.append(Paragraph("To:", styles['Normal']))
        story.append(Paragraph(f"{recipient['name']}", styles['Normal']))
        story.append(Paragraph(f"{recipient['address']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Content
        story.append(Paragraph("RE: Cease and Desist - Copyright Infringement", styles['Heading2']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(f"This letter serves as formal notice that you are infringing upon the copyrighted work titled '{data['work_title']}' owned by {data['copyright_owner']['name']}.", styles['Normal']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(f"The infringing material can be found at: {data['infringing_url']}", styles['Normal']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph("DEMANDS:", styles['Heading3']))
        for demand in data['demand_actions']:
            story.append(Paragraph(f"• {demand}", styles['Normal']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(f"You have until {data['response_deadline']} to comply with these demands.", styles['Normal']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(data['legal_consequences'], styles['Normal']))
        
        return story
    
    def _build_licensing_content(self, data: Dict[str, Any], styles) -> List:
        """Build licensing agreement content"""
        story = []
        
        # Header
        story.append(Paragraph("LICENSING AGREEMENT", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Parties
        story.append(Paragraph("PARTIES", styles['Heading2']))
        licensor = data['licensor']
        licensee = data['licensee']
        story.append(Paragraph(f"Licensor: {licensor['name']}", styles['Normal']))
        story.append(Paragraph(f"Licensee: {licensee['name']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Licensed work
        story.append(Paragraph("LICENSED WORK", styles['Heading2']))
        story.append(Paragraph(f"Title: {data['work_title']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Terms
        story.append(Paragraph("LICENSE TERMS", styles['Heading2']))
        story.append(Paragraph(f"Type: {data['license_type']}", styles['Normal']))
        story.append(Paragraph(f"Duration: {data['license_duration']}", styles['Normal']))
        story.append(Paragraph(f"Fee: {data['license_fee']}", styles['Normal']))
        story.append(Paragraph(f"Territory: {data['territory']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Restrictions
        if data.get('usage_restrictions'):
            story.append(Paragraph("USAGE RESTRICTIONS", styles['Heading2']))
            for restriction in data['usage_restrictions']:
                story.append(Paragraph(f"• {restriction}", styles['Normal']))
        
        return story
    
    async def _create_evidence_package(self, violation: ViolationDetails) -> str:
        """Create evidence package for legal submission"""
        try:
            # Create temporary directory for evidence
            temp_dir = tempfile.mkdtemp()
            evidence_dir = Path(temp_dir) / "evidence"
            evidence_dir.mkdir(exist_ok=True)
            
            # Collect evidence files
            evidence_files = []
            
            # Copy screenshots
            for screenshot_path in violation.screenshot_paths:
                if Path(screenshot_path).exists():
                    dest_path = evidence_dir / Path(screenshot_path).name
                    Path(screenshot_path).copy(dest_path)
                    evidence_files.append(dest_path)
            
            # Create evidence manifest
            manifest = {
                'violation_url': violation.infringing_url,
                'platform': violation.platform,
                'detection_date': violation.detection_date.isoformat(),
                'similarity_score': violation.similarity_score,
                'evidence_files': [f.name for f in evidence_files],
                'collection_timestamp': datetime.utcnow().isoformat()
            }
            
            manifest_path = evidence_dir / "evidence_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Create ZIP package
            zip_path = Path(temp_dir) / "evidence_package.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in evidence_dir.rglob("*"):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(evidence_dir))
            
            logger.info(f"Evidence package created: {zip_path}")
            return str(zip_path)
            
        except Exception as e:
            logger.error(f"Evidence package creation failed: {e}")
            return ""
    
    async def _sign_document(self, document_path: str) -> Dict[str, str]:
        """Create digital signature for document"""
        try:
            if not self._private_key:
                logger.warning("No private key available for signing")
                return {}
            
            # Calculate document hash
            document_hash = await self._calculate_file_hash(document_path)
            
            # Sign the hash
            signature = self._private_key.sign(
                document_hash.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature
            signature_b64 = signature.hex()
            
            return {
                'signature': signature_b64,
                'algorithm': 'RSA-PSS-SHA256',
                'document_hash': document_hash,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document signing failed: {e}")
            return {}
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"File hash calculation failed: {e}")
            return ""
    
    def _load_signing_keys(self):
        """Load RSA keys for document signing"""
        try:
            # In production, these would be loaded from secure storage
            # For now, we'll generate temporary keys
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            self._public_key = self._private_key.public_key()
            
            logger.info("Signing keys loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load signing keys: {e}")
    
    def _generate_good_faith_statement(self) -> str:
        """Generate good faith statement for DMCA"""
        return ("I have a good faith belief that use of the copyrighted materials described above "
                "on the infringing web pages is not authorized by the copyright owner, or its agent, "
                "or the law.")
    
    def _generate_perjury_statement(self) -> str:
        """Generate perjury statement for DMCA"""
        return ("I swear, under penalty of perjury, that the information in this notification is "
                "accurate and that I am the copyright owner, or am authorized to act on behalf of "
                "the owner, of an exclusive right that is allegedly infringed.")
    
    def _generate_cease_desist_demands(self) -> List[str]:
        """Generate demands for cease and desist letter"""
        return [
            "Immediately cease and desist all use of the copyrighted material",
            "Remove all infringing content from your platform or website",
            "Provide written confirmation of compliance within 10 days",
            "Refrain from any future use of the copyrighted material without proper authorization"
        ]
    
    def _generate_legal_consequences_text(self) -> str:
        """Generate legal consequences warning text"""
        return ("Failure to comply with this demand may result in legal action against you, "
                "including but not limited to seeking monetary damages, injunctive relief, "
                "and attorney's fees. We reserve all rights to pursue any and all legal remedies available.")
    
    # Platform-specific DMCA submission methods
    async def _submit_youtube_dmca(self, takedown_data: Dict[str, Any]) -> bool:
        """Submit DMCA to YouTube"""
        # Implementation for YouTube copyright claim submission
        logger.info("YouTube DMCA submission not yet implemented")
        return False
    
    async def _submit_instagram_dmca(self, takedown_data: Dict[str, Any]) -> bool:
        """Submit DMCA to Instagram"""
        # Implementation for Instagram copyright report
        logger.info("Instagram DMCA submission not yet implemented")
        return False
    
    async def _submit_facebook_dmca(self, takedown_data: Dict[str, Any]) -> bool:
        """Submit DMCA to Facebook"""
        # Implementation for Facebook copyright report
        logger.info("Facebook DMCA submission not yet implemented")
        return False
    
    async def _submit_tiktok_dmca(self, takedown_data: Dict[str, Any]) -> bool:
        """Submit DMCA to TikTok"""
        # Implementation for TikTok copyright report
        logger.info("TikTok DMCA submission not yet implemented")
        return False
    
    async def _submit_generic_dmca(self, takedown_data: Dict[str, Any], platform: str) -> bool:
        """Submit DMCA via email"""
        try:
            # Get platform contact information
            contact_info = self._get_platform_contact_info(platform)
            if not contact_info:
                logger.error(f"No contact information available for {platform}")
                return False
            
            # Send email with DMCA notice
            return await self._send_dmca_email(takedown_data, contact_info)
            
        except Exception as e:
            logger.error(f"Generic DMCA submission failed: {e}")
            return False
    
    def _get_platform_contact_info(self, platform: str) -> Optional[Dict[str, str]]:
        """Get contact information for platform"""
        # This would be maintained in a database or configuration
        platform_contacts = {
            'generic': {
                'email': 'copyright@example.com',
                'name': 'Copyright Department'
            }
        }
        
        return platform_contacts.get(platform.lower())
    
    async def _send_dmca_email(self, takedown_data: Dict[str, Any], contact_info: Dict[str, str]) -> bool:
        """Send DMCA notice via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USER
            msg['To'] = contact_info['email']
            msg['Subject'] = "DMCA Takedown Notice"
            
            # Email body
            body = ("Please find attached a DMCA takedown notice for copyrighted material "
                   "that has been identified on your platform.")
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            if takedown_data.get('document_path'):
                with open(takedown_data['document_path'], "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= "dmca_notice.pdf"',
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(settings.SMTP_USER, contact_info['email'], text)
            server.quit()
            
            logger.info(f"DMCA notice sent to {contact_info['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
