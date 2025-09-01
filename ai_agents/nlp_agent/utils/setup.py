"""Setup configuration for NLP Agent package
=========================================

Advanced Natural Language Processing System for content analysis and protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    requirements.append(line)
    return requirements

setup(
    name="ia-influencer-nlp-agent",
    version="1.0.0",
    description="Advanced NLP Agent System for Content Processing and Protection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Fahed Mlaiel",
    author_email="mlaiel@live.de",
    url="https://github.com/fahed-mlaiel/ia-influencer-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "gpu": [
            "torch>=1.12.0+cu116",
            "faiss-gpu>=1.7.2",
        ],
        "dev": [
            "pytest>=7.1.0",
            "pytest-asyncio>=0.19.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.971",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.9.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipython>=8.0.0",
        ],
        "full": [
            "torch>=1.12.0+cu116",
            "faiss-gpu>=1.7.2",
            "pytest>=7.1.0",
            "pytest-asyncio>=0.19.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.971",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.9.0",
            "jupyter>=1.0.0",
            "ipython>=8.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "nlp-agent=nlp_agent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nlp_agent": [
            "*.md",
            "*.txt",
            "*.json",
            "data/*",
            "models/*",
        ],
    },
    zip_safe=False,
    keywords=[
        "nlp",
        "natural language processing",
        "text analysis",
        "sentiment analysis",
        "content protection",
        "entity recognition",
        "topic modeling",
        "embeddings",
        "ai",
        "machine learning",
        "transformers",
        "bert",
        "roberta",
        "influencer",
        "content creation",
        "plagiarism detection",
        "text fingerprinting",
        "semantic analysis",
        "intent recognition",
        "language detection",
        "multilingual",
        "async processing",
        "industrial grade"
    ],
    project_urls={
        "Bug Reports": "https://github.com/fahed-mlaiel/ia-influencer-agent/issues",
        "Source": "https://github.com/fahed-mlaiel/ia-influencer-agent",
        "Documentation": "https://ia-influencer-agent.readthedocs.io/",
    },
)

# Post-installation setup
def post_install():
    """
    Post-installation setup for NLP models and data
    """
    print("Setting up NLP Agent...")
    
    try:
        # Download required NLTK data
        import nltk
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("NLTK data downloaded successfully.")
    except ImportError:
        print("NLTK not available. Skipping NLTK data download.")
    
    try:
        # Download spaCy model
        import spacy.cli
        print("Downloading spaCy English model...")
        spacy.cli.download("en_core_web_sm")
        print("spaCy model downloaded successfully.")
    except:
        print("spaCy model download failed. Install manually with: python -m spacy download en_core_web_sm")
    
    print("NLP Agent setup complete!")

if __name__ == "__main__":
    post_install()
