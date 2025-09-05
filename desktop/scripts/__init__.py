#!/usr/bin/env python3
"""
Desktop Scripts Module Initialization
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Description: Initializes the desktop automation scripts module for Python imports
Usage: import desktop.scripts as scripts

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
TOUS DROITS RÉSERVÉS - PROTÉGÉ PAR LE DROIT D'AUTEUR
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Desktop Scripts Module
# Provides Python interface for desktop automation scripts

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

# Get the scripts directory path
SCRIPTS_DIR = Path(__file__).parent
DESKTOP_DIR = SCRIPTS_DIR.parent

# Available automation scripts
AVAILABLE_SCRIPTS = {
    "validate_build": "validate-build.sh",
    "audio_processing": "audio_processing_automation.sh", 
    "protection": "protection_automation.sh",
    "monetization": "monetization_automation.sh",
    "collaboration": "collaboration_automation.sh",
    "seo": "seo_automation.sh",
    "distribution": "distribution_automation.sh",
    "deployment": "deployment_automation.sh",
    "analytics": "analytics_automation.sh",
    "security": "security_automation.sh",
    "localization": "localization_automation.sh",
    "orchestrator": "workflow_orchestrator.sh"
}

def get_script_path(script_name: str) -> Optional[Path]:
    """Get the full path to a script"""
    if script_name not in AVAILABLE_SCRIPTS:
        return None
    return SCRIPTS_DIR / AVAILABLE_SCRIPTS[script_name]

def list_available_scripts() -> List[str]:
    """List all available automation scripts"""
    return list(AVAILABLE_SCRIPTS.keys())

def run_script(script_name: str, args: List[str] = None) -> subprocess.CompletedProcess:
    """Run a desktop automation script with optional arguments"""
    script_path = get_script_path(script_name)
    if not script_path or not script_path.exists():
        raise FileNotFoundError(f"Script '{script_name}' not found")
    
    cmd = [str(script_path)]
    if args:
        cmd.extend(args)
    
    return subprocess.run(cmd, capture_output=True, text=True, cwd=DESKTOP_DIR)

# Export public interface
__all__ = [
    "SCRIPTS_DIR",
    "DESKTOP_DIR", 
    "AVAILABLE_SCRIPTS",
    "get_script_path",
    "list_available_scripts",
    "run_script"
]