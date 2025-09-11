"""
Enterprise Third-Party Services Integration Module
=================================================

Comprehensive third-party service integrations including:
- Email service providers (SendGrid, Mailgun, etc.)
- SMS service providers (Twilio, Vonage, etc.)
- Analytics platforms (Google Analytics, Mixpanel, etc.)
- Audio processing services
- CRM integrations
- Translation services
- And many more enterprise integrations

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 Fahed Mlaiel. All rights reserved.
"""

from .email_services import EmailEnterpriseService, EmailProvider
from .audio_processing import AudioProcessingHub, AudioProvider
from .sms_services import SMSServicesHub, SMSProvider, MessageType as SMSMessageType
from .analytics_services import AnalyticsServicesHub, AnalyticsProvider, EventType
from .crm_integration import CRMIntegrationService, CRMPlatform
from .compliance_services import ComplianceServicesIntegration, ComplianceStandard
from .cdn_services import CDNServicesIntegration, CDNProvider

__all__ = [
    'EmailEnterpriseService',
    'EmailProvider',
    'AudioProcessingHub', 
    'AudioProvider',
    'SMSServicesHub',
    'SMSProvider',
    'SMSMessageType',
    'AnalyticsServicesHub',
    'AnalyticsProvider',
    'EventType',
    'CRMIntegrationService',
    'CRMPlatform',
    'ComplianceServicesIntegration',
    'ComplianceStandard',
    'CDNServicesIntegration',
    'CDNProvider'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"