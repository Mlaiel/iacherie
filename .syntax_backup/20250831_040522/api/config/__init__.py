"""Configuration Module - IA Influencer Agent Platform
Complete professional configuration system for production-ready application

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team Specialties: Lead Dev AI + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Core configuration management
from .index import *

# Initialize configuration system
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"

# Project team specialties
TEAM_SPECIALTIES = [
    "Lead Developer AI",
    "Backend Senior Engineer", 
    "ML/AI Engineer",
    "Database Administrator",
    "Security Specialist",
    "Microservices Architect",
    "Audio Processing Expert",
    "DevOps Engineer", 
    "IA Prompt Engineer"
]

COPYRIGHT_NOTICE = """INTELLECTUAL PROPERTY PROTECTION NOTICE
=====================================

This codebase contains proprietary intellectual property belonging to Fahed Mlaiel.
All rights are reserved under international copyright law.

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Copying, reproduction, or distribution of this code
- Reverse engineering or decompilation
- Commercial use without explicit written license
- Modification or derivative works without authorization

For licensing inquiries, contact: mlaiel@live.de

Violators will be prosecuted to the full extent of the law.
"""
def print_copyright_notice():
    """Print copyright and team information"""    print(COPYRIGHT_NOTICE)
    print(f"\nProject Lead: {__author__}")
    print(f"Contact: {__email__}")
    print("\nTeam Specialties:")
    for specialty in TEAM_SPECIALTIES:
        print(f"  • {specialty}")
