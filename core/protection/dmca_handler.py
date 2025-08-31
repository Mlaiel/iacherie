"""DMCA Takedown Handler for Automated Copyright Protection

This module provides automated DMCA takedown request generation and submission:
- Automated DMCA notice generation with legal templates
- Platform-specific takedown request submission
- Legal compliance verification and documentation
- Tracking and follow-up for takedown requests
- Integration with legal databases and services

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import json
import aiohttp
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
from pathlib import Path
import hashlib
import uuid
from urllib.parse import urlparse, urljoin

# PDF generation
import weasyprint
from jinja2 import Environment, FileSystemLoader

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, DMCATakedown
from ...config.settings import get_settings
from .violation_detector import ViolationEvidence, ViolationType, ViolationSeverity
from .evidence_collector import EvidenceData

logger = get_logger(__name__)
settings = get_settings()


class TakedownStatus(Enum):
    """Status of DMCA takedown requests"""    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    APPEALED = "appealed"
    COUNTER_NOTICE = "counter_notice"


class PlatformType(Enum):
    """Supported platforms for DMCA submissions"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    GENERIC_HOST = "generic_host"


@dataclass
class ContactInformation:
    """Contact information for DMCA notices"""    name: str
    company: Optional[str] = None
    address: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""
    email: str = ""
    phone: str = ""
    
    def to_formatted_string(self) -> str:
        """Format contact info for legal documents"""        lines = [self.name]
        if self.company:
            lines.append(self.company)
        if self.address:
            lines.append(self.address)
        if self.city or self.state or self.postal_code:
            location = ", ".join(filter(None, [self.city, self.state, self.postal_code]))
            lines.append(location)
        if self.country:
            lines.append(self.country)
        if self.email:
            lines.append(f"Email: {self.email}")
        if self.phone:
            lines.append(f"Phone: {self.phone}")
        return "\n".join(lines)


@dataclass
class DMCANotice:
    """DMCA takedown notice data structure"""    notice_id: str
    violation_evidence: ViolationEvidence
    
    # Legal information
    copyright_owner: ContactInformation
    authorized_agent: Optional[ContactInformation] = None
    
    # Content identification
    original_work_description: str = ""
    copyrighted_work_location: str = ""
    infringing_material_location: str = ""
    infringing_material_description: str = ""
    
    # Legal statements
    good_faith_statement: str = ""
    accuracy_statement: str = ""
    authority_statement: str = ""
    
    # Metadata
    platform: PlatformType = PlatformType.GENERIC_HOST
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: TakedownStatus = TakedownStatus.DRAFT
    
    # Tracking
    submission_reference: Optional[str] = None
    platform_case_id: Optional[str] = None
    response_received: Optional[datetime] = None
    
    # Documentation
    evidence_files: List[str] = field(default_factory=list)
    generated_notice_path: Optional[str] = None


@dataclass
class PlatformConfig:
    """Configuration for platform-specific DMCA submission"""    platform: PlatformType
    submission_url: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    
    # Form field mappings
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Submission requirements
    requires_sworn_statement: bool = True
    requires_physical_signature: bool = False
    supports_bulk_submission: bool = False
    max_urls_per_submission: int = 1
    
    # Response handling
    acknowledgment_email_patterns: List[str] = field(default_factory=list)
    case_id_patterns: List[str] = field(default_factory=list)


class DMCATemplateEngine:
    """Template engine for generating DMCA notices"""    
    def __init__(self):
        template_dir = Path(__file__).parent / "templates" / "dmca"
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Load default templates if not exists
        self._ensure_templates_exist()
    
    def _ensure_templates_exist(self):
        """Ensure DMCA templates exist"""        template_dir = Path(__file__).parent / "templates" / "dmca"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic DMCA template if it doesn't exist
        basic_template_path = template_dir / "basic_dmca_notice.html"
        if not basic_template_path.exists():
            self._create_basic_template(basic_template_path)
    
    def _create_basic_template(self, template_path: Path):
        """Create basic DMCA notice template"""        template_content = """<!DOCTYPE html>
<html>
<head>
    <title>DMCA Takedown Notice</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 20px; }
        .signature { margin-top: 40px; }
        .footer { margin-top: 50px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DMCA TAKEDOWN NOTICE</h1>
        <p>Digital Millennium Copyright Act (17 U.S.C. § 512)</p>
    </div>
    
    <div class="section">
        <h3>To: {{ platform_name }}</h3>
        <p>Date: {{ notice_date }}</p>
        <p>Notice ID: {{ notice_id }}</p>
    </div>
    
    <div class="section">
        <h3>COPYRIGHT OWNER INFORMATION</h3>
        <pre>{{ copyright_owner_info }}</pre>
    </div>
    
    {% if authorized_agent %}
    <div class="section">
        <h3>AUTHORIZED AGENT INFORMATION</h3>
        <pre>{{ authorized_agent_info }}</pre>
    </div>
    {% endif %}
    
    <div class="section">
        <h3>IDENTIFICATION OF COPYRIGHTED WORK</h3>
        <p>{{ original_work_description }}</p>
        <p><strong>Original work location:</strong> {{ copyrighted_work_location }}</p>
    </div>
    
    <div class="section">
        <h3>IDENTIFICATION OF INFRINGING MATERIAL</h3>
        <p>{{ infringing_material_description }}</p>
        <p><strong>Infringing material URL:</strong> {{ infringing_material_location }}</p>
    </div>
    
    <div class="section">
        <h3>GOOD FAITH STATEMENT</h3>
        <p>{{ good_faith_statement }}</p>
    </div>
    
    <div class="section">
        <h3>ACCURACY STATEMENT</h3>
        <p>{{ accuracy_statement }}</p>
    </div>
    
    <div class="section">
        <h3>AUTHORITY STATEMENT</h3>
        <p>{{ authority_statement }}</p>
    </div>
    
    <div class="signature">
        <p><strong>Electronic Signature:</strong> {{ signature_name }}</p>
        <p><strong>Date:</strong> {{ signature_date }}</p>
    </div>
    
    <div class="footer">
        <p>This notice is submitted in good faith compliance with the Digital Millennium Copyright Act.</p>
        <p>Generated by IA Influencer Agent Protection System</p>
    </div>
</body>
</html>
        """.strip()
        
        template_path.write_text(template_content)
    
    def generate_notice_html(self, dmca_notice: DMCANotice) -> str:
        """Generate HTML DMCA notice"""        try:
            template = self.template_env.get_template("basic_dmca_notice.html")
            
            # Prepare template variables
            template_vars = {
                'notice_id': dmca_notice.notice_id,
                'notice_date': dmca_notice.created_at.strftime("%B %d, %Y"),
                'platform_name': self._get_platform_name(dmca_notice.platform),
                'copyright_owner_info': dmca_notice.copyright_owner.to_formatted_string(),
                'authorized_agent_info': dmca_notice.authorized_agent.to_formatted_string() if dmca_notice.authorized_agent else None,
                'original_work_description': dmca_notice.original_work_description,
                'copyrighted_work_location': dmca_notice.copyrighted_work_location,
                'infringing_material_description': dmca_notice.infringing_material_description,
                'infringing_material_location': dmca_notice.infringing_material_location,
                'good_faith_statement': dmca_notice.good_faith_statement,
                'accuracy_statement': dmca_notice.accuracy_statement,
                'authority_statement': dmca_notice.authority_statement,
                'signature_name': dmca_notice.copyright_owner.name,
                'signature_date': datetime.utcnow().strftime("%B %d, %Y")
            }
            
            return template.render(**template_vars)
            
        except Exception as e:
            logger.error(f"Error generating DMCA notice HTML: {e}")
            raise
    
    def generate_notice_pdf(self, dmca_notice: DMCANotice) -> Path:
        """Generate PDF DMCA notice"""        try:
            # Generate HTML first
            html_content = self.generate_notice_html(dmca_notice)
            
            # Create output directory
            output_dir = Path("dmca_notices")
            output_dir.mkdir(exist_ok=True)
            
            # Generate PDF filename
            pdf_filename = f"dmca_notice_{dmca_notice.notice_id}_{int(datetime.utcnow().timestamp())}.pdf"
            pdf_path = output_dir / pdf_filename
            
            # Convert HTML to PDF
            weasyprint.HTML(string=html_content).write_pdf(pdf_path)
            
            logger.info(f"Generated DMCA notice PDF: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating DMCA notice PDF: {e}")
            raise
    
    def _get_platform_name(self, platform: PlatformType) -> str:
        """Get formatted platform name"""        platform_names = {
            PlatformType.YOUTUBE: "YouTube (Google LLC)",
            PlatformType.INSTAGRAM: "Instagram (Meta Platforms, Inc.)",
            PlatformType.TIKTOK: "TikTok (ByteDance Ltd.)",
            PlatformType.TWITTER: "Twitter/X (X Corp.)",
            PlatformType.FACEBOOK: "Facebook (Meta Platforms, Inc.)",
            PlatformType.SPOTIFY: "Spotify Technology S.A.",
            PlatformType.SOUNDCLOUD: "SoundCloud Limited",
            PlatformType.GENERIC_HOST: "Service Provider"
        }
        return platform_names.get(platform, "Service Provider")


class PlatformSubmitter:
    """Handle platform-specific DMCA submission"""    
    def __init__(self):
        self.platform_configs = self._load_platform_configs()
    
    def _load_platform_configs(self) -> Dict[PlatformType, PlatformConfig]:
        """Load platform-specific configurations"""        configs = {}
        
        # YouTube configuration
        configs[PlatformType.YOUTUBE] = PlatformConfig(
            platform=PlatformType.YOUTUBE,
            submission_url="https://www.youtube.com/copyright_complaint_form",
            field_mappings={
                'copyright_owner': 'complainant_name',
                'infringing_url': 'video_url',
                'original_work': 'work_description'
            },
            requires_sworn_statement=True,
            max_urls_per_submission=10,
            case_id_patterns=[r'Case #(\d+)', r'Reference: ([A-Z0-9]+)']
        )
        
        # Instagram configuration
        configs[PlatformType.INSTAGRAM] = PlatformConfig(
            platform=PlatformType.INSTAGRAM,
            submission_url="https://help.instagram.com/contact/372592039493026",
            field_mappings={
                'copyright_owner': 'full_name',
                'infringing_url': 'content_url',
                'description': 'additional_info'
            },
            requires_sworn_statement=True,
            max_urls_per_submission=5
        )
        
        # TikTok configuration
        configs[PlatformType.TIKTOK] = PlatformConfig(
            platform=PlatformType.TIKTOK,
            submission_url="https://www.tiktok.com/legal/report/Copyright",
            field_mappings={
                'reporter_name': 'full_name',
                'infringing_content': 'video_url',
                'original_content': 'original_work_url'
            },
            requires_sworn_statement=True
        )
        
        return configs
    
    async def submit_dmca_notice(self, dmca_notice: DMCANotice) -> bool:
        """Submit DMCA notice to platform"""        try:
            config = self.platform_configs.get(dmca_notice.platform)
            if not config:
                logger.error(f"No configuration for platform {dmca_notice.platform}")
                return False
            
            if config.api_endpoint:
                return await self._submit_via_api(dmca_notice, config)
            else:
                return await self._submit_via_web_form(dmca_notice, config)
                
        except Exception as e:
            logger.error(f"Error submitting DMCA notice: {e}")
            return False
    
    async def _submit_via_api(self, dmca_notice: DMCANotice, config: PlatformConfig) -> bool:
        """Submit via platform API"""        try:
            # Prepare API payload
            payload = {
                'notice_id': dmca_notice.notice_id,
                'copyright_owner': asdict(dmca_notice.copyright_owner),
                'infringing_url': dmca_notice.infringing_material_location,
                'original_work_description': dmca_notice.original_work_description,
                'good_faith_statement': dmca_notice.good_faith_statement
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'IA-Influencer-Agent/2.0 DMCA-Handler'
            }
            
            if config.api_key:
                headers['Authorization'] = f'Bearer {config.api_key}'
            elif config.auth_token:
                headers['X-Auth-Token'] = config.auth_token
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.api_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status < 400:
                        response_data = await response.json()
                        
                        # Extract case ID if available
                        case_id = response_data.get('case_id') or response_data.get('reference_id')
                        if case_id:
                            dmca_notice.platform_case_id = case_id
                        
                        dmca_notice.status = TakedownStatus.SUBMITTED
                        dmca_notice.submission_reference = response_data.get('submission_id', dmca_notice.notice_id)
                        
                        logger.info(f"DMCA notice submitted via API: {dmca_notice.notice_id}")
                        return True
                    else:
                        logger.error(f"API submission failed: {response.status}")
                        return False
            
        except Exception as e:
            logger.error(f"Error in API submission: {e}")
            return False
    
    async def _submit_via_web_form(self, dmca_notice: DMCANotice, config: PlatformConfig) -> bool:
        """Submit via web form (using Selenium)"""        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
            
            # Setup Chrome driver
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to submission form
                driver.get(config.submission_url)
                await asyncio.sleep(3)  # Wait for page load
                
                # Fill form fields based on platform mapping
                field_mappings = config.field_mappings
                
                # Copyright owner name
                if 'copyright_owner' in field_mappings:
                    name_field = driver.find_element(By.NAME, field_mappings['copyright_owner'])
                    name_field.send_keys(dmca_notice.copyright_owner.name)
                
                # Email
                if dmca_notice.copyright_owner.email:
                    email_field = driver.find_element(By.NAME, 'email')
                    email_field.send_keys(dmca_notice.copyright_owner.email)
                
                # Infringing URL
                if 'infringing_url' in field_mappings:
                    url_field = driver.find_element(By.NAME, field_mappings['infringing_url'])
                    url_field.send_keys(dmca_notice.infringing_material_location)
                
                # Description
                if 'description' in field_mappings:
                    desc_field = driver.find_element(By.NAME, field_mappings['description'])
                    desc_field.send_keys(dmca_notice.infringing_material_description)
                
                # Original work description
                if 'original_work' in field_mappings:
                    original_field = driver.find_element(By.NAME, field_mappings['original_work'])
                    original_field.send_keys(dmca_notice.original_work_description)
                
                # Good faith statement checkbox
                try:
                    good_faith_checkbox = driver.find_element(By.NAME, 'good_faith')
                    good_faith_checkbox.click()
                except:
                    pass  # Some platforms don't have explicit checkbox
                
                # Accuracy statement checkbox
                try:
                    accuracy_checkbox = driver.find_element(By.NAME, 'accuracy')
                    accuracy_checkbox.click()
                except:
                    pass
                
                # Submit form
                submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"], button[type="submit"]')
                submit_button.click()
                
                # Wait for confirmation
                await asyncio.sleep(5)
                
                # Check for success indicators
                page_source = driver.page_source.lower()
                success_indicators = ['thank you', 'submitted', 'received', 'confirmation']
                
                if any(indicator in page_source for indicator in success_indicators):
                    dmca_notice.status = TakedownStatus.SUBMITTED
                    logger.info(f"DMCA notice submitted via web form: {dmca_notice.notice_id}")
                    return True
                else:
                    logger.warning(f"Web form submission unclear: {dmca_notice.notice_id}")
                    return False
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error in web form submission: {e}")
            return False


class DMCAHandler:
    """Main DMCA takedown handler"""    
    def __init__(self):
        self.template_engine = DMCATemplateEngine()
        self.platform_submitter = PlatformSubmitter()
        
        # Storage
        self.dmca_notices: Dict[str, DMCANotice] = {}
        
        # Default contact information (should be configured)
        self.default_copyright_owner = ContactInformation(
            name=getattr(settings, 'DMCA_COPYRIGHT_OWNER_NAME', 'Content Owner'),
            email=getattr(settings, 'DMCA_COPYRIGHT_OWNER_EMAIL', 'legal@example.com'),
            address=getattr(settings, 'DMCA_COPYRIGHT_OWNER_ADDRESS', ''),
            city=getattr(settings, 'DMCA_COPYRIGHT_OWNER_CITY', ''),
            country=getattr(settings, 'DMCA_COPYRIGHT_OWNER_COUNTRY', '')
        )
    
    async def submit_takedown_request(self, violation_evidence: ViolationEvidence, evidence_data: Any = None) -> str:
        """Submit automated DMCA takedown request"""        try:
            # Generate notice ID
            notice_id = f"dmca_{violation_evidence.violation_id}_{int(datetime.utcnow().timestamp())}"
            
            # Determine platform
            platform = self._detect_platform(violation_evidence.detected_url)
            
            # Create DMCA notice
            dmca_notice = self._create_dmca_notice(violation_evidence, notice_id, platform)
            
            # Generate legal statements
            self._generate_legal_statements(dmca_notice)
            
            # Generate PDF notice
            pdf_path = self.template_engine.generate_notice_pdf(dmca_notice)
            dmca_notice.generated_notice_path = str(pdf_path)
            
            # Store notice
            self.dmca_notices[notice_id] = dmca_notice
            
            # Submit to platform
            success = await self.platform_submitter.submit_dmca_notice(dmca_notice)
            
            if success:
                logger.info(f"DMCA takedown submitted successfully: {notice_id}")
            else:
                logger.warning(f"DMCA takedown submission failed: {notice_id}")
                dmca_notice.status = TakedownStatus.REJECTED
            
            return notice_id
            
        except Exception as e:
            logger.error(f"Error submitting DMCA takedown: {e}")
            raise
    
    def _detect_platform(self, url: str) -> PlatformType:
        """Detect platform from URL"""        try:
            domain = urlparse(url).netloc.lower()
            
            if 'youtube.com' in domain or 'youtu.be' in domain:
                return PlatformType.YOUTUBE
            elif 'instagram.com' in domain:
                return PlatformType.INSTAGRAM
            elif 'tiktok.com' in domain:
                return PlatformType.TIKTOK
            elif 'twitter.com' in domain or 'x.com' in domain:
                return PlatformType.TWITTER
            elif 'facebook.com' in domain:
                return PlatformType.FACEBOOK
            elif 'spotify.com' in domain:
                return PlatformType.SPOTIFY
            elif 'soundcloud.com' in domain:
                return PlatformType.SOUNDCLOUD
            else:
                return PlatformType.GENERIC_HOST
                
        except Exception:
            return PlatformType.GENERIC_HOST
    
    def _create_dmca_notice(self, violation: ViolationEvidence, notice_id: str, platform: PlatformType) -> DMCANotice:
        """Create DMCA notice from violation evidence"""        dmca_notice = DMCANotice(
            notice_id=notice_id,
            violation_evidence=violation,
            copyright_owner=self.default_copyright_owner,
            platform=platform,
            infringing_material_location=violation.detected_url
        )
        
        # Set descriptions based on violation type
        dmca_notice.original_work_description = self._generate_work_description(violation)
        dmca_notice.infringing_material_description = self._generate_infringement_description(violation)
        
        return dmca_notice
    
    def _generate_work_description(self, violation: ViolationEvidence) -> str:
        """Generate original work description"""        violation_type = violation.violation_type
        
        if violation_type in [ViolationType.EXACT_DUPLICATE, ViolationType.MODIFIED_CONTENT]:
            return f"Original copyrighted content owned by {self.default_copyright_owner.name}, created and published with all rights reserved."
        elif violation_type == ViolationType.DERIVATIVE_WORK:
            return f"Original copyrighted content that has been modified or adapted without authorization."
        elif violation_type == ViolationType.PARTIAL_USAGE:
            return f"Original copyrighted content from which substantial portions have been used without permission."
        else:
            return f"Original copyrighted content protected under copyright law."
    
    def _generate_infringement_description(self, violation: ViolationEvidence) -> str:
        """Generate infringement description"""        max_similarity = max(s.similarity_score for s in violation.similarity_scores) if violation.similarity_scores else 0
        
        description = f"The content located at the specified URL contains copyrighted material that infringes upon the rights of {self.default_copyright_owner.name}. "
        description += f"Analysis shows {max_similarity:.1%} similarity to the original work. "
        description += f"This constitutes {violation.violation_type.value.replace('_', ' ')} "
        description += f"and violates copyright protection under the Digital Millennium Copyright Act."
        
        return description
    
    def _generate_legal_statements(self, dmca_notice: DMCANotice):
        """Generate required legal statements"""        # Good faith statement
        dmca_notice.good_faith_statement = (
            "I have a good faith belief that use of the copyrighted material described above is not authorized "
            "by the copyright owner, its agent, or the law, and therefore infringes the copyright owner's rights."
        )
        
        # Accuracy statement
        dmca_notice.accuracy_statement = (
            "I swear, under penalty of perjury, that the information in this notification is accurate and "
            f"that I am the copyright owner or am authorized to act on behalf of the copyright owner of "
            "an exclusive right that is allegedly infringed."
        )
        
        # Authority statement
        dmca_notice.authority_statement = (
            f"I am authorized to act on behalf of {dmca_notice.copyright_owner.name} with respect to "
            "the copyrighted work that is allegedly being infringed."
        )
    
    def get_takedown_status(self, notice_id: str) -> Optional[Dict[str, Any]]:
        """Get status of DMCA takedown request"""        if notice_id not in self.dmca_notices:
            return None
        
        notice = self.dmca_notices[notice_id]
        
        return {
            'notice_id': notice_id,
            'status': notice.status.value,
            'platform': notice.platform.value,
            'created_at': notice.created_at.isoformat(),
            'submission_reference': notice.submission_reference,
            'platform_case_id': notice.platform_case_id,
            'infringing_url': notice.infringing_material_location,
            'response_received': notice.response_received.isoformat() if notice.response_received else None
        }
    
    def get_dmca_statistics(self) -> Dict[str, Any]:
        """Get DMCA system statistics"""        total_notices = len(self.dmca_notices)
        
        if total_notices == 0:
            return {'total_notices': 0}
        
        status_counts = {}
        platform_counts = {}
        
        for notice in self.dmca_notices.values():
            # Status distribution
            status = notice.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Platform distribution
            platform = notice.platform.value
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Calculate success rate
        successful_statuses = ['submitted', 'acknowledged', 'processing', 'completed']
        successful_notices = sum(status_counts.get(status, 0) for status in successful_statuses)
        success_rate = successful_notices / total_notices if total_notices > 0 else 0
        
        return {
            'total_notices': total_notices,
            'status_distribution': status_counts,
            'platform_distribution': platform_counts,
            'success_rate': success_rate,
            'pending_notices': status_counts.get('pending_review', 0) + status_counts.get('submitted', 0)
        }
