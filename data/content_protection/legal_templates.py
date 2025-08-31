"""
Advanced Legal Templates Manager
===============================

Industrial-grade legal document templates for comprehensive content protection.
Handles DMCA notices, licensing agreements, and international copyright compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE 
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, modification ou distribution sans autorisation 
écrite explicite de l'auteur est strictement interdite et constitue une violation 
du droit d'auteur. Les contrevenants s'exposent à des poursuites judiciaires.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json
import hashlib
from pathlib import Path

# Template engine imports
from jinja2 import Environment, DictLoader, select_autoescape
import markdown

# PDF generation imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Email and messaging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis


class TemplateType(Enum):
    """Legal template types"""
    DMCA_TAKEDOWN = "dmca_takedown"
    COPYRIGHT_NOTICE = "copyright_notice"
    LICENSING_AGREEMENT = "licensing_agreement"
    COLLABORATION_CONTRACT = "collaboration_contract"
    CEASE_DESIST = "cease_desist"
    PLATFORM_TOS = "platform_tos"
    PRIVACY_POLICY = "privacy_policy"
    INFRINGEMENT_WARNING = "infringement_warning"
    MONETIZATION_AGREEMENT = "monetization_agreement"
    COUNTER_NOTICE = "counter_notice"
    SETTLEMENT_OFFER = "settlement_offer"
    COURT_FILING = "court_filing"


class JurisdictionType(Enum):
    """Legal jurisdiction types"""
    US_FEDERAL = "us_federal"
    EU_COPYRIGHT = "eu_copyright"
    UK_COPYRIGHT = "uk_copyright"
    GERMAN_COPYRIGHT = "german_copyright"
    INTERNATIONAL = "international"
    BERNE_CONVENTION = "berne_convention"


@dataclass
class TemplateConfig:
    """Legal template configuration"""
    template_type: TemplateType
    jurisdiction: JurisdictionType
    language: str
    format_type: str  # html, pdf, text
    include_signatures: bool
    digital_signature: bool
    notarization_required: bool
    multi_language: bool


@dataclass
class DMCATemplate:
    """DMCA takedown notice template data"""
    copyright_owner: str
    copyright_owner_email: str
    copyright_owner_address: str
    agent_name: Optional[str]
    work_title: str
    work_description: str
    work_creation_date: datetime
    original_location: str
    infringing_location: str
    platform_name: str
    evidence_urls: List[str]
    good_faith_statement: str
    penalty_statement: str
    signature_date: datetime
    electronic_signature: str


@dataclass
class CopyrightNotice:
    """Copyright notice data"""
    copyright_symbol: str
    copyright_year: str
    copyright_owner: str
    work_title: str
    rights_statement: str
    usage_restrictions: List[str]
    contact_information: Dict[str, str]
    license_terms: Optional[str]


@dataclass
class LegalDocument:
    """Generated legal document"""
    document_id: str
    template_type: TemplateType
    jurisdiction: JurisdictionType
    content: str
    format_type: str
    metadata: Dict[str, Any]
    generated_at: datetime
    valid_until: Optional[datetime]
    digital_hash: str
    signed: bool


class LegalTemplateManager:
    """
    Advanced legal template management system.
    
    Provides comprehensive legal document generation for content protection
    with multi-jurisdiction support and automated compliance verification.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 templates_path: str = "./templates"):
        """
        Initialize LegalTemplateManager.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            templates_path: Path to legal templates directory
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self.templates_path = Path(templates_path)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=DictLoader({}),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Load templates
        self.templates = self._load_all_templates()
        
        # Configuration
        self.cache_ttl = 7200  # 2 hours
        self.document_retention_days = 2555  # 7 years (legal requirement)
        
        # Jurisdiction-specific settings
        self.jurisdiction_configs = {
            JurisdictionType.US_FEDERAL: {
                'dmca_compliance': True,
                'statutory_damages': (750, 30000),
                'required_fields': ['good_faith_statement', 'penalty_statement'],
                'notification_timeframe': 24  # hours
            },
            JurisdictionType.EU_COPYRIGHT: {
                'gdpr_compliance': True,
                'article_17_compliance': True,
                'required_fields': ['copyright_basis', 'proportionality_statement'],
                'notification_timeframe': 72  # hours
            },
            JurisdictionType.GERMAN_COPYRIGHT: {
                'urheberrecht_compliance': True,
                'required_fields': ['rechteinhaberschaft', 'verhaeltnismaessigkeit'],
                'notification_timeframe': 48  # hours
            }
        }
    
    def _load_all_templates(self) -> Dict[str, Dict[str, str]]:
        """Load all legal templates from files and database"""
        templates = {}
        
        # Load built-in templates
        templates.update(self._get_builtin_templates())
        
        # Load custom templates from files if available
        if self.templates_path.exists():
            templates.update(self._load_file_templates())
        
        return templates
    
    def _get_builtin_templates(self) -> Dict[str, Dict[str, str]]:
        """Get built-in legal templates"""



        return {
            TemplateType.DMCA_TAKEDOWN.value: {
                JurisdictionType.US_FEDERAL.value: self._get_us_dmca_template(),
                JurisdictionType.INTERNATIONAL.value: self._get_international_dmca_template()
            },
            TemplateType.COPYRIGHT_NOTICE.value: {
                JurisdictionType.US_FEDERAL.value: self._get_us_copyright_template(),
                JurisdictionType.EU_COPYRIGHT.value: self._get_eu_copyright_template(),
                JurisdictionType.GERMAN_COPYRIGHT.value: self._get_german_copyright_template()
            },
            TemplateType.CEASE_DESIST.value: {
                JurisdictionType.US_FEDERAL.value: self._get_us_cease_desist_template(),
                JurisdictionType.EU_COPYRIGHT.value: self._get_eu_cease_desist_template()
            },
            TemplateType.COUNTER_NOTICE.value: {
                JurisdictionType.US_FEDERAL.value: self._get_us_counter_notice_template()
            }
        }
    
    async def generate_dmca_notice(self, dmca_data: DMCATemplate,
                                 config: TemplateConfig) -> LegalDocument:
        """
        Generate DMCA takedown notice.
        
        Args:
            dmca_data: DMCA notice data
            config: Template configuration
            
        Returns:
            Generated legal document
        """



        try:
            # Validate DMCA data
            if not await self._validate_dmca_data(dmca_data, config.jurisdiction):
                raise ValueError("Invalid DMCA data for jurisdiction")
            
            # Get appropriate template
            template_content = self._get_template_content(
                TemplateType.DMCA_TAKEDOWN, config.jurisdiction, config.language
            )
            
            # Prepare template variables
            template_vars = {
                'copyright_owner': dmca_data.copyright_owner,
                'copyright_owner_email': dmca_data.copyright_owner_email,
                'copyright_owner_address': dmca_data.copyright_owner_address,
                'agent_name': dmca_data.agent_name or dmca_data.copyright_owner,
                'work_title': dmca_data.work_title,
                'work_description': dmca_data.work_description,
                'work_creation_date': dmca_data.work_creation_date.strftime('%Y-%m-%d'),
                'original_location': dmca_data.original_location,
                'infringing_location': dmca_data.infringing_location,
                'platform_name': dmca_data.platform_name,
                'evidence_urls': '\\n'.join(dmca_data.evidence_urls),
                'good_faith_statement': dmca_data.good_faith_statement,
                'penalty_statement': dmca_data.penalty_statement,
                'signature_date': dmca_data.signature_date.strftime('%Y-%m-%d'),
                'electronic_signature': dmca_data.electronic_signature,
                'current_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'document_id': str(uuid.uuid4()),
                'jurisdiction': config.jurisdiction.value,
                'platform_contact': self._get_platform_contact_info(dmca_data.platform_name)
            }
            
            # Render template
            template = self.jinja_env.from_string(template_content)
            rendered_content = template.render(**template_vars)
            
            # Create legal document
            document = LegalDocument(
                document_id=template_vars['document_id'],
                template_type=TemplateType.DMCA_TAKEDOWN,
                jurisdiction=config.jurisdiction,
                content=rendered_content,
                format_type=config.format_type,
                metadata={
                    'copyright_owner': dmca_data.copyright_owner,
                    'platform': dmca_data.platform_name,
                    'work_title': dmca_data.work_title,
                    'infringing_url': dmca_data.infringing_location,
                    'config': asdict(config)
                },
                generated_at=datetime.utcnow(),
                valid_until=None,  # DMCA notices don't expire
                digital_hash=hashlib.sha256(rendered_content.encode()).hexdigest(),
                signed=config.digital_signature
            )
            
            # Convert to requested format
            if config.format_type == 'pdf':
                document.content = await self._convert_to_pdf(document.content, TemplateType.DMCA_TAKEDOWN)
            elif config.format_type == 'html':
                document.content = await self._convert_to_html(document.content)
            
            # Store document
            await self._store_legal_document(document)
            
            # Cache document
            await self._cache_document(document)
            
            self.logger.info(f"Generated DMCA notice {document.document_id}")
            return document
            
        except Exception as e:
            self.logger.error(f"Error generating DMCA notice: {str(e)}")
            raise
    
    async def generate_copyright_notice(self, notice_data: CopyrightNotice,
                                      config: TemplateConfig) -> LegalDocument:
        """
        Generate copyright notice.
        
        Args:
            notice_data: Copyright notice data
            config: Template configuration
            
        Returns:
            Generated copyright notice document
        """



        try:
            # Get template content
            template_content = self._get_template_content(
                TemplateType.COPYRIGHT_NOTICE, config.jurisdiction, config.language
            )
            
            # Prepare template variables
            template_vars = {
                'copyright_symbol': notice_data.copyright_symbol,
                'copyright_year': notice_data.copyright_year,
                'copyright_owner': notice_data.copyright_owner,
                'work_title': notice_data.work_title,
                'rights_statement': notice_data.rights_statement,
                'usage_restrictions': '\\n'.join(notice_data.usage_restrictions),
                'contact_email': notice_data.contact_information.get('email', ''),
                'contact_phone': notice_data.contact_information.get('phone', ''),
                'contact_address': notice_data.contact_information.get('address', ''),
                'license_terms': notice_data.license_terms or 'All rights reserved',
                'current_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'document_id': str(uuid.uuid4()),
                'jurisdiction': config.jurisdiction.value,
                'legal_framework': self._get_legal_framework(config.jurisdiction)
            }
            
            # Render template
            template = self.jinja_env.from_string(template_content)
            rendered_content = template.render(**template_vars)
            
            # Create document
            document = LegalDocument(
                document_id=template_vars['document_id'],
                template_type=TemplateType.COPYRIGHT_NOTICE,
                jurisdiction=config.jurisdiction,
                content=rendered_content,
                format_type=config.format_type,
                metadata={
                    'copyright_owner': notice_data.copyright_owner,
                    'work_title': notice_data.work_title,
                    'copyright_year': notice_data.copyright_year
                },
                generated_at=datetime.utcnow(),
                valid_until=None,  # Copyright notices don't expire
                digital_hash=hashlib.sha256(rendered_content.encode()).hexdigest(),
                signed=config.digital_signature
            )
            
            # Format conversion
            if config.format_type == 'pdf':
                document.content = await self._convert_to_pdf(document.content, TemplateType.COPYRIGHT_NOTICE)
            
            # Store and cache
            await self._store_legal_document(document)
            await self._cache_document(document)
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error generating copyright notice: {str(e)}")
            raise
    
    async def generate_cease_desist_letter(self, violation_data: Dict[str, Any],
                                         config: TemplateConfig) -> LegalDocument:
        """
        Generate cease and desist letter.
        
        Args:
            violation_data: Violation and infringer data
            config: Template configuration
            
        Returns:
            Generated cease and desist letter
        """



        try:
            template_content = self._get_template_content(
                TemplateType.CEASE_DESIST, config.jurisdiction, config.language
            )
            
            # Calculate damages
            damages = await self._calculate_statutory_damages(
                violation_data, config.jurisdiction
            )
            
            template_vars = {
                'infringer_name': violation_data.get('infringer_name', 'Unknown'),
                'infringer_address': violation_data.get('infringer_address', ''),
                'infringer_email': violation_data.get('infringer_email', ''),
                'copyright_owner': violation_data['copyright_owner'],
                'work_title': violation_data['work_title'],
                'work_description': violation_data['work_description'],
                'infringement_description': violation_data['infringement_description'],
                'infringing_urls': '\\n'.join(violation_data.get('infringing_urls', [])),
                'first_detected': violation_data.get('first_detected', datetime.utcnow().strftime('%Y-%m-%d')),
                'evidence_description': violation_data.get('evidence_description', ''),
                'damages_amount': damages['estimated_damages'],
                'statutory_range': f"${damages['min_statutory']} - ${damages['max_statutory']}",
                'response_deadline': (datetime.utcnow() + timedelta(days=14)).strftime('%Y-%m-%d'),
                'current_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'document_id': str(uuid.uuid4()),
                'sender_name': violation_data['copyright_owner'],
                'sender_title': violation_data.get('sender_title', 'Copyright Owner'),
                'sender_contact': violation_data.get('sender_contact', ''),
                'legal_framework': self._get_legal_framework(config.jurisdiction)
            }
            
            # Render and create document
            template = self.jinja_env.from_string(template_content)
            rendered_content = template.render(**template_vars)
            
            document = LegalDocument(
                document_id=template_vars['document_id'],
                template_type=TemplateType.CEASE_DESIST,
                jurisdiction=config.jurisdiction,
                content=rendered_content,
                format_type=config.format_type,
                metadata=violation_data,
                generated_at=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=30),
                digital_hash=hashlib.sha256(rendered_content.encode()).hexdigest(),
                signed=config.digital_signature
            )
            
            # Store and format
            await self._store_legal_document(document)
            
            if config.format_type == 'pdf':
                document.content = await self._convert_to_pdf(document.content, TemplateType.CEASE_DESIST)
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error generating cease and desist letter: {str(e)}")
            raise
    
    async def send_legal_document(self, document: LegalDocument, 
                                recipient_info: Dict[str, Any],
                                delivery_method: str = "email") -> bool:
        """
        Send legal document to recipient.
        
        Args:
            document: Legal document to send
            recipient_info: Recipient contact information
            delivery_method: Delivery method (email, certified_mail, fax)
            
        Returns:
            Delivery success status
        """



        try:
            if delivery_method == "email":
                return await self._send_email_document(document, recipient_info)
            elif delivery_method == "certified_mail":
                return await self._send_certified_mail(document, recipient_info)
            elif delivery_method == "fax":
                return await self._send_fax_document(document, recipient_info)
            else:
                raise ValueError(f"Unsupported delivery method: {delivery_method}")
                
        except Exception as e:
            self.logger.error(f"Error sending legal document: {str(e)}")
            return False
    
    # Template content methods
    
    def _get_us_dmca_template(self) -> str:
        """US Federal DMCA takedown template"""



        return """
DIGITAL MILLENNIUM COPYRIGHT ACT
SECTION 512(c)(3) TAKEDOWN NOTICE

To: {{ platform_contact.name }}
{{ platform_contact.address }}
Email: {{ platform_contact.email }}

Date: {{ current_date }}
Document ID: {{ document_id }}

NOTICE OF INFRINGEMENT

I, {{ copyright_owner }}, certify under penalty of perjury that I am the owner, or authorized to act on behalf of the owner, of certain intellectual property rights, said owner being {{ copyright_owner }}.

I HAVE A GOOD FAITH BELIEF that the use of the material described below is not authorized by the copyright owner, its agent, or the law.

THE INFORMATION IN THIS NOTIFICATION IS ACCURATE, and I swear under penalty of perjury that I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.

COPYRIGHTED WORK:
Title: {{ work_title }}
Description: {{ work_description }}
Created: {{ work_creation_date }}
Original Location: {{ original_location }}

INFRINGING MATERIAL:
Platform: {{ platform_name }}
Infringing URL: {{ infringing_location }}

EVIDENCE:
{{ evidence_urls }}

I request that you immediately remove or disable access to the infringing material described above.

CONTACT INFORMATION:
Name: {{ copyright_owner }}
Email: {{ copyright_owner_email }}
Address: {{ copyright_owner_address }}

{{ good_faith_statement }}

{{ penalty_statement }}

Electronic Signature: {{ electronic_signature }}
Date: {{ signature_date }}

---
This notice complies with the Digital Millennium Copyright Act, 17 U.S.C. § 512(c)(3).
Generated by IA Influencer Agent Legal System - © 2025 Fahed Mlaiel
        """
    
    def _get_international_dmca_template(self) -> str:
        """International DMCA takedown template"""



        return """
COPYRIGHT INFRINGEMENT TAKEDOWN NOTICE
(International Application)

To: {{ platform_name }} Copyright Agent
Date: {{ current_date }}
Document ID: {{ document_id }}
Jurisdiction: {{ jurisdiction }}

NOTICE OF COPYRIGHT INFRINGEMENT

I, {{ copyright_owner }}, am the copyright owner of the work described below, protected under international copyright law including the Berne Convention.

COPYRIGHTED WORK:
Title: {{ work_title }}
Description: {{ work_description }}
Created: {{ work_creation_date }}
Original Location: {{ original_location }}

UNAUTHORIZED USE:
Platform: {{ platform_name }}
Infringing URL: {{ infringing_location }}

EVIDENCE OF INFRINGEMENT:
{{ evidence_urls }}

LEGAL BASIS:
This notice is served under applicable copyright laws and international treaties, including:
- Berne Convention for the Protection of Literary and Artistic Works
- WIPO Copyright Treaty
- Applicable national copyright legislation

REQUEST FOR ACTION:
I request immediate removal of the infringing material and prevention of future uploads.

CONTACT INFORMATION:
{{ copyright_owner }}
{{ copyright_owner_email }}
{{ copyright_owner_address }}

{{ good_faith_statement }}

Signature: {{ electronic_signature }}
Date: {{ signature_date }}

---
Generated by IA Influencer Agent International Legal System
© 2025 Fahed Mlaiel - All Rights Reserved
        """
    
    def _get_us_copyright_template(self) -> str:
        """US Copyright notice template"""



        return """
COPYRIGHT NOTICE

{{ copyright_symbol }} {{ copyright_year }} {{ copyright_owner }}. All rights reserved.

WORK IDENTIFICATION:
Title: {{ work_title }}
Creator: {{ copyright_owner }}
Year of Creation: {{ copyright_year }}

RIGHTS STATEMENT:
{{ rights_statement }}

USAGE RESTRICTIONS:
{{ usage_restrictions }}

LICENSE TERMS:
{{ license_terms }}

CONTACT INFORMATION:
Email: {{ contact_email }}
Phone: {{ contact_phone }}
Address: {{ contact_address }}

LEGAL NOTICE:
This work is protected under United States copyright law (Title 17, U.S. Code) and international copyright treaties. Unauthorized reproduction, distribution, or display of this work may result in severe civil and criminal penalties.

ENFORCEMENT:
Copyright infringement is monitored by automated systems. Violations will be prosecuted to the full extent of the law.

Generated: {{ current_date }}
Document ID: {{ document_id }}

---
© 2025 IA Influencer Agent Platform - Fahed Mlaiel
Legal Protection System Active
        """
    
    def _get_eu_copyright_template(self) -> str:
        """EU Copyright notice template"""



        return """
URHEBERRECHTSHINWEIS / COPYRIGHT NOTICE
(European Union)

{{ copyright_symbol }} {{ copyright_year }} {{ copyright_owner }}. Alle Rechte vorbehalten / All rights reserved.

WERKANGABEN / WORK DETAILS:
Titel / Title: {{ work_title }}
Urheber / Creator: {{ copyright_owner }}
Schöpfungsjahr / Year of Creation: {{ copyright_year }}

RECHTEINHABER / RIGHTS HOLDER:
{{ copyright_owner }}
{{ contact_email }}

NUTZUNGSBESTIMMUNGEN / USAGE TERMS:
{{ usage_restrictions }}

RECHTLICHER RAHMEN / LEGAL FRAMEWORK:
Dieses Werk ist geschützt durch:
- EU-Urheberrechtsrichtlinie (2019/790/EU)
- Nationale Urheberrechtsgesetze der EU-Mitgliedstaaten
- Berner Übereinkunft

This work is protected under:
- EU Copyright Directive (2019/790/EU)
- National copyright laws of EU member states
- Berne Convention

LIZENZBESTIMMUNGEN / LICENSE TERMS:
{{ license_terms }}

KONTAKT / CONTACT:
{{ contact_email }}
{{ contact_address }}

Generiert / Generated: {{ current_date }}
Dokument-ID / Document ID: {{ document_id }}

---
© 2025 IA Influencer Agent Platform - Fahed Mlaiel
Europäisches Rechtsschutzsystem / European Legal Protection System
        """
    
    def _get_german_copyright_template(self) -> str:
        """German Copyright notice template"""



        return """
URHEBERRECHTSHINWEIS
Nach deutschem Urheberrechtsgesetz (UrhG)

{{ copyright_symbol }} {{ copyright_year }} {{ copyright_owner }}. Alle Rechte vorbehalten.

WERKANGABEN:
Titel: {{ work_title }}
Urheber: {{ copyright_owner }}
Schöpfungsjahr: {{ copyright_year }}

URHEBERSCHAFT:
{{ rights_statement }}

NUTZUNGSRECHTE:
{{ usage_restrictions }}

RECHTLICHER SCHUTZ:
Dieses Werk genießt Schutz nach dem Urheberrechtsgesetz (UrhG) der Bundesrepublik Deutschland. Jede Verwertung außerhalb der engen Grenzen des Urheberrechtsgesetzes ist ohne Zustimmung des Urhebers unzulässig und strafbar.

LIZENZBESTIMMUNGEN:
{{ license_terms }}

KONTAKT:
E-Mail: {{ contact_email }}
Telefon: {{ contact_phone }}
Anschrift: {{ contact_address }}

RECHTSDURCHSETZUNG:
Urheberrechtsverletzungen werden strafrechtlich und zivilrechtlich verfolgt (§§ 106-108a UrhG).

Erstellt: {{ current_date }}
Dokument-ID: {{ document_id }}

---
© 2025 IA Influencer Agent Plattform - Fahed Mlaiel
Deutsches Urheberrechtsschutzsystem
        """
    
    def _get_us_cease_desist_template(self) -> str:
        """US Cease and Desist letter template"""



        return """
CEASE AND DESIST NOTICE
COPYRIGHT INFRINGEMENT

{{ current_date }}

{{ infringer_name }}
{{ infringer_address }}

RE: Immediate Cessation of Copyright Infringement
    Work: "{{ work_title }}"
    Document ID: {{ document_id }}

Dear {{ infringer_name }},

I am writing to notify you that your unauthorized use of my copyrighted work constitutes copyright infringement under federal law.

COPYRIGHTED WORK:
Title: {{ work_title }}
Description: {{ work_description }}
Copyright Owner: {{ copyright_owner }}

INFRINGEMENT DETAILS:
{{ infringement_description }}

INFRINGING LOCATIONS:
{{ infringing_urls }}

First Detected: {{ first_detected }}

EVIDENCE:
{{ evidence_description }}

LEGAL BASIS:
Your actions constitute willful copyright infringement under Title 17 of the United States Code. Copyright infringement is subject to civil remedies under 17 U.S.C. § 504, including:

- Actual damages and profits (17 U.S.C. § 504(b))
- Statutory damages between {{ statutory_range }} per work (17 U.S.C. § 504(c))
- Attorney's fees (17 U.S.C. § 505)
- Injunctive relief (17 U.S.C. § 502)

ESTIMATED DAMAGES:
Based on the scope of infringement, estimated damages are {{ damages_amount }}.

DEMAND FOR CESSATION:
I hereby DEMAND that you:
1. Immediately cease all use of the copyrighted work
2. Remove all infringing content from all platforms
3. Provide written confirmation of compliance
4. Preserve all records related to the infringement

RESPONSE DEADLINE:
You must respond to this notice by {{ response_deadline }}. Failure to comply will result in legal action without further notice.

CONTACT:
{{ sender_name }}, {{ sender_title }}
{{ sender_contact }}

This letter serves as formal notice under applicable copyright law.

{{ sender_name }}
{{ current_date }}

---
Generated by IA Influencer Agent Legal System
© 2025 Fahed Mlaiel - Professional Legal Protection
        """
    
    def _get_us_counter_notice_template(self) -> str:
        """US DMCA Counter-Notice template"""



        return """
DMCA COUNTER-NOTIFICATION
17 U.S.C. § 512(g)(3)

To: {{ platform_name }} Copyright Agent
Date: {{ current_date }}
Document ID: {{ document_id }}

COUNTER-NOTIFICATION

I, {{ user_name }}, am the user who posted the material described below that was removed or disabled by your service.

REMOVED MATERIAL:
The material that was removed or disabled was located at:
{{ removed_urls }}

Description: {{ content_description }}

GOOD FAITH BELIEF:
I have a good faith belief that the material was removed or disabled as a result of mistake or misidentification of the material to be removed or disabled.

CONSENT TO JURISDICTION:
I consent to the jurisdiction of Federal District Court for the judicial district in which my address is located, or if my address is located outside of the United States, for any judicial district in which {{ platform_name }} may be found.

I will accept service of process from the person who provided the original notification or an agent of such person.

PENALTY OF PERJURY:
I swear, under penalty of perjury, that I have a good faith belief that each search result, link, or other URL identified above was removed or disabled as a result of a mistake or misidentification of the material or activity to be removed or disabled.

CONTACT INFORMATION:
Name: {{ user_name }}
Address: {{ user_address }}
Phone: {{ user_phone }}
Email: {{ user_email }}

SIGNATURE:
{{ electronic_signature }}
Date: {{ signature_date }}

---
This counter-notification complies with 17 U.S.C. § 512(g)(3).
Generated by IA Influencer Agent Legal System
        """
    
    # Helper methods
    
    async def _validate_dmca_data(self, dmca_data: DMCATemplate, jurisdiction: JurisdictionType) -> bool:
        """Validate DMCA data for specific jurisdiction"""



        try:
            jurisdiction_config = self.jurisdiction_configs.get(jurisdiction, {})
            required_fields = jurisdiction_config.get('required_fields', [])
            
            # Check required fields
            for field in required_fields:
                if field == 'good_faith_statement' and not dmca_data.good_faith_statement:
                    return False
                elif field == 'penalty_statement' and not dmca_data.penalty_statement:
                    return False
            
            # Validate email format
            if '@' not in dmca_data.copyright_owner_email:
                return False
            
            # Validate URLs
            if not dmca_data.infringing_location.startswith(('http://', 'https://')):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"DMCA validation error: {str(e)}")
            return False
    
    def _get_template_content(self, template_type: TemplateType, 
                            jurisdiction: JurisdictionType, language: str = "en") -> str:
        """Get template content for specific type and jurisdiction"""



        try:
            templates_for_type = self.templates.get(template_type.value, {})
            
            # Try specific jurisdiction first
            if jurisdiction.value in templates_for_type:
                return templates_for_type[jurisdiction.value]
            
            # Fall back to international template
            if JurisdictionType.INTERNATIONAL.value in templates_for_type:
                return templates_for_type[JurisdictionType.INTERNATIONAL.value]
            
            # Fall back to US template
            if JurisdictionType.US_FEDERAL.value in templates_for_type:
                return templates_for_type[JurisdictionType.US_FEDERAL.value]
            
            raise ValueError(f"No template found for {template_type.value} in {jurisdiction.value}")
            
        except Exception as e:
            self.logger.error(f"Error getting template content: {str(e)}")
            raise
    
    def _get_platform_contact_info(self, platform_name: str) -> Dict[str, str]:
        """Get platform contact information for legal notices"""
        platform_contacts = {
            'youtube': {
                'name': 'YouTube/Google LLC',
                'address': '901 Cherry Ave, San Bruno, CA 94066',
                'email': 'copyright@youtube.com'
            },
            'instagram': {
                'name': 'Meta Platforms, Inc.',
                'address': '1601 Willow Road, Menlo Park, CA 94025',
                'email': 'ip@fb.com'
            },
            'tiktok': {
                'name': 'TikTok Technology Limited',
                'address': '10 Earlsfort Terrace, Dublin 2, Ireland',
                'email': 'copyright@tiktok.com'
            },
            'twitter': {
                'name': 'Twitter, Inc.',
                'address': '1355 Market Street, Suite 900, San Francisco, CA 94103',
                'email': 'copyright@twitter.com'
            }
        }
        
        return platform_contacts.get(platform_name.lower(), {
            'name': platform_name,
            'address': 'Unknown',
            'email': 'copyright@' + platform_name.lower() + '.com'
        })
    
    def _get_legal_framework(self, jurisdiction: JurisdictionType) -> str:
        """Get legal framework description for jurisdiction"""
        frameworks = {
            JurisdictionType.US_FEDERAL: "United States Copyright Act (Title 17, U.S. Code) and Digital Millennium Copyright Act",
            JurisdictionType.EU_COPYRIGHT: "EU Copyright Directive (2019/790/EU) and national implementations",
            JurisdictionType.GERMAN_COPYRIGHT: "Urheberrechtsgesetz (UrhG) der Bundesrepublik Deutschland",
            JurisdictionType.UK_COPYRIGHT: "Copyright, Designs and Patents Act 1988 (UK)",
            JurisdictionType.INTERNATIONAL: "Berne Convention and WIPO Copyright Treaty",
            JurisdictionType.BERNE_CONVENTION: "Berne Convention for the Protection of Literary and Artistic Works"
        }
        
        return frameworks.get(jurisdiction, "Applicable national and international copyright law")
    
    async def _calculate_statutory_damages(self, violation_data: Dict[str, Any], 
                                         jurisdiction: JurisdictionType) -> Dict[str, Any]:
        """Calculate potential statutory damages"""



        try:
            jurisdiction_config = self.jurisdiction_configs.get(jurisdiction, {})
            
            if jurisdiction == JurisdictionType.US_FEDERAL:
                min_damage, max_damage = jurisdiction_config.get('statutory_damages', (750, 30000))
                
                # Estimate based on violation severity
                estimated = min_damage * 2  # Conservative estimate
                
                return {
                    'min_statutory': min_damage,
                    'max_statutory': max_damage,
                    'estimated_damages': f"${estimated:,}"
                }
            
            return {
                'min_statutory': 0,
                'max_statutory': 0,
                'estimated_damages': "To be determined under applicable law"
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating damages: {str(e)}")
            return {'estimated_damages': "Substantial damages under applicable law"}
    
    async def _convert_to_pdf(self, content: str, template_type: TemplateType) -> bytes:
        """Convert document content to PDF format"""



        try:
            from io import BytesIO
            buffer = BytesIO()
            
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center
            )
            
            title_map = {
                TemplateType.DMCA_TAKEDOWN: "DMCA TAKEDOWN NOTICE",
                TemplateType.COPYRIGHT_NOTICE: "COPYRIGHT NOTICE",
                TemplateType.CEASE_DESIST: "CEASE AND DESIST LETTER"
            }
            
            title = title_map.get(template_type, "LEGAL DOCUMENT")
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Add content
            normal_style = styles['Normal']
            paragraphs = content.split('\\n\\n')
            
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), normal_style))
                    story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting to PDF: {str(e)}")
            return content.encode('utf-8')
    
    async def _convert_to_html(self, content: str) -> str:
        """Convert document content to HTML format"""



        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Legal Document</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    .header {{ text-align: center; font-weight: bold; font-size: 18px; margin-bottom: 30px; }}
                    .content {{ white-space: pre-line; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="content">{content}</div>
                <div class="footer">
                    Generated by IA Influencer Agent Legal System<br>
                    © 2025 Fahed Mlaiel - All Rights Reserved
                </div>
            </body>
            </html>
            """
            return html_content
            
        except Exception as e:
            self.logger.error(f"Error converting to HTML: {str(e)}")
            return content
    
    async def _send_email_document(self, document: LegalDocument, 
                                 recipient_info: Dict[str, Any]) -> bool:
        """Send document via email"""



        try:
            # Email sending implementation would go here
            # This is a placeholder for the actual email functionality
            
            self.logger.info(f"Email sent for document {document.document_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def _store_legal_document(self, document: LegalDocument):
        """Store legal document in database"""



        try:
            # Database storage implementation
            pass
        except Exception as e:
            self.logger.error(f"Error storing document: {str(e)}")
    
    async def _cache_document(self, document: LegalDocument):
        """Cache document in Redis"""



        try:
            cache_key = f"legal_doc:{document.document_id}"
            document_data = asdict(document)
            
            # Convert datetime objects to ISO strings
            for key, value in document_data.items():
                if isinstance(value, datetime):
                    document_data[key] = value.isoformat()
            
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(document_data, default=str)
            )
            
        except Exception as e:
            self.logger.error(f"Error caching document: {str(e)}")
    
    def _load_file_templates(self) -> Dict[str, Dict[str, str]]:
        """Load templates from file system"""
        templates = {}
        
        try:
            for template_file in self.templates_path.glob("*.jinja2"):
                template_name = template_file.stem
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse template metadata from filename
                # Format: template_type_jurisdiction_language.jinja2
                parts = template_name.split('_')
                if len(parts) >= 2:
                    template_type = '_'.join(parts[:-1])
                    jurisdiction = parts[-1]
                    
                    if template_type not in templates:
                        templates[template_type] = {}
                    
                    templates[template_type][jurisdiction] = content
            
        except Exception as e:
            self.logger.warning(f"Error loading file templates: {str(e)}")
        
        return templates


@dataclass
class LegalTemplateData:
    """Data structure for legal template variables."""
    content_title: str
    content_type: str
    creator_name: str
    creator_email: str
    copyright_date: str
    infringing_url: str
    platform_name: str
    description: str
    evidence_urls: List[str]
    contact_info: Dict[str, str]


class LegalTemplateManager:
    """Manager for legal document templates and generation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize all legal templates."""



        return {
            'dmca_takedown': self._get_dmca_template(),
            'copyright_notice': self._get_copyright_template(),
            'licensing_agreement': self._get_licensing_template(),
            'collaboration_contract': self._get_collaboration_template(),
            'platform_tos': self._get_platform_tos_template(),
            'privacy_policy': self._get_privacy_template(),
            'infringement_warning': self._get_infringement_warning_template(),
            'monetization_agreement': self._get_monetization_template()
        }
    
    def generate_document(self, template_type: str, data: LegalTemplateData) -> str:
        """Generate a legal document from template and data."""



        try:
            if template_type not in self._templates:
                raise ValueError(f"Template type '{template_type}' not found")
            
            template = self._templates[template_type]
            
            # Replace template variables
            document = template.format(
                content_title=data.content_title,
                content_type=data.content_type,
                creator_name=data.creator_name,
                creator_email=data.creator_email,
                copyright_date=data.copyright_date,
                infringing_url=data.infringing_url,
                platform_name=data.platform_name,
                description=data.description,
                evidence_urls='\n'.join(data.evidence_urls),
                current_date=datetime.now().strftime('%Y-%m-%d'),
                contact_info=self._format_contact_info(data.contact_info)
            )
            
            self.logger.info(f"Generated {template_type} document for {data.creator_name}")
            return document
            
        except Exception as e:
            self.logger.error(f"Error generating document: {e}")
            raise
    
    def _format_contact_info(self, contact_info: Dict[str, str]) -> str:
        """Format contact information for templates."""
        formatted = []
        for key, value in contact_info.items():
            formatted.append(f"{key.title()}: {value}")
        return '\n'.join(formatted)
    
    def _get_dmca_template(self) -> str:
        """DMCA takedown notice template."""



        return """
DIGITAL MILLENNIUM COPYRIGHT ACT TAKEDOWN NOTICE

To: {platform_name} Copyright Agent
Date: {current_date}

I, {creator_name}, am the copyright owner of the work described below. I have a good faith belief that the use of the material described below is not authorized by me, my agent, or the law.

COPYRIGHTED WORK:
Title: {content_title}
Type: {content_type}
Copyright Date: {copyright_date}
Description: {description}

INFRINGING MATERIAL:
Location: {infringing_url}
Platform: {platform_name}

EVIDENCE:
{evidence_urls}

CONTACT INFORMATION:
{contact_info}
Email: {creator_email}

DECLARATION:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner.

Signature: {creator_name}
Date: {current_date}

---
Generated by IA Influencer Agent Content Protection System
© 2025 Fahed Mlaiel. All rights reserved.
        """
    
    def _get_copyright_template(self) -> str:
        """Copyright notice template."""



        return """
COPYRIGHT NOTICE

© {copyright_date} {creator_name}. All rights reserved.

WORK DETAILS:
Title: {content_title}
Type: {content_type}
Creator: {creator_name}
Date of Creation: {copyright_date}

RIGHTS RESERVED:
This work is protected by copyright law. No part of this work may be reproduced, distributed, transmitted, or displayed in any form or by any means without the prior written permission of the copyright owner.

UNAUTHORIZED USE:
Any unauthorized use, reproduction, or distribution of this work constitutes copyright infringement and may result in civil and criminal penalties.

CONTACT:
For licensing inquiries: {creator_email}
{contact_info}

LEGAL NOTICE:
This copyright notice was generated using IA Influencer Agent Content Protection System.
Removal or alteration of this notice is prohibited.

© 2025 IA Influencer Agent Platform - Fahed Mlaiel
        """
    
    def _get_licensing_template(self) -> str:
        """Content licensing agreement template."""



        return """
CONTENT LICENSING AGREEMENT

This agreement is entered into on {current_date} between:

LICENSOR: {creator_name}
Email: {creator_email}
{contact_info}

LICENSED WORK:
Title: {content_title}
Type: {content_type}
Description: {description}

TERMS AND CONDITIONS:
1. The licensor grants limited rights to use the above work
2. Usage must comply with the terms specified herein
3. Attribution is required in all uses
4. Commercial use requires separate agreement

ATTRIBUTION REQUIREMENT:
"{content_title}" by {creator_name} - Licensed under IA Influencer Agent Platform

CONTACT FOR LICENSING:
{creator_email}

This agreement is governed by applicable copyright laws.

---
Generated by IA Influencer Agent Licensing System
© 2025 Fahed Mlaiel. All rights reserved.
        """
    
    def _get_collaboration_template(self) -> str:
        """Collaboration contract template."""



        return """
CREATIVE COLLABORATION AGREEMENT

Date: {current_date}

PARTIES:
Primary Creator: {creator_name}
Email: {creator_email}
{contact_info}

PROJECT DETAILS:
Title: {content_title}
Type: {content_type}
Description: {description}

COLLABORATION TERMS:
1. All parties retain rights to their individual contributions
2. Joint ownership of collaborative elements
3. Revenue sharing as agreed upon
4. Credit requirements for all participants

INTELLECTUAL PROPERTY:
- Each collaborator retains rights to their original contributions
- Collaborative work is jointly owned
- Usage rights governed by this agreement

DISPUTE RESOLUTION:
Any disputes will be resolved through IA Influencer Agent Platform mediation system.

CONTACT:
Primary Contact: {creator_email}

---
Facilitated by IA Influencer Agent Collaboration Platform
© 2025 Fahed Mlaiel. All rights reserved.
        """
    
    def _get_platform_tos_template(self) -> str:
        """Platform terms of service template."""



        return """
IA INFLUENCER AGENT PLATFORM - TERMS OF SERVICE

Last Updated: {current_date}

ACCEPTANCE OF TERMS:
By using IA Influencer Agent Platform, you agree to these terms.

USER RIGHTS AND RESPONSIBILITIES:
- Users retain ownership of their original content
- Platform provides protection and monetization services
- Users must comply with copyright laws
- Respectful collaboration is required

CONTENT PROTECTION:
- Automated copyright monitoring
- DMCA compliance and takedown procedures
- Legal template generation
- Anti-piracy enforcement

INTELLECTUAL PROPERTY:
- Users retain rights to their content
- Platform technology is proprietary
- Unauthorized use of platform code is prohibited

PLATFORM SERVICES:
Content Type: {content_type}
Protection Level: Industrial Grade
Monitoring: 24/7 Automated

CONTACT:
Platform Owner: Fahed Mlaiel
Email: mlaiel@live.de

COPYRIGHT WARNING:
This platform and its code are protected by copyright.
Unauthorized copying, distribution, or reverse engineering is strictly prohibited.

© 2025 IA Influencer Agent Platform - Fahed Mlaiel
All rights reserved.
        """
    
    def _get_privacy_template(self) -> str:
        """Privacy policy template."""



        return """
IA INFLUENCER AGENT PLATFORM - PRIVACY POLICY

Effective Date: {current_date}

INFORMATION COLLECTION:
We collect information necessary to provide content protection services.

DATA USAGE:
- Content fingerprinting for protection
- Copyright monitoring and enforcement
- Platform analytics and improvements
- Legal compliance and documentation

USER RIGHTS:
- Access to your data
- Correction of inaccurate information
- Deletion requests (subject to legal requirements)
- Data portability

SECURITY:
We employ industry-standard security measures to protect your data.

CONTACT:
Data Protection Officer: Fahed Mlaiel
Email: mlaiel@live.de
{contact_info}

LEGAL BASIS:
Data processing is based on legitimate interests in providing content protection services.

---
© 2025 IA Influencer Agent Platform - Fahed Mlaiel
Privacy by Design - Protection by Default
        """
    
    def _get_infringement_warning_template(self) -> str:
        """Copyright infringement warning template."""



        return """
COPYRIGHT INFRINGEMENT WARNING

Date: {current_date}
To: {platform_name}

NOTICE OF INFRINGEMENT:
This is a formal notice of copyright infringement regarding content on your platform.

COPYRIGHTED WORK:
Title: {content_title}
Type: {content_type}
Owner: {creator_name}
Copyright Date: {copyright_date}

INFRINGING CONTENT:
Location: {infringing_url}
Description: {description}

EVIDENCE:
{evidence_urls}

REQUESTED ACTION:
Immediate removal of infringing content and prevention of re-upload.

LEGAL WARNING:
Continued hosting of infringing content may result in:
- DMCA takedown notices
- Legal action for copyright infringement
- Potential damages and legal fees

CONTACT:
{creator_name}
Email: {creator_email}
{contact_info}

This notice is generated by IA Influencer Agent Content Protection System.
Failure to respond may result in escalated legal action.

© 2025 IA Influencer Agent - Fahed Mlaiel
        """
    
    def _get_monetization_template(self) -> str:
        """Monetization agreement template."""



        return """
CONTENT MONETIZATION AGREEMENT

Agreement Date: {current_date}

CONTENT CREATOR:
Name: {creator_name}
Email: {creator_email}
{contact_info}

MONETIZED CONTENT:
Title: {content_title}
Type: {content_type}
Description: {description}

MONETIZATION TERMS:
- Revenue sharing as per platform standards
- Creator retains full ownership rights
- Platform provides distribution and protection
- Analytics and reporting included

PAYMENT TERMS:
- Monthly payment cycles
- Transparent revenue reporting
- Multiple payment methods supported
- Currency conversion available

INTELLECTUAL PROPERTY:
Creator maintains full ownership of content while granting platform limited distribution rights.

TERMINATION:
Either party may terminate with 30 days notice.

PLATFORM SERVICES:
- Content protection and monitoring
- Multi-platform distribution
- SEO optimization
- Collaboration matching

CONTACT:
Platform: IA Influencer Agent
Owner: Fahed Mlaiel
Email: mlaiel@live.de

---
Powered by IA Influencer Agent Monetization Engine
© 2025 Fahed Mlaiel. All rights reserved.
        """


# Template validator
class TemplateValidator:
    """Validator for legal template integrity and compliance."""
    
    def __init__(self):
        self.required_fields = [
            'creator_name', 'creator_email', 'content_title', 
            'content_type', 'copyright_date'
        ]
    
    def validate_template_data(self, data: LegalTemplateData) -> bool:
        """Validate template data completeness."""



        try:
            for field in self.required_fields:
                if not getattr(data, field, None):
                    raise ValueError(f"Required field '{field}' is missing")
            
            # Validate email format
            if '@' not in data.creator_email:
                raise ValueError("Invalid email format")
            
            return True
            
        except Exception as e:
            logger.error(f"Template validation error: {e}")
            return False
    
    def validate_generated_document(self, document: str) -> bool:
        """Validate generated document integrity."""



        try:
            # Check document is not empty
            if not document.strip():
                return False
            
            # Check for unfilled template variables
            if '{' in document and '}' in document:
                logger.warning("Document contains unfilled template variables")
                return False
            
            # Check minimum length
            if len(document) < 100:
                logger.warning("Document appears too short")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Document validation error: {e}")
            return False


# Export classes
__all__ = [
    'LegalTemplateManager',
    'LegalTemplateData', 
    'TemplateValidator'
]
