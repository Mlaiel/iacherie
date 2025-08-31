#!/usr/bin/env python3
"""Setup script for IA Influencer Agent Pipeline Management System

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action under German and international law.
"""from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt"""    requirements_path = this_directory / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Remove inline comments
                    requirement = line.split('#')[0].strip()
                    if requirement:
                        requirements.append(requirement)
            return requirements
    return []

# Package metadata
PACKAGE_NAME = "ia-influencer-pipeline"
VERSION = "1.0.0"
DESCRIPTION = "Enterprise-Grade Pipeline Management System for IA Influencer Agent"
AUTHOR = "Fahed Mlaiel"
AUTHOR_EMAIL = "mlaiel@live.de"
URL = "https://github.com/fahed-mlaiel/ia-influencer-agent"
LICENSE = "Proprietary"

# Classifiers
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Systems Administration",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    "Topic :: System :: Monitoring",
    "Topic :: Security",
]

# Keywords
KEYWORDS = [
    "pipeline", "ci/cd", "deployment", "automation", "monitoring",
    "security", "enterprise", "kubernetes", "docker", "fastapi",
    "async", "microservices", "devops", "infrastructure"
]

# Entry points for CLI commands
ENTRY_POINTS = {
    'console_scripts': [
        'ia-pipeline=index:main_entry',
        'ia-pipeline-orchestrator=orchestrator:main',
        'ia-pipeline-api=api_manager:main',
        'ia-pipeline-scan=security_manager:main',
    ],
}

# Extra requirements for different use cases
EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=7.4.3',
        'pytest-asyncio>=0.21.1',
        'pytest-cov>=4.1.0',
        'pytest-mock>=3.12.0',
        'black>=23.11.0',
        'isort>=5.12.0',
        'flake8>=6.1.0',
        'mypy>=1.7.1',
        'pre-commit>=3.6.0',
    ],
    'monitoring': [
        'prometheus-client>=0.19.0',
        'grafana-api>=1.0.3',
        'psutil>=5.9.6',
    ],
    'cloud': [
        'boto3>=1.34.0',
        'azure-storage-blob>=12.19.0',
        'google-cloud-storage>=2.10.0',
    ],
    'security': [
        'bandit>=1.7.5',
        'safety>=2.3.5',
        'semgrep>=1.45.0',
    ],
    'all': [
        # Combines all extras
    ]
}

# Combine all extras for 'all'
all_extras = []
for extra_deps in EXTRAS_REQUIRE.values():
    if extra_deps:  # Skip empty lists
        all_extras.extend(extra_deps)
EXTRAS_REQUIRE['all'] = list(set(all_extras))

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    
    # Package discovery
    packages=find_packages(),
    py_modules=[
        'index',
        'orchestrator', 
        'pipeline_manager',
        'config_manager',
        'notification_manager',
        'monitoring_manager',
        'security_manager',
        'api_manager'
    ],
    
    # Requirements
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require=EXTRAS_REQUIRE,
    
    # Metadata
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    
    # Entry points
    entry_points=ENTRY_POINTS,
    
    # Package data
    include_package_data=True,
    package_data={
        '': [
            '*.md',
            '*.txt',
            '*.yml',
            '*.yaml',
            '*.json',
            'templates/*.j2',
            'config/*.yml',
        ],
    },
    
    # Additional metadata
    project_urls={
        'Documentation': 'https://github.com/fahed-mlaiel/ia-influencer-agent/docs',
        'Source': 'https://github.com/fahed-mlaiel/ia-influencer-agent',
        'Tracker': 'https://github.com/fahed-mlaiel/ia-influencer-agent/issues',
    },
    
    # ZIP safe
    zip_safe=False,
    
    # Platform compatibility
    platforms=['any'],
    
    # Copyright and license information
    options={
        'build': {
            'build_base': 'build',
        },
        'install': {
            'install_base': '/usr/local',
        },
    },
)

# Post-install message
def print_post_install_message():
    """Print post-installation message"""    message = """╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🎉 IA Influencer Agent Pipeline System Successfully Installed!           ║
║                                                                              ║
║    Author: Fahed Mlaiel <mlaiel@live.de>                                   ║
║    Copyright: © 2025 Fahed Mlaiel. All rights reserved.                    ║
║                                                                              ║
║    ⚠️  WARNING: This software is proprietary and confidential.              ║
║        Unauthorized use is strictly prohibited.                             ║
║                                                                              ║
║    🚀 Quick Start:                                                          ║
║       • ia-pipeline --help          # Show all commands                     ║
║       • ia-pipeline start            # Start pipeline system                ║
║       • ia-pipeline-api             # Start REST API server                 ║
║                                                                              ║
║    📚 Documentation:                                                        ║
║       • README.md    (English)                                             ║
║       • README.de.md (Deutsch)                                             ║
║       • README.fr.md (Français)                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """    print(message)

if __name__ == "__main__":
    print_post_install_message()
