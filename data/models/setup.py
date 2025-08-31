"""
Setup Configuration for IA Influencer Agent Data Models
======================================================

Professional setup script for the data models module.
Handles dependencies, installation, and package configuration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from setuptools import setup, find_packages
import os
import sys

# Ensure we're using Python 3.9+
if sys.version_info < (3, 9):
    raise RuntimeError("This package requires Python 3.9 or later")

# Read README for long description
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies
CORE_DEPENDENCIES = [
    "sqlalchemy>=2.0.0,<3.0.0",
    "psycopg2-binary>=2.9.0",
    "alembic>=1.13.0",
    "python-dateutil>=2.8.0",
    "typing-extensions>=4.0.0",
]

# Validation dependencies
VALIDATION_DEPENDENCIES = [
    "email-validator>=2.0.0",
    "phonenumbers>=8.13.0",
    "validators>=0.22.0",
    "pydantic>=2.0.0",
]

# Development dependencies
DEV_DEPENDENCIES = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]

# Testing dependencies
TEST_DEPENDENCIES = [
    "factory-boy>=3.3.0",
    "faker>=19.0.0",
    "pytest-mock>=3.11.0",
    "pytest-xdist>=3.3.0",
    "coverage>=7.0.0",
]

# Documentation dependencies
DOCS_DEPENDENCIES = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
    "myst-parser>=2.0.0",
    "sphinx-autodoc-typehints>=1.24.0",
]

# Optional dependencies for enhanced features
EXTRAS_DEPENDENCIES = {
    "redis": ["redis>=4.6.0"],
    "elasticsearch": ["elasticsearch>=8.9.0"],
    "monitoring": ["prometheus-client>=0.17.0"],
    "encryption": ["cryptography>=41.0.0"],
    "async": ["asyncpg>=0.28.0", "aioredis>=2.0.0"],
}

# All optional dependencies
ALL_OPTIONAL = []
for deps in EXTRAS_DEPENDENCIES.values():
    ALL_OPTIONAL.extend(deps)

setup(
    name="ia-influencer-agent-data-models",
    version="1.0.0",
    author="Fahed Mlaiel",
    author_email="mlaiel@live.de",
    description="Professional data models for IA Influencer Agent platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fahed/ia-influencer-agent",
    project_urls={
        "Bug Reports": "https://github.com/fahed/ia-influencer-agent/issues",
        "Source": "https://github.com/fahed/ia-influencer-agent",
        "Documentation": "https://ia-influencer-agent.readthedocs.io/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Video",
        "Topic :: Office/Business :: Financial",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: SQLAlchemy",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.9",
    install_requires=CORE_DEPENDENCIES + VALIDATION_DEPENDENCIES,
    extras_require={
        "dev": DEV_DEPENDENCIES,
        "test": TEST_DEPENDENCIES,
        "docs": DOCS_DEPENDENCIES,
        "redis": EXTRAS_DEPENDENCIES["redis"],
        "elasticsearch": EXTRAS_DEPENDENCIES["elasticsearch"],
        "monitoring": EXTRAS_DEPENDENCIES["monitoring"],
        "encryption": EXTRAS_DEPENDENCIES["encryption"],
        "async": EXTRAS_DEPENDENCIES["async"],
        "all": ALL_OPTIONAL,
        "complete": (
            DEV_DEPENDENCIES + 
            TEST_DEPENDENCIES + 
            DOCS_DEPENDENCIES + 
            ALL_OPTIONAL
        ),
    },
    package_data={
        "": [
            "*.md",
            "*.txt",
            "*.yml",
            "*.yaml",
            "*.json",
            "*.sql",
            "*.ini",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "ia-models-migrate=backend.data.models.migrations:main",
            "ia-models-validate=backend.data.models.validators:main",
            "ia-models-examples=backend.data.models.examples:run_all_examples",
        ],
    },
    keywords=[
        "influencer",
        "content-creator",
        "social-media",
        "monetization",
        "analytics",
        "content-protection",
        "licensing",
        "sqlalchemy",
        "postgresql",
        "data-models",
        "orm",
        "ai",
        "machine-learning",
        "fingerprinting",
        "copyright-protection",
        "revenue-tracking",
        "social-analytics"
    ],
    license="Proprietary",
    platforms=["any"],
    
    # Metadata for package discovery
    license_files=["LICENSE"],
    maintainer="Fahed Mlaiel",
    maintainer_email="mlaiel@live.de",
    
    # Custom metadata
    custom_metadata={
        "team": {
            "lead_developer": "Fahed Mlaiel",
            "data_architect": "Fahed Mlaiel",
            "security_specialist": "Fahed Mlaiel",
            "ai_specialist": "Fahed Mlaiel"
        },
        "features": [
            "Multi-platform content management",
            "Advanced revenue tracking",
            "AI-powered content protection",
            "Comprehensive analytics",
            "Professional licensing management",
            "Multi-language support",
            "Enterprise-grade validation",
            "Automated migrations"
        ],
        "supported_platforms": [
            "YouTube",
            "Instagram", 
            "TikTok",
            "LinkedIn",
            "Twitter/X",
            "Facebook",
            "Twitch",
            "OnlyFans"
        ]
    }
)


def post_install_message():
    """Display post-installation message"""
    print("""

                IA INFLUENCER AGENT DATA MODELS               
                     Successfully Installed!                  

                                                               
   Thank you for choosing IA Influencer Agent Data Models   
                                                               
   Documentation: README.md (EN), README.de.md (DE),       
                    README.fr.md (FR)                         
                                                               
   Quick Start:                                             
     from backend.data.models import ContentModel, UserModel  
                                                               
    CLI Tools:                                              
     ia-models-migrate    - Database migrations               
     ia-models-validate   - Data validation                   
     ia-models-examples   - Usage examples                    
                                                               
   Support: mlaiel@live.de                                  
                                                               
    WARNING: This is proprietary software.                 
      Unauthorized use is strictly prohibited.                
                                                               

    """)


if __name__ == "__main__":
    post_install_message()
