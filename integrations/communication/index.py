"""
Communication Module - Ainflue Integrations
==========================================
Enterprise-grade communication infrastructure providing multi-channel
messaging, collaboration tools, notification systems, and real-time
communication across platforms and users.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all communication components
from .chat_integration import *
from .collaboration_tools import *
from .email_campaigns import *
from .notification_manager import *
from .push_notification import *
from .sms_campaigns import *
from .video_conferencing import *
from .voice_services import *

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise communication infrastructure for multi-platform collaboration"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'communication_channels': 8,
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}