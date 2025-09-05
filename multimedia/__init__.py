"""Advanced Multimedia Processing Platform
High-performance multimedia content processing, analysis, and distribution system.

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

# Only import working modules for now
from .formats import (
    SupportedFormats,
    AudioFormat,
    VideoFormat,
    ImageFormat,
    ContentFormat
)

# Version info
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Format definitions
    "SupportedFormats",
    "AudioFormat", 
    "VideoFormat",
    "ImageFormat",
    "ContentFormat"
]
