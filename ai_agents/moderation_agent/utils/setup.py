"""Moderation Agent - Ultra-Advanced AI Content Safety System

Enterprise-grade content moderation agent providing comprehensive safety filtering 
and automated compliance enforcement across multiple formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), "__init__.py")
    with open(init_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"

# Read requirements
def get_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_file):
        with open(requirements_file, "r", encoding="utf-8") as f:
            return [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith("#")
            ]
    return []

# Read README for long description
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return "Ultra-Advanced AI Content Moderation & Safety System"

setup(
    name="ia-influencer-moderation-agent",
    version=get_version(),
    author="Fahed Mlaiel",
    author_email="mlaiel@live.de",
    description="Ultra-Advanced AI Content Moderation & Safety System",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mlaiel/Achiri/tree/main/IA-Influencer-Agent/backend/ai_agents/moderation_agent",
    
    packages=find_packages(),
    include_package_data=True,
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Security",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: GPU :: NVIDIA CUDA",
        "Framework :: AsyncIO",
        "Framework :: FastAPI",
    ],
    
    python_requires=">=3.9",
    install_requires=get_requirements(),
    
    extras_require={
        "gpu": [
            "torch[cuda]",
            "tensorflow[and-cuda]",
            "tensorrt>=8.6.1",
            "cupy-cuda11x>=12.0.0"
        ],
        "enterprise": [
            "kubernetes>=28.1.0",
            "prometheus-client>=0.19.0",
            "grafana-api>=1.0.3",
            "elasticsearch>=8.11.0"
        ],
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
            "sphinx>=7.2.6"
        ]
    },
    
    entry_points={
        "console_scripts": [
            "moderation-agent=moderation_agent.cli:main",
        ],
    },
    
    project_urls={
        "Documentation": "https://github.com/Mlaiel/Achiri/tree/main/IA-Influencer-Agent/docs",
        "Source Code": "https://github.com/Mlaiel/Achiri/tree/main/IA-Influencer-Agent/backend/ai_agents/moderation_agent",
        "Issue Tracker": "https://github.com/Mlaiel/Achiri/issues",
        "Licensing": "mailto:mlaiel@live.de",
    },
    
    keywords=[
        "ai", "machine-learning", "content-moderation", "safety", "nlp",
        "computer-vision", "audio-processing", "video-analysis", "toxicity-detection",
        "nsfw-detection", "deepfake-detection", "copyright-protection", "creator-economy",
        "monetization", "compliance", "enterprise", "real-time", "scalable"
    ],
    
    license="Proprietary - All rights reserved",
    
    # Package metadata
    zip_safe=False,
    package_data={
        "moderation_agent": [
            "*.md",
            "*.txt",
            "*.yaml",
            "*.yml",
            "*.json",
            "config/*.yaml",
            "models/*.pt",
            "models/*.onnx",
        ],
    },
    
    # CLI and API endpoints
    command_options={
        "build_py": {
            "compile": ("setup.py", 1),
        },
    },
)
