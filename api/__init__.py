"""
IA Influencer Agent – Backend App Root
-------------------------------------
Complete enterprise-grade backend application for IA-Influencer platform with:

Core Business Logic:
User (Creator: musician/blogger/photographer/influencer/comedian) → 
Upload multi-format content → IA protection & rights → SEO optimization → 
Matching & collaboration → Distribution multi-platforms → Monetization tracking

Architecture Modules:
- API: REST/GraphQL/WebSocket endpoints with JWT/OAuth2
- AI: Machine learning, content generation, analytics processing
- Business: Core business logic services and workflows
- Core: Configuration, database, logging, exceptions
- Protection: Advanced content fingerprinting and rights management
- Fingerprinting: Multi-format content identification (audio, video, image, text)
- Monetization: Revenue tracking, payment processing, licensing automation
- Crawlers: Web surveillance and content monitoring
- Workflow: Process orchestration and automation
- Security: Enterprise-grade security and compliance
- Observability: Monitoring, metrics, and logging
- Database: Data models and repositories
- Services: Business services and integrations
- Utils: Common utilities and helpers

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Machine Learning Engineer: Advanced AI processing and content analysis
- Security Specialist: Enterprise security and content protection
- Financial Technology Expert: Monetization and payment systems
- Web Crawling Engineer: Content monitoring and surveillance
- DevOps Engineer: Infrastructure and deployment automation
- Database Architect: Data modeling and performance optimization
- Legal Technology Expert: Rights management and compliance automation

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

# Import all core application modules
# Temporarily commented out to allow basic app startup
# from . import (
#     ai,
#     api, 
#     business,
#     core,
#     models,
#     services,
#     utils,
#     schemas,
#     security,
#     database,
#     config,
#     protection,
#     fingerprinting,
#     monetization,
#     crawlers,
#     workflow,
#     observability,
#     notifications,
#     multimedia,
#     blockchain
# )

# Export all modules for external access
__all__ = [
    "ai",
    "api",
    "business", 
    "core",
    "models",
    "services",
    "utils",
    "schemas",
    "security",
    "database",
    "config",
    "protection",
    "fingerprinting", 
    "monetization",
    "crawlers",
    "workflow",
    "observability",
    "notifications",
    "multimedia",
    "blockchain"
]
