"""
  Init   module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop Scripts Module Initialization
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Description: Python initialization module for desktop scripts automation
Usage: Import this module to initialize desktop scripts environment
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."

import os
import sys
import logging
from pathlib import Path

# Configure logging for desktop scripts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/desktop_scripts.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Desktop scripts directory
SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent

# Environment configuration
DESKTOP_CONFIG = {
    'SCRIPTS_DIR': str(SCRIPTS_DIR),
    'PROJECT_ROOT': str(PROJECT_ROOT),
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'DESKTOP_ENV': os.getenv('DESKTOP_ENV', 'development'),
}

def initialize_desktop_environment() -> None:
    """Initialize desktop scripts environment"""
    logger.info("🚀 Initializing Ainflue Desktop Scripts Environment")
    logger.info(f"📁 Scripts Directory: {DESKTOP_CONFIG['SCRIPTS_DIR']}")
    logger.info(f"🏠 Project Root: {DESKTOP_CONFIG['PROJECT_ROOT']}")
    logger.info(f"🌍 Environment: {DESKTOP_CONFIG['DESKTOP_ENV']}")
    
    # Ensure required directories exist
    os.makedirs('/tmp/desktop_scripts', exist_ok=True)
    os.makedirs('/tmp/desktop_logs', exist_ok=True)
    
    return DESKTOP_CONFIG

def get_script_path(script_name) -> None:
    """Get full path to a desktop script"""
    return SCRIPTS_DIR / script_name

def validate_script_permissions() -> None:
    """Validate that all scripts have proper permissions"""
    scripts = SCRIPTS_DIR.glob('*.sh')
    for script in scripts:
        if not os.access(script, os.X_OK):
            logger.warning(f"⚠️ Script {script.name} is not executable")
            os.chmod(script, 0o755)
            logger.info(f"✅ Fixed permissions for {script.name}")

if __name__ == "__main__":
    config = initialize_desktop_environment()
    validate_script_permissions()
    logger.info("✅ Desktop scripts environment initialized successfully")