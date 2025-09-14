"""Setup script for Ainflue Python SDK"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme() -> None:
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Ainflue Platform Python SDK"

# Read requirements
def read_requirements() -> None:
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["httpx>=0.25.0", "pydantic>=2.0.0"]

setup(
    name="ainflue-sdk",
    version="1.0.0",
    author="Fahed Mlaiel",
    author_email="mlaiel@live.de",
    description="Official Python SDK for the Ainflue AI-powered content protection platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mlaiel/Ainflue",
    py_modules=["ainflue_sdk"],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia",
        "Topic :: Security"
    ],
    keywords="ainflue api sdk content protection ai monetization",
    project_urls={
        "Documentation": "https://docs.ainflue.com",
        "Source": "https://github.com/Mlaiel/Ainflue",
        "Tracker": "https://github.com/Mlaiel/Ainflue/issues",
    }
)