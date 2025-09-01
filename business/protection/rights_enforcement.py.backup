"""Rights Enforcement System
Professional copyright enforcement and violation response system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
import requests
from urllib.parse import urlparse
import hashlib
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of copyright violations"""
    EXACT_COPY = "exact_copy"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_USE = "unauthorized_use"
    COMMERCIAL_USE = "commercial_use"
    PLAGIARISM = "plagiarism"
    FAIR_USE_VIOLATION = "fair_use_violation"


class EnforcementAction(Enum):
    """Types of enforcement actions"""
    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_and_desist"
    PLATFORM_REPORT = "platform_report"
    LEGAL_NOTICE = "legal_notice"
    MONETIZATION_CLAIM = "monetization_claim"
    ACCOUNT_SUSPENSION = "account_suspension"
    CONTENT_REMOVAL = "content_removal"


class EnforcementStatus(Enum):
    """Status of enforcement actions"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    ESCALATED = "escalated"


@dataclass
class ViolationReport:
    """Copyright violation report"""
    violation_id: str
    content_id: str
    violator_info: Dict[str, Any]
    violation_type: ViolationType
    evidence_urls: List[str]
    similarity_score: float
    detection_timestamp: datetime
    violation_url: str
    platform: str
    description: str
    severity_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    owner_id: str


@dataclass
class EnforcementRecord:
    """Record of enforcement action taken"""
    record_id: str
    violation_id: str
    action_type: EnforcementAction
    status: EnforcementStatus
    initiated_at: datetime
    completed_at: Optional[datetime]
    details: Dict[str, Any]
    response_received: Optional[str]
    follow_up_required: bool
    escalation_level: int  # 1-5


class DMCATakedownGenerator:
    """Generate DMCA takedown notices"""
    
    def __init__(self, copyright_holder_info: Dict[str, str]):
        self.copyright_holder = copyright_holder_info
        self.template_path = Path(__file__).parent / "templates"
    
    def generate_dmca_notice(self, violation: ViolationReport) -> str:
        """Generate formal DMCA takedown notice"""
        try:
            notice_template = """DMCA TAKEDOWN NOTICE

Date: {date}

To: Copyright Agent
{platform_name}

Dear Sir/Madam,

I am writing to notify you of copyright infringement occurring on your platform.

COPYRIGHT HOLDER INFORMATION:
Name: {holder_name}
Address: {holder_address}
Email: {holder_email}
Phone: {holder_phone}

INFRINGED WORK:
Title: {work_title}
Description: {work_description}
Original Publication Date: {original_date}
Copyright Registration: {copyright_reg}

INFRINGING MATERIAL:
Location of Infringing Material: {violation_url}
Description of Infringement: {infringement_description}
Similarity Score: {similarity_score}%
Detection Date: {detection_date}

GOOD FAITH STATEMENT:
I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

ACCURACY STATEMENT:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the copyright owner.

SIGNATURE:
{holder_signature}
{holder_name}
{date}

Please remove or disable access to the infringing material within 24 hours of receipt of this notice.

For questions regarding this notice, please contact: {holder_email}
"""
            
            formatted_notice = notice_template.format(
                date=datetime.now().strftime("%B %d, %Y"),
                platform_name=violation.platform.title(),
                holder_name=self.copyright_holder.get('name', 'Fahed Mlaiel'),
                holder_address=self.copyright_holder.get('address', 'Germany'),
                holder_email=self.copyright_holder.get('email', 'mlaiel@live.de'),
                holder_phone=self.copyright_holder.get('phone', 'Available upon request'),
                work_title=violation.description,
                work_description=f"Original content ID: {violation.content_id}",
                original_date=violation.detection_timestamp.strftime("%Y-%m-%d"),
                copyright_reg="Pending/Automatic",
                violation_url=violation.violation_url,
                infringement_description=f"{violation.violation_type.value} - {violation.description}",
                similarity_score=int(violation.similarity_score * 100),
                detection_date=violation.detection_timestamp.strftime("%Y-%m-%d %H:%M UTC"),
                holder_signature="[Digital Signature]"
            )
            
            logger.info(f"Generated DMCA notice for violation {violation.violation_id}")
            return formatted_notice
            
        except Exception as e:
            logger.error(f"Error generating DMCA notice: {str(e)}")
            raise


class CeaseDesistGenerator:
    """Generate cease and desist letters"""
    
    def __init__(self, copyright_holder_info: Dict[str, str]):
        self.copyright_holder = copyright_holder_info
    
    def generate_cease_desist(self, violation: ViolationReport) -> str:
        """Generate formal cease and desist letter"""
        try:
            letter_template = """CEASE AND DESIST LETTER

Date: {date}

To: {violator_name}
{violator_address}

RE: UNAUTHORIZED USE OF COPYRIGHTED MATERIAL

Dear {violator_name},

I am the owner of copyrighted material that you are using without authorization.

COPYRIGHTED WORK:
Content ID: {content_id}
Description: {work_description}
Creation Date: {creation_date}

UNAUTHORIZED USE:
Your unauthorized use was detected at: {violation_url}
Platform: {platform}
Detection Date: {detection_date}
Violation Type: {violation_type}
Similarity to Original: {similarity_score}%

DEMAND:
I hereby demand that you immediately:
1. Remove or disable access to the infringing material
2. Cease all use of my copyrighted work
3. Confirm in writing that you have complied with these demands
4. Provide assurance that you will not infringe my copyright in the future

LEGAL BASIS:
Your use constitutes copyright infringement under applicable copyright laws.

CONSEQUENCES OF NON-COMPLIANCE:
If you do not comply within 7 days of receiving this letter, I will consider taking legal action, including but not limited to:
- Filing a copyright infringement lawsuit
- Seeking monetary damages
- Requesting attorney's fees
- Pursuing injunctive relief

This letter is not a complete statement of my rights, and all rights are expressly reserved.

TIME LIMIT:
You have 7 days from receipt of this letter to comply with these demands.

Sincerely,

{holder_name}
{holder_title}
Email: {holder_email}
Date: {date}

DELIVERY CONFIRMATION REQUESTED
"""
            
            violator_name = violation.violator_info.get('name', 'Unknown User')
            violator_address = violation.violator_info.get('address', 'Address Unknown')
            
            formatted_letter = letter_template.format(
                date=datetime.now().strftime("%B %d, %Y"),
                violator_name=violator_name,
                violator_address=violator_address,
                content_id=violation.content_id,
                work_description=violation.description,
                creation_date=violation.detection_timestamp.strftime("%Y-%m-%d"),
                violation_url=violation.violation_url,
                platform=violation.platform.title(),
                detection_date=violation.detection_timestamp.strftime("%Y-%m-%d"),
                violation_type=violation.violation_type.value.replace('_', ' ').title(),
                similarity_score=int(violation.similarity_score * 100),
                holder_name=self.copyright_holder.get('name', 'Fahed Mlaiel'),
                holder_title=self.copyright_holder.get('title', 'Copyright Owner'),
                holder_email=self.copyright_holder.get('email', 'mlaiel@live.de')
            )
            
            logger.info(f"Generated cease and desist letter for violation {violation.violation_id}")
            return formatted_letter
            
        except Exception as e:
            logger.error(f"Error generating cease and desist letter: {str(e)}")
            raise


class PlatformAPIHandler:
    """Handle platform-specific API interactions for enforcement"""
    
    def __init__(self):
        self.platform_configs = {
            'youtube': {
                'api_endpoint': 'https://www.googleapis.com/youtube/v3/videos/reportAbuse',
                'auth_required': True,
                'rate_limit': 100  # per hour
            },
            'instagram': {
                'api_endpoint': 'https://api.instagram.com/v1/media/report',
                'auth_required': True,
                'rate_limit': 50
            },
            'tiktok': {
                'api_endpoint': 'https://www.tiktok.com/api/abuse/report',
                'auth_required': False,
                'rate_limit': 25
            },
            'facebook': {
                'api_endpoint': 'https://graph.facebook.com/v12.0/report',
                'auth_required': True,
                'rate_limit': 75
            }
        }
    
    async def submit_platform_report(self, violation: ViolationReport, api_credentials: Dict[str, str]) -> Dict[str, Any]:
        """Submit copyright report to platform API"""
        try:
            platform = violation.platform.lower()
            
            if platform not in self.platform_configs:
                raise ValueError(f"Unsupported platform: {platform}")
            
            config = self.platform_configs[platform]
            
            # Prepare report data
            report_data = {
                'content_url': violation.violation_url,
                'violation_type': 'copyright_infringement',
                'description': f"Copyright infringement detected. Similarity: {violation.similarity_score:.2%}",
                'evidence': violation.evidence_urls,
                'contact_email': 'mlaiel@live.de',
                'timestamp': violation.detection_timestamp.isoformat()
            }
            
            # Add platform-specific formatting
            if platform == 'youtube':
                report_data = self._format_youtube_report(report_data, violation)
            elif platform == 'instagram':
                report_data = self._format_instagram_report(report_data, violation)
            elif platform == 'tiktok':
                report_data = self._format_tiktok_report(report_data, violation)
            elif platform == 'facebook':
                report_data = self._format_facebook_report(report_data, violation)
            
            # Submit report
            async with aiohttp.ClientSession() as session:
                headers = self._get_platform_headers(platform, api_credentials)
                
                async with session.post(
                    config['api_endpoint'],
                    json=report_data,
                    headers=headers,
                    timeout=30
                ) as response:
                    
                    result = {
                        'status_code': response.status,
                        'platform': platform,
                        'response_data': await response.json() if response.content_type == 'application/json' else await response.text(),
                        'submission_time': datetime.now(timezone.utc).isoformat(),
                        'success': response.status == 200
                    }
                    
                    if result['success']:
                        logger.info(f"Successfully submitted report to {platform} for violation {violation.violation_id}")
                    else:
                        logger.warning(f"Platform report submission failed: {result}")
                    
                    return result
            
        except Exception as e:
            logger.error(f"Error submitting platform report: {str(e)}")
            raise
    
    def _format_youtube_report(self, base_data: Dict[str, Any], violation: ViolationReport) -> Dict[str, Any]:
        """Format report for YouTube API"""
        return {
            **base_data,
            'reason': 'copyright',
            'video_id': self._extract_youtube_video_id(violation.violation_url)
        }
    
    def _format_instagram_report(self, base_data: Dict[str, Any], violation: ViolationReport) -> Dict[str, Any]:
        """Format report for Instagram API"""
        return {
            **base_data,
            'object_type': 'media',
            'report_type': 'intellectual_property'
        }
    
    def _format_tiktok_report(self, base_data: Dict[str, Any], violation: ViolationReport) -> Dict[str, Any]:
        """Format report for TikTok API"""
        return {
            **base_data,
            'report_reason': 'copyright_infringement',
            'video_url': violation.violation_url
        }
    
    def _format_facebook_report(self, base_data: Dict[str, Any], violation: ViolationReport) -> Dict[str, Any]:
        """Format report for Facebook API"""
        return {
            **base_data,
            'category': 'intellectual_property',
            'subcategory': 'copyright'
        }
    
    def _get_platform_headers(self, platform: str, credentials: Dict[str, str]) -> Dict[str, str]:
        """Get platform-specific headers"""
        base_headers = {
            'User-Agent': 'IA-Influencer-Protection/1.0',
            'Content-Type': 'application/json'
        }
        
        if platform == 'youtube' and 'api_key' in credentials:
            base_headers['Authorization'] = f"Bearer {credentials['api_key']}"
        elif platform in ['instagram', 'facebook'] and 'access_token' in credentials:
            base_headers['Authorization'] = f"Bearer {credentials['access_token']}"
        
        return base_headers
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        try:
            parsed_url = urlparse(url)
            if 'youtube.com' in parsed_url.netloc:
                return parsed_url.query.split('v=')[1].split('&')[0] if 'v=' in parsed_url.query else None
            elif 'youtu.be' in parsed_url.netloc:
                return parsed_url.path.lstrip('/')
        except:
            pass
        return None


class EmailNotificationSystem:
    """Handle email notifications for enforcement actions"""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        self.sender_email = smtp_config.get('sender_email', 'mlaiel@live.de')
        self.sender_name = smtp_config.get('sender_name', 'Fahed Mlaiel - IA Influencer Protection')
    
    async def send_dmca_notice(self, violation: ViolationReport, dmca_content: str, recipient_email: str) -> bool:
        """Send DMCA takedown notice via email"""
        try:
            subject = f"DMCA Takedown Notice - Copyright Infringement (Ref: {violation.violation_id})"
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            body = f"""This is a formal DMCA takedown notice regarding copyright infringement.

Violation Details:
- Violation ID: {violation.violation_id}
- Platform: {violation.platform}
- Violation URL: {violation.violation_url}
- Detection Date: {violation.detection_timestamp.strftime('%Y-%m-%d %H:%M UTC')}
- Similarity Score: {violation.similarity_score:.2%}

{dmca_content}

This notice is sent in good faith and under penalty of perjury.

Best regards,
{self.sender_name}
Email: {self.sender_email}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"DMCA notice sent to {recipient_email} for violation {violation.violation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending DMCA notice: {str(e)}")
            return False
    
    async def send_cease_desist(self, violation: ViolationReport, letter_content: str, recipient_email: str) -> bool:
        """Send cease and desist letter via email"""
        try:
            subject = f"Cease and Desist - Copyright Infringement (Ref: {violation.violation_id})"
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            body = f"""URGENT: CEASE AND DESIST REQUIRED

This is a formal cease and desist letter regarding your unauthorized use of copyrighted material.

{letter_content}

Immediate action required. Please respond within 7 days.

{self.sender_name}
{self.sender_email}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"Cease and desist sent to {recipient_email} for violation {violation.violation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending cease and desist: {str(e)}")
            return False


class RightsEnforcementEngine:
    """Main enforcement engine coordinating all enforcement actions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.copyright_holder_info = config.get('copyright_holder', {
            'name': 'Fahed Mlaiel',
            'email': 'mlaiel@live.de',
            'address': 'Germany',
            'title': 'Creator & Copyright Owner'
        })
        
        self.dmca_generator = DMCATakedownGenerator(self.copyright_holder_info)
        self.cease_desist_generator = CeaseDesistGenerator(self.copyright_holder_info)
        self.platform_handler = PlatformAPIHandler()
        self.email_system = EmailNotificationSystem(config.get('smtp_config', {}))
        
        self.enforcement_records: List[EnforcementRecord] = []
        self.active_violations: Dict[str, ViolationReport] = {}
    
    async def enforce_violation(self, violation: ViolationReport, enforcement_actions: List[EnforcementAction]) -> List[EnforcementRecord]:
        """Execute enforcement actions for a violation"""
        try:
            records = []
            
            # Store violation
            self.active_violations[violation.violation_id] = violation
            
            for action in enforcement_actions:
                record = await self._execute_enforcement_action(violation, action)
                records.append(record)
                self.enforcement_records.append(record)
            
            logger.info(f"Executed {len(records)} enforcement actions for violation {violation.violation_id}")
            return records
            
        except Exception as e:
            logger.error(f"Error enforcing violation: {str(e)}")
            raise
    
    async def _execute_enforcement_action(self, violation: ViolationReport, action: EnforcementAction) -> EnforcementRecord:
        """Execute a specific enforcement action"""
        record_id = str(uuid.uuid4())[:8]
        
        record = EnforcementRecord(
            record_id=record_id,
            violation_id=violation.violation_id,
            action_type=action,
            status=EnforcementStatus.IN_PROGRESS,
            initiated_at=datetime.now(timezone.utc),
            completed_at=None,
            details={},
            response_received=None,
            follow_up_required=True,
            escalation_level=1
        )
        
        try:
            if action == EnforcementAction.DMCA_TAKEDOWN:
                await self._execute_dmca_takedown(violation, record)
            elif action == EnforcementAction.CEASE_DESIST:
                await self._execute_cease_desist(violation, record)
            elif action == EnforcementAction.PLATFORM_REPORT:
                await self._execute_platform_report(violation, record)
            elif action == EnforcementAction.LEGAL_NOTICE:
                await self._execute_legal_notice(violation, record)
            else:
                record.status = EnforcementStatus.FAILED
                record.details['error'] = f"Unsupported action type: {action}"
            
            record.completed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            record.status = EnforcementStatus.FAILED
            record.details['error'] = str(e)
            record.completed_at = datetime.now(timezone.utc)
            logger.error(f"Enforcement action failed: {str(e)}")
        
        return record
    
    async def _execute_dmca_takedown(self, violation: ViolationReport, record: EnforcementRecord):
        """Execute DMCA takedown notice"""
        try:
            # Generate DMCA notice
            dmca_content = self.dmca_generator.generate_dmca_notice(violation)
            
            # Determine recipient email
            recipient_email = self._get_platform_copyright_email(violation.platform)
            
            if recipient_email:
                # Send via email
                success = await self.email_system.send_dmca_notice(violation, dmca_content, recipient_email)
                
                record.details.update({
                    'dmca_content': dmca_content,
                    'recipient_email': recipient_email,
                    'sent_successfully': success,
                    'method': 'email'
                })
                
                record.status = EnforcementStatus.COMPLETED if success else EnforcementStatus.FAILED
            else:
                record.status = EnforcementStatus.FAILED
                record.details['error'] = f"No copyright email found for platform: {violation.platform}"
            
        except Exception as e:
            record.status = EnforcementStatus.FAILED
            record.details['error'] = str(e)
            raise
    
    async def _execute_cease_desist(self, violation: ViolationReport, record: EnforcementRecord):
        """Execute cease and desist letter"""
        try:
            # Generate letter
            letter_content = self.cease_desist_generator.generate_cease_desist(violation)
            
            # Try to get violator email
            violator_email = violation.violator_info.get('email')
            
            if violator_email:
                # Send via email
                success = await self.email_system.send_cease_desist(violation, letter_content, violator_email)
                
                record.details.update({
                    'letter_content': letter_content,
                    'recipient_email': violator_email,
                    'sent_successfully': success,
                    'method': 'email'
                })
                
                record.status = EnforcementStatus.COMPLETED if success else EnforcementStatus.FAILED
            else:
                # Save letter for manual delivery
                record.details.update({
                    'letter_content': letter_content,
                    'method': 'manual_delivery_required'
                })
                record.status = EnforcementStatus.PENDING
                record.follow_up_required = True
            
        except Exception as e:
            record.status = EnforcementStatus.FAILED
            record.details['error'] = str(e)
            raise
    
    async def _execute_platform_report(self, violation: ViolationReport, record: EnforcementRecord):
        """Execute platform-specific report"""
        try:
            # Get API credentials for platform
            api_credentials = self.config.get('platform_credentials', {}).get(violation.platform, {})
            
            # Submit report
            result = await self.platform_handler.submit_platform_report(violation, api_credentials)
            
            record.details.update({
                'platform_response': result,
                'api_used': True
            })
            
            record.status = EnforcementStatus.COMPLETED if result['success'] else EnforcementStatus.FAILED
            
        except Exception as e:
            record.status = EnforcementStatus.FAILED
            record.details['error'] = str(e)
            raise
    
    async def _execute_legal_notice(self, violation: ViolationReport, record: EnforcementRecord):
        """Execute legal notice"""
        try:
            # Generate formal legal notice
            legal_notice = self._generate_legal_notice(violation)
            
            record.details.update({
                'legal_notice': legal_notice,
                'method': 'formal_legal_notice',
                'requires_attorney_review': True
            })
            
            record.status = EnforcementStatus.PENDING
            record.escalation_level = 3
            
        except Exception as e:
            record.status = EnforcementStatus.FAILED
            record.details['error'] = str(e)
            raise
    
    def _generate_legal_notice(self, violation: ViolationReport) -> str:
        """Generate formal legal notice"""
        return f"""FORMAL LEGAL NOTICE - COPYRIGHT INFRINGEMENT

Case Reference: {violation.violation_id}
Date: {datetime.now().strftime('%B %d, %Y')}

This constitutes formal notice of copyright infringement requiring immediate attention from your legal department.

VIOLATION DETAILS:
- Content ID: {violation.content_id}
- Violation URL: {violation.violation_url}
- Platform: {violation.platform}
- Detection Date: {violation.detection_timestamp.strftime('%Y-%m-%d')}
- Similarity Score: {violation.similarity_score:.2%}
- Violation Type: {violation.violation_type.value}

COPYRIGHT OWNER:
{self.copyright_holder_info['name']}
Email: {self.copyright_holder_info['email']}

This matter requires immediate legal review and response within 48 hours.

Failure to respond appropriately may result in formal legal proceedings.
"""
    
    def _get_platform_copyright_email(self, platform: str) -> Optional[str]:
        """Get copyright contact email for platform"""
        copyright_emails = {
            'youtube': 'copyright@youtube.com',
            'instagram': 'copyright@instagram.com',
            'facebook': 'copyright@facebook.com',
            'tiktok': 'copyright@tiktok.com',
            'twitter': 'copyright@twitter.com',
            'linkedin': 'copyright@linkedin.com',
            'pinterest': 'copyright@pinterest.com'
        }
        
        return copyright_emails.get(platform.lower())
    
    def get_enforcement_statistics(self) -> Dict[str, Any]:
        """Get enforcement statistics"""
        try:
            total_records = len(self.enforcement_records)
            
            if total_records == 0:
                return {'total_records': 0, 'message': 'No enforcement records found'}
            
            status_counts = {}
            action_counts = {}
            
            for record in self.enforcement_records:
                status_counts[record.status.value] = status_counts.get(record.status.value, 0) + 1
                action_counts[record.action_type.value] = action_counts.get(record.action_type.value, 0) + 1
            
            success_rate = status_counts.get('completed', 0) / total_records * 100
            
            return {
                'total_records': total_records,
                'status_breakdown': status_counts,
                'action_breakdown': action_counts,
                'success_rate': round(success_rate, 2),
                'pending_follow_ups': len([r for r in self.enforcement_records if r.follow_up_required])
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'ViolationType',
    'EnforcementAction', 
    'EnforcementStatus',
    'ViolationReport',
    'EnforcementRecord',
    'DMCATakedownGenerator',
    'CeaseDesistGenerator',
    'PlatformAPIHandler',
    'EmailNotificationSystem',
    'RightsEnforcementEngine'
]
