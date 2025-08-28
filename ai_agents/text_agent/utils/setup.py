#!/usr/bin/env python3
"""
Text Agent Setup Script

Setup and configuration script for the Text Agent module.
Downloads required models and verifies installation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import subprocess
import sys
import logging
import importlib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description=""):
    """Run shell command and handle errors"""
    try:
        logger.info(f"Running: {description or command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {description or command}: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    try:
        importlib.import_module(import_name or package_name)
        logger.info(f"✓ {package_name} is installed")
        return True
    except ImportError:
        logger.warning(f"✗ {package_name} is not installed")
        return False

def setup_nltk_data():
    """Download required NLTK data"""
    logger.info("Setting up NLTK data...")
    
    nltk_downloads = [
        'punkt',
        'stopwords', 
        'vader_lexicon',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words',
        'wordnet',
        'omw-1.4'
    ]
    
    try:
        import nltk
        for dataset in nltk_downloads:
            try:
                nltk.data.find(f'tokenizers/{dataset}')
            except LookupError:
                try:
                    nltk.data.find(f'corpora/{dataset}')
                except LookupError:
                    try:
                        nltk.data.find(f'taggers/{dataset}')
                    except LookupError:
                        try:
                            nltk.data.find(f'chunkers/{dataset}')
                        except LookupError:
                            logger.info(f"Downloading NLTK dataset: {dataset}")
                            nltk.download(dataset, quiet=True)
        
        logger.info("✓ NLTK data setup complete")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up NLTK data: {e}")
        return False

def setup_spacy_models():
    """Download required spaCy models"""
    logger.info("Setting up spaCy models...")
    
    models = [
        'en_core_web_sm',
        'fr_core_news_sm',
        'de_core_news_sm', 
        'es_core_news_sm',
        'it_core_news_sm'
    ]
    
    success = True
    for model in models:
        if not run_command(f"python -m spacy download {model}", f"Downloading spaCy model: {model}"):
            logger.warning(f"Failed to download spaCy model: {model}")
            success = False
    
    if success:
        logger.info("✓ spaCy models setup complete")
    
    return success

def verify_installation():
    """Verify that all required packages are installed"""
    logger.info("Verifying installation...")
    
    required_packages = [
        ('torch', 'torch'),
        ('transformers', 'transformers'),
        ('sentence_transformers', 'sentence_transformers'),
        ('sklearn', 'sklearn'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('nltk', 'nltk'),
        ('spacy', 'spacy'),
        ('textblob', 'textblob'),
        ('vaderSentiment', 'vaderSentiment'),
        ('langdetect', 'langdetect'),
        ('googletrans', 'googletrans'),
        ('ftfy', 'ftfy'),
        ('contractions', 'contractions'),
        ('bs4', 'bs4'),
        ('redis', 'redis'),
        ('psycopg2', 'psycopg2'),
        ('sqlalchemy', 'sqlalchemy')
    ]
    
    all_installed = True
    for package_name, import_name in required_packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    return all_installed

def test_basic_functionality():
    """Test basic functionality of the text agent"""
    logger.info("Testing basic functionality...")
    
    try:
        # Test imports
        from . import TextAgent, TextProcessor, AITextGenerator
        logger.info("✓ Basic imports successful")
        
        # Test initialization
        processor = TextProcessor()
        logger.info("✓ TextProcessor initialization successful")
        
        # Test basic processing
        import asyncio
        async def test_processing():
            result = await processor.process_text("This is a test text.")
            return result.processed_text
        
        processed = asyncio.run(test_processing())
        logger.info(f"✓ Basic text processing successful: {processed}")
        
        return True
        
    except Exception as e:
        logger.error(f"Basic functionality test failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("Starting Text Agent setup...")
    
    steps = [
        ("Verifying package installation", verify_installation),
        ("Setting up NLTK data", setup_nltk_data),
        ("Setting up spaCy models", setup_spacy_models),
        ("Testing basic functionality", test_basic_functionality)
    ]
    
    for step_name, step_func in steps:
        logger.info(f"\n=== {step_name} ===")
        if not step_func():
            logger.error(f"Setup failed at step: {step_name}")
            logger.info("Please check the errors above and retry.")
            sys.exit(1)
    
    logger.info("\n=== Text Agent Setup Complete ===")
    logger.info("✓ All components are installed and configured correctly")
    logger.info("The Text Agent module is ready for use!")

if __name__ == "__main__":
    main()
