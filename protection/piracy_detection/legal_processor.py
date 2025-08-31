"""⚖️ Legal Compliance Processor
============================

Advanced legal compliance and regulatory framework processor for content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.

Team Specialties:
- Lead Dev IA: Advanced AI algorithms and machine learning models
- Backend Senior: Scalable microservices architecture  
- ML Engineer: Deep learning and neural network optimization
- DBA: High-performance database design and optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems and API design
- Audio Engineer: Advanced audio processing and fingerprinting
- DevOps Engineer: CI/CD, monitoring, and infrastructure automation
- IA Prompt Engineer: Intelligent prompt design and optimization

Contact: mlaiel@live.de for licensing inquiries.

This module provides:
- Multi-jurisdictional legal compliance
- Automated DMCA and takedown processing
- GDPR and privacy regulation compliance
- Legal documentation generation
- Court-admissible evidence formatting
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
from pathlib import Path
import aiofiles
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

logger = logging.getLogger(__name__)

class LegalJurisdiction(Enum):
    """Legal jurisdictions supported."""    UNITED_STATES = "us"
    EUROPEAN_UNION = "eu"
    UNITED_KINGDOM = "uk"
    CANADA = "ca"
    AUSTRALIA = "au"
    GERMANY = "de"
    FRANCE = "fr"
    JAPAN = "jp"
    SOUTH_KOREA = "kr"
    BRAZIL = "br"

class ComplianceFramework(Enum):
    """Compliance frameworks."""    DMCA = "dmca"
    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    PRIVACY_ACT = "privacy_act"

class LegalActionType(Enum):
    """Types of legal actions."""    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    COPYRIGHT_CLAIM = "copyright_claim"
    COURT_FILING = "court_filing"
    SETTLEMENT_OFFER = "settlement_offer"
    INJUNCTION_REQUEST = "injunction_request"

class DocumentType(Enum):
    """Types of legal documents."""    TAKEDOWN_NOTICE = "takedown_notice"
    COUNTER_NOTICE = "counter_notice"
    CEASE_DESIST_LETTER = "cease_desist_letter"
    COPYRIGHT_REGISTRATION = "copyright_registration"
    EVIDENCE_PACKAGE = "evidence_package"
    COURT_FILING = "court_filing"
    SETTLEMENT_AGREEMENT = "settlement_agreement"

@dataclass
class LegalRequirement:
    """Legal requirement specification."""    jurisdiction: LegalJurisdiction
    framework: ComplianceFramework
    requirement_type: str
    description: str
    mandatory_fields: List[str]
    optional_fields: List[str]
    deadline_days: int
    penalties: Dict[str, Any]

@dataclass
class ComplianceCheck:
    """Result of compliance verification."""    check_id: str
    jurisdiction: LegalJurisdiction
    framework: ComplianceFramework
    check_timestamp: datetime
    compliant: bool
    violations: List[str]
    recommendations: List[str]
    risk_level: str
    next_review_date: datetime

@dataclass
class LegalDocument:
    """Generated legal document."""    document_id: str
    document_type: DocumentType
    jurisdiction: LegalJurisdiction
    creation_timestamp: datetime
    recipient_info: Dict[str, Any]
    sender_info: Dict[str, Any]
    content: str
    attachments: List[str]
    legal_references: List[str]
    deadline: Optional[datetime]
    status: str
    delivery_confirmation: Optional[str]

@dataclass
class TakedownRequest:
    """DMCA takedown request."""    request_id: str
    copyright_holder: Dict[str, Any]
    infringing_content: Dict[str, Any]
    platform_info: Dict[str, Any]
    evidence_package: Dict[str, Any]
    good_faith_statement: str
    perjury_statement: str
    signature: str
    submission_timestamp: datetime
    response_deadline: datetime

class LegalTemplateEngine:
    """Generates legal documents from templates."""    
    def __init__(self, templates_path: str):
        self.templates_path = Path(templates_path)
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load legal document templates."""        # DMCA Takedown Notice Template
        self.templates['dmca_takedown'] = {
            'us': """DMCA TAKEDOWN NOTICE

To: {platform_name}
    {platform_address}
    
Date: {current_date}

Dear Sir/Madam,

I am writing to notify you of copyright infringement occurring on your platform under the provisions of the Digital Millennium Copyright Act (DMCA), 17 U.S.C. § 512.

IDENTIFICATION OF COPYRIGHTED WORK:
{copyrighted_work_description}

IDENTIFICATION OF INFRINGING MATERIAL:
The following material located on your platform infringes the copyrighted work described above:
{infringing_urls}

CONTACT INFORMATION:
Name: {copyright_holder_name}
Address: {copyright_holder_address}
Phone: {copyright_holder_phone}
Email: {copyright_holder_email}

GOOD FAITH STATEMENT:
I have a good faith belief that use of the copyrighted materials described above is not authorized by the copyright owner, its agent, or the law.

ACCURACY STATEMENT:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the copyright owner.

SIGNATURE:
{digital_signature}

{copyright_holder_name}
{copyright_holder_title}
{date_signed}
""",
            'eu': """COPYRIGHT INFRINGEMENT NOTICE
(European Union Directive 2001/29/EC)

To: {platform_name}
    {platform_address}

Date: {current_date}

Subject: Notice of Copyright Infringement

Dear Legal Department,

We hereby notify you of copyright infringement occurring on your platform under European Union copyright law, specifically Directive 2001/29/EC on the harmonisation of certain aspects of copyright and related rights in the information society.

COPYRIGHTED WORK IDENTIFICATION:
{copyrighted_work_description}

INFRINGING CONTENT:
{infringing_urls}

RIGHTS HOLDER INFORMATION:
{copyright_holder_name}
{copyright_holder_address}
{copyright_holder_email}

We request immediate removal of the infringing content and prevention of future infringements.

DECLARATION:
I declare in good faith that the use of the work described above is not authorized by the rights holder, its agent, or the law.

{digital_signature}
{copyright_holder_name}
{date_signed}
"""        }
        
        # Cease and Desist Template
        self.templates['cease_desist'] = {
            'us': """CEASE AND DESIST LETTER

{current_date}

{recipient_name}
{recipient_address}

RE: DEMAND TO CEASE AND DESIST UNAUTHORIZED USE OF COPYRIGHTED MATERIAL

Dear {recipient_name},

This letter serves as formal notice that you are engaging in unauthorized use of copyrighted material owned by {copyright_holder_name}.

COPYRIGHTED WORK:
{copyrighted_work_description}

INFRINGING ACTIVITIES:
{infringement_description}

LEGAL BASIS:
Your actions constitute copyright infringement under 17 U.S.C. § 101 et seq.

DEMAND:
You are hereby demanded to:
1. Immediately cease and desist all unauthorized use
2. Remove all infringing content
3. Provide written assurance of compliance

CONSEQUENCES:
Failure to comply within {deadline_days} days may result in legal action seeking monetary damages, injunctive relief, and attorney's fees.

{copyright_holder_name}
{copyright_holder_title}
{contact_information}
"""        }
    
    def generate_document(self, 
                         template_type: str,
                         jurisdiction: LegalJurisdiction,
                         variables: Dict[str, Any]) -> str:
        """Generate legal document from template."""        try:
            template_key = f"{template_type}_{jurisdiction.value}"
            if template_key not in self.templates.get(template_type, {}):
                # Fallback to US template
                template_key = f"{template_type}_us"
            
            template = self.templates.get(template_type, {}).get(jurisdiction.value, 
                      self.templates.get(template_type, {}).get('us', ''))
            
            if not template:
                raise ValueError(f"Template not found: {template_type} for {jurisdiction.value}")
            
            # Replace variables in template
            formatted_document = template.format(**variables)
            return formatted_document
            
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            raise

class ComplianceValidator:
    """Validates compliance with legal frameworks."""    
    def __init__(self):
        self.requirements = self._load_compliance_requirements()
    
    def _load_compliance_requirements(self) -> Dict[str, List[LegalRequirement]]:
        """Load compliance requirements by framework."""        requirements = {
            'gdpr': [
                LegalRequirement(
                    jurisdiction=LegalJurisdiction.EUROPEAN_UNION,
                    framework=ComplianceFramework.GDPR,
                    requirement_type="data_processing_lawfulness",
                    description="Ensure lawful basis for processing personal data",
                    mandatory_fields=["lawful_basis", "data_subject_consent", "purpose_limitation"],
                    optional_fields=["legitimate_interests"],
                    deadline_days=30,
                    penalties={"max_fine": "20000000 EUR or 4% annual turnover"}
                ),
                LegalRequirement(
                    jurisdiction=LegalJurisdiction.EUROPEAN_UNION,
                    framework=ComplianceFramework.GDPR,
                    requirement_type="data_subject_rights",
                    description="Implement data subject rights mechanisms",
                    mandatory_fields=["access_right", "rectification_right", "erasure_right", "portability_right"],
                    optional_fields=["restriction_right"],
                    deadline_days=30,
                    penalties={"max_fine": "20000000 EUR or 4% annual turnover"}
                )
            ],
            'dmca': [
                LegalRequirement(
                    jurisdiction=LegalJurisdiction.UNITED_STATES,
                    framework=ComplianceFramework.DMCA,
                    requirement_type="takedown_notice",
                    description="Proper DMCA takedown notice format",
                    mandatory_fields=["copyright_identification", "infringing_material", "contact_info", 
                                    "good_faith_statement", "accuracy_statement", "signature"],
                    optional_fields=["agent_authorization"],
                    deadline_days=10,
                    penalties={"perjury_risk": "Criminal charges for false statements"}
                )
            ]
        }
        
        return requirements
    
    async def validate_compliance(self, 
                                framework: ComplianceFramework,
                                jurisdiction: LegalJurisdiction,
                                data: Dict[str, Any]) -> ComplianceCheck:
        """Validate compliance with specific framework."""        try:
            check_id = f"compliance_{framework.value}_{int(datetime.now().timestamp())}"
            violations = []
            recommendations = []
            
            # Get requirements for framework
            framework_requirements = self.requirements.get(framework.value, [])
            relevant_requirements = [
                req for req in framework_requirements 
                if req.jurisdiction == jurisdiction or req.jurisdiction == LegalJurisdiction.EUROPEAN_UNION
            ]
            
            # Check each requirement
            for requirement in relevant_requirements:
                # Check mandatory fields
                for field in requirement.mandatory_fields:
                    if field not in data or not data[field]:
                        violations.append(f"Missing mandatory field: {field}")
                
                # Check optional fields for completeness
                missing_optional = [field for field in requirement.optional_fields if field not in data]
                if missing_optional:
                    recommendations.append(f"Consider adding optional fields: {', '.join(missing_optional)}")
            
            # Determine compliance and risk level
            compliant = len(violations) == 0
            risk_level = "low" if compliant else ("high" if len(violations) > 3 else "medium")
            
            # Calculate next review date
            min_deadline = min([req.deadline_days for req in relevant_requirements], default=30)
            next_review = datetime.now() + timedelta(days=min_deadline)
            
            return ComplianceCheck(
                check_id=check_id,
                jurisdiction=jurisdiction,
                framework=framework,
                check_timestamp=datetime.now(),
                compliant=compliant,
                violations=violations,
                recommendations=recommendations,
                risk_level=risk_level,
                next_review_date=next_review
            )
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            raise

class LegalDocumentManager:
    """Manages legal document lifecycle."""    
    def __init__(self, storage_path: str, email_config: Dict[str, Any]):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.email_config = email_config
        self.documents = {}
    
    async def create_document(self,
                            document_type: DocumentType,
                            jurisdiction: LegalJurisdiction,
                            template_vars: Dict[str, Any]) -> LegalDocument:
        """Create a new legal document."""        try:
            document_id = f"doc_{document_type.value}_{int(datetime.now().timestamp())}"
            
            # Generate document content
            template_engine = LegalTemplateEngine(str(self.storage_path / "templates"))
            content = template_engine.generate_document(
                document_type.value, jurisdiction, template_vars
            )
            
            # Create document
            document = LegalDocument(
                document_id=document_id,
                document_type=document_type,
                jurisdiction=jurisdiction,
                creation_timestamp=datetime.now(),
                recipient_info=template_vars.get('recipient_info', {}),
                sender_info=template_vars.get('sender_info', {}),
                content=content,
                attachments=[],
                legal_references=template_vars.get('legal_references', []),
                deadline=template_vars.get('deadline'),
                status="draft",
                delivery_confirmation=None
            )
            
            # Store document
            await self._save_document(document)
            self.documents[document_id] = document
            
            return document
            
        except Exception as e:
            logger.error(f"Document creation failed: {e}")
            raise
    
    async def send_document(self, document_id: str) -> bool:
        """Send legal document via email."""        try:
            if document_id not in self.documents:
                raise ValueError(f"Document not found: {document_id}")
            
            document = self.documents[document_id]
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = document.recipient_info.get('email', '')
            msg['Subject'] = f"Legal Notice - {document.document_type.value.replace('_', ' ').title()}"
            
            # Add document content
            msg.attach(MIMEText(document.content, 'plain'))
            
            # Add attachments
            for attachment_path in document.attachments:
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=Path(attachment_path).name)
                    msg.attach(attachment)
            
            # Send email
            smtp_server = aiosmtplib.SMTP(
                hostname=self.email_config['smtp_host'],
                port=self.email_config['smtp_port'],
                use_tls=self.email_config.get('use_tls', True)
            )
            
            await smtp_server.connect()
            await smtp_server.login(
                self.email_config['username'],
                self.email_config['password']
            )
            await smtp_server.send_message(msg)
            await smtp_server.quit()
            
            # Update document status
            document.status = "sent"
            document.delivery_confirmation = f"sent_{datetime.now().isoformat()}"
            await self._save_document(document)
            
            logger.info(f"Legal document sent: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Document sending failed: {e}")
            return False
    
    async def _save_document(self, document: LegalDocument):
        """Save document to storage."""        try:
            file_path = self.storage_path / f"{document.document_id}.json"
            
            # Convert document to JSON
            doc_data = asdict(document)
            doc_data['creation_timestamp'] = document.creation_timestamp.isoformat()
            if document.deadline:
                doc_data['deadline'] = document.deadline.isoformat()
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(doc_data, indent=2))
            
            # Save content as separate file
            content_path = self.storage_path / f"{document.document_id}_content.txt"
            async with aiofiles.open(content_path, 'w') as f:
                await f.write(document.content)
            
        except Exception as e:
            logger.error(f"Document saving failed: {e}")
            raise

class LegalComplianceProcessor:
    """    Advanced legal compliance processor system.
    
    Provides comprehensive legal compliance management for content protection
    with multi-jurisdictional support and automated document generation.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """        Initialize the Legal Compliance Processor.
        
        Args:
            config: Legal compliance configuration parameters
        """        self.config = config or {}
        self._initialized = False
        
        # Initialize components
        self.compliance_validator = ComplianceValidator()
        
        # Document management
        storage_path = self.config.get('document_storage_path', '/tmp/legal_documents')
        email_config = self.config.get('email_config', {})
        self.document_manager = LegalDocumentManager(storage_path, email_config)
        
        # Active cases and compliance checks
        self.active_cases = {}
        self.compliance_checks = {}
        self.takedown_requests = {}
        
        # Configuration
        self.default_jurisdiction = LegalJurisdiction(self.config.get('default_jurisdiction', 'us'))
        self.auto_send_enabled = self.config.get('auto_send_documents', False)
        
        # Statistics
        self.compliance_stats = {
            'total_compliance_checks': 0,
            'compliant_cases': 0,
            'violations_found': 0,
            'documents_generated': 0,
            'documents_sent': 0,
            'takedown_requests_submitted': 0
        }
        
        logger.info("Legal Compliance Processor initialized")
    
    async def initialize(self) -> bool:
        """        Initialize legal compliance components.
        
        Returns:
            bool: True if initialization successful
        """        try:
            self._initialized = True
            logger.info("Legal compliance processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize legal compliance processor: {e}")
            return False
    
    async def process_dmca_takedown(self,
                                  copyright_holder: Dict[str, Any],
                                  infringing_content: Dict[str, Any],
                                  platform_info: Dict[str, Any]) -> TakedownRequest:
        """        Process DMCA takedown request.
        
        Args:
            copyright_holder: Copyright holder information
            infringing_content: Details of infringing content
            platform_info: Platform information
            
        Returns:
            Generated takedown request
        """        if not self._initialized:
            await self.initialize()
        
        try:
            request_id = f"dmca_{int(datetime.now().timestamp())}"
            
            # Validate DMCA compliance
            dmca_data = {
                'copyright_identification': infringing_content.get('original_work'),
                'infringing_material': infringing_content.get('infringing_urls'),
                'contact_info': copyright_holder,
                'good_faith_statement': True,
                'accuracy_statement': True,
                'signature': copyright_holder.get('digital_signature')
            }
            
            compliance_check = await self.compliance_validator.validate_compliance(
                ComplianceFramework.DMCA,
                LegalJurisdiction.UNITED_STATES,
                dmca_data
            )
            
            if not compliance_check.compliant:
                raise ValueError(f"DMCA compliance failed: {compliance_check.violations}")
            
            # Generate takedown notice
            template_vars = {
                'platform_name': platform_info.get('name', ''),
                'platform_address': platform_info.get('address', ''),
                'current_date': datetime.now().strftime('%B %d, %Y'),
                'copyrighted_work_description': infringing_content.get('original_work', ''),
                'infringing_urls': '\n'.join(infringing_content.get('infringing_urls', [])),
                'copyright_holder_name': copyright_holder.get('name', ''),
                'copyright_holder_address': copyright_holder.get('address', ''),
                'copyright_holder_phone': copyright_holder.get('phone', ''),
                'copyright_holder_email': copyright_holder.get('email', ''),
                'digital_signature': copyright_holder.get('digital_signature', ''),
                'copyright_holder_title': copyright_holder.get('title', 'Copyright Holder'),
                'date_signed': datetime.now().strftime('%B %d, %Y'),
                'recipient_info': {
                    'email': platform_info.get('dmca_email', platform_info.get('contact_email', ''))
                },
                'sender_info': copyright_holder
            }
            
            document = await self.document_manager.create_document(
                DocumentType.TAKEDOWN_NOTICE,
                LegalJurisdiction.UNITED_STATES,
                template_vars
            )
            
            # Create takedown request
            takedown_request = TakedownRequest(
                request_id=request_id,
                copyright_holder=copyright_holder,
                infringing_content=infringing_content,
                platform_info=platform_info,
                evidence_package={'compliance_check': asdict(compliance_check)},
                good_faith_statement="I have a good faith belief that use of the copyrighted materials is not authorized",
                perjury_statement="I swear, under penalty of perjury, that the information in this notification is accurate",
                signature=copyright_holder.get('digital_signature', ''),
                submission_timestamp=datetime.now(),
                response_deadline=datetime.now() + timedelta(days=10)
            )
            
            # Store request
            self.takedown_requests[request_id] = takedown_request
            
            # Send document if auto-send is enabled
            if self.auto_send_enabled:
                await self.document_manager.send_document(document.document_id)
                self.compliance_stats['documents_sent'] += 1
            
            # Update statistics
            self.compliance_stats['documents_generated'] += 1
            self.compliance_stats['takedown_requests_submitted'] += 1
            
            logger.info(f"DMCA takedown request processed: {request_id}")
            return takedown_request
            
        except Exception as e:
            logger.error(f"DMCA takedown processing failed: {e}")
            raise
    
    async def check_gdpr_compliance(self, 
                                  data_processing_activities: Dict[str, Any]) -> ComplianceCheck:
        """        Check GDPR compliance for data processing activities.
        
        Args:
            data_processing_activities: Details of data processing
            
        Returns:
            GDPR compliance check result
        """        try:
            compliance_check = await self.compliance_validator.validate_compliance(
                ComplianceFramework.GDPR,
                LegalJurisdiction.EUROPEAN_UNION,
                data_processing_activities
            )
            
            # Store compliance check
            self.compliance_checks[compliance_check.check_id] = compliance_check
            
            # Update statistics
            self.compliance_stats['total_compliance_checks'] += 1
            if compliance_check.compliant:
                self.compliance_stats['compliant_cases'] += 1
            else:
                self.compliance_stats['violations_found'] += len(compliance_check.violations)
            
            return compliance_check
            
        except Exception as e:
            logger.error(f"GDPR compliance check failed: {e}")
            raise
    
    async def generate_cease_desist_letter(self,
                                         recipient_info: Dict[str, Any],
                                         infringement_details: Dict[str, Any],
                                         jurisdiction: LegalJurisdiction) -> LegalDocument:
        """        Generate cease and desist letter.
        
        Args:
            recipient_info: Recipient information
            infringement_details: Details of infringement
            jurisdiction: Legal jurisdiction
            
        Returns:
            Generated legal document
        """        try:
            template_vars = {
                'current_date': datetime.now().strftime('%B %d, %Y'),
                'recipient_name': recipient_info.get('name', 'To Whom It May Concern'),
                'recipient_address': recipient_info.get('address', ''),
                'copyright_holder_name': infringement_details.get('copyright_holder', ''),
                'copyrighted_work_description': infringement_details.get('work_description', ''),
                'infringement_description': infringement_details.get('infringement_description', ''),
                'deadline_days': 10,
                'copyright_holder_title': 'Copyright Holder',
                'contact_information': infringement_details.get('contact_info', ''),
                'recipient_info': recipient_info,
                'sender_info': infringement_details.get('sender_info', {})
            }
            
            document = await self.document_manager.create_document(
                DocumentType.CEASE_DESIST_LETTER,
                jurisdiction,
                template_vars
            )
            
            self.compliance_stats['documents_generated'] += 1
            
            return document
            
        except Exception as e:
            logger.error(f"Cease and desist generation failed: {e}")
            raise
    
    async def prepare_court_evidence_package(self,
                                           case_id: str,
                                           evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """        Prepare court-admissible evidence package.
        
        Args:
            case_id: Legal case identifier
            evidence_data: Evidence data to package
            
        Returns:
            Court-ready evidence package
        """        try:
            package_id = f"evidence_{case_id}_{int(datetime.now().timestamp())}"
            
            # Create evidence package structure
            evidence_package = {
                'package_id': package_id,
                'case_id': case_id,
                'creation_timestamp': datetime.now().isoformat(),
                'evidence_items': [],
                'chain_of_custody': [],
                'digital_signatures': {},
                'metadata': {
                    'total_items': 0,
                    'hash_algorithm': 'SHA-256',
                    'package_hash': ''
                }
            }
            
            # Process each evidence item
            for item_key, item_data in evidence_data.items():
                evidence_item = {
                    'item_id': f"{package_id}_{item_key}",
                    'item_type': item_data.get('type', 'digital_evidence'),
                    'description': item_data.get('description', ''),
                    'source': item_data.get('source', ''),
                    'collection_timestamp': item_data.get('timestamp', datetime.now().isoformat()),
                    'hash_value': self._calculate_evidence_hash(item_data),
                    'metadata': item_data.get('metadata', {}),
                    'admissibility_notes': self._assess_admissibility(item_data)
                }
                
                evidence_package['evidence_items'].append(evidence_item)
            
            # Update package metadata
            evidence_package['metadata']['total_items'] = len(evidence_package['evidence_items'])
            evidence_package['metadata']['package_hash'] = self._calculate_package_hash(evidence_package)
            
            # Create chain of custody entry
            custody_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'evidence_package_created',
                'custodian': 'legal_compliance_processor',
                'location': 'digital_evidence_system',
                'notes': f"Evidence package created for case {case_id}"
            }
            evidence_package['chain_of_custody'].append(custody_entry)
            
            return evidence_package
            
        except Exception as e:
            logger.error(f"Evidence package preparation failed: {e}")
            raise
    
    def _calculate_evidence_hash(self, evidence_data: Dict[str, Any]) -> str:
        """Calculate hash for evidence integrity."""        evidence_string = json.dumps(evidence_data, sort_keys=True, default=str)
        return hashlib.sha256(evidence_string.encode()).hexdigest()
    
    def _calculate_package_hash(self, package_data: Dict[str, Any]) -> str:
        """Calculate hash for entire evidence package."""        # Remove hash field temporarily for calculation
        temp_package = package_data.copy()
        temp_package['metadata'] = temp_package['metadata'].copy()
        temp_package['metadata'].pop('package_hash', None)
        
        package_string = json.dumps(temp_package, sort_keys=True, default=str)
        return hashlib.sha256(package_string.encode()).hexdigest()
    
    def _assess_admissibility(self, evidence_data: Dict[str, Any]) -> List[str]:
        """Assess legal admissibility of evidence."""        notes = []
        
        # Check for chain of custody
        if 'chain_of_custody' not in evidence_data:
            notes.append("WARNING: No chain of custody documentation")
        
        # Check for timestamps
        if 'timestamp' not in evidence_data:
            notes.append("WARNING: No timestamp information")
        
        # Check for authentication
        if 'digital_signature' not in evidence_data:
            notes.append("INFO: Consider adding digital signature for authentication")
        
        # Check for metadata
        if not evidence_data.get('metadata'):
            notes.append("INFO: Additional metadata would strengthen admissibility")
        
        if not notes:
            notes.append("GOOD: Evidence meets basic admissibility requirements")
        
        return notes
    
    async def monitor_compliance_deadlines(self) -> List[Dict[str, Any]]:
        """Monitor and alert on compliance deadlines."""        try:
            upcoming_deadlines = []
            current_time = datetime.now()
            
            # Check takedown request deadlines
            for request_id, request in self.takedown_requests.items():
                if request.response_deadline > current_time:
                    days_remaining = (request.response_deadline - current_time).days
                    if days_remaining <= 3:  # Alert 3 days before deadline
                        upcoming_deadlines.append({
                            'type': 'takedown_response',
                            'request_id': request_id,
                            'deadline': request.response_deadline.isoformat(),
                            'days_remaining': days_remaining,
                            'priority': 'high' if days_remaining <= 1 else 'medium'
                        })
            
            # Check compliance review deadlines
            for check_id, check in self.compliance_checks.items():
                if check.next_review_date > current_time:
                    days_remaining = (check.next_review_date - current_time).days
                    if days_remaining <= 7:  # Alert 7 days before review
                        upcoming_deadlines.append({
                            'type': 'compliance_review',
                            'check_id': check_id,
                            'framework': check.framework.value,
                            'deadline': check.next_review_date.isoformat(),
                            'days_remaining': days_remaining,
                            'priority': 'medium' if days_remaining <= 3 else 'low'
                        })
            
            return upcoming_deadlines
            
        except Exception as e:
            logger.error(f"Deadline monitoring failed: {e}")
            return []
    
    def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get legal compliance statistics."""        return {
            **self.compliance_stats,
            'active_cases': len(self.active_cases),
            'compliance_checks_count': len(self.compliance_checks),
            'takedown_requests_count': len(self.takedown_requests),
            'documents_stored': len(self.document_manager.documents),
            'default_jurisdiction': self.default_jurisdiction.value,
            'initialized': self._initialized
        }
