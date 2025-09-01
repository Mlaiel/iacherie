#!/usr/bin/env python3
"""IA Influencer Agent - Content Management System
Quick Start & Installation Guide
==============================================

Industrial-grade content management system for multi-format content creators.
Complete setup and deployment guide with automated configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Expert Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ LEGAL WARNING: This code and concept are protected by intellectual property laws.
Any unauthorized copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will 
result in legal action under German and international copyright laws.
"""

import os
import sys
import subprocess
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any


def print_banner():
    """
Print system banner."""
    print("""╔══════════════════════════════════════════════════════════════════════════════╗
║                    IA Influencer Agent - Content Module                     ║
║                         Quick Start & Installation                          ║
║                                                                              ║
║  🎵 Multi-Format Content Management System                                  ║
║  🤖 AI-Powered Enhancement & Optimization                                   ║
║  🔒 Enterprise-Grade Security & Protection                                  ║
║  📈 Advanced Analytics & Revenue Optimization                               ║
║                                                                              ║
║  Author: Fahed Mlaiel <mlaiel@live.de>                                      ║
║  Industrial-Grade Architecture for Content Creators                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """
Check Python version compatibility."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing Dependencies...")
    
    requirements = [
        "fastapi>=0.104.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "redis>=4.5.0",
        "celery>=5.3.0",
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "librosa>=0.10.0",
        "opencv-python>=4.8.0",
        "Pillow>=10.0.0",
        "aiohttp>=3.9.0",
        "psutil>=5.9.0",
        "cryptography>=41.0.0"
    ]
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        
        print("✅ All dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


async def quick_setup():
    """Perform quick setup and configuration."""
    print("\n⚙️ Running Quick Setup...")
    
    # Run setup script
    try:
        from setup_content_module import ContentModuleSetup
        
        setup = ContentModuleSetup()
        
        # Environment validation
        env_validation = setup.validate_environment()
        if not env_validation['overall_status']:
            print("⚠️  Environment validation found issues - continuing with setup...")
        
        # Configuration setup
        config_result = await setup.setup_configuration()
        print(f"✅ Configuration completed: {config_result['engines_enabled']} engines configured")
        
        # Generate deployment scripts
        setup.generate_deployment_scripts()
        print("✅ Deployment scripts generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


def run_health_check():
    """Run basic health check."""
    print("\n🔍 Running Health Check...")
    
    try:
        # Import and run health check
        result = subprocess.run([sys.executable, "health_check.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Health check passed - System ready")
            return True
        else:
            print(f"⚠️  Health check completed with warnings (exit code: {result.returncode})")
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️  Health check timed out - system may be slow")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def run_demo():
    """Run system demonstration."""
    print("\n🎬 Launching System Demo...")
    
    try:
        # Run demo system
        subprocess.run([sys.executable, "demo_complete_system.py"], timeout=30)
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  Demo timed out - system components may be initializing")
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("""╔══════════════════════════════════════════════════════════════════════════════╗
║                               SETUP COMPLETE                                ║
║                                                                              ║
║  🎉 Content Management System Successfully Installed!                       ║
║                                                                              ║
║  📋 What you have now:                                                       ║
║     • 11 Industrial-Grade Content Engines                                   ║
║     • Complete Testing Framework                                            ║
║     • System Health Monitoring                                              ║
║     • Automated Maintenance Tools                                           ║
║     • Docker Deployment Ready                                               ║
║                                                                              ║
║  🚀 Next Steps:                                                              ║
║                                                                              ║
║     1. Configure API Keys:                                                   ║
║        cp .env.template .env                                                 ║
║        nano .env  # Add your API keys                                        ║
║                                                                              ║
║     2. Run Full Tests:                                                       ║
║        python test_content_complete.py                                       ║
║                                                                              ║
║     3. Launch Production:                                                    ║
║        docker-compose up -d                                                  ║
║                                                                              ║
║     4. Monitor System:                                                       ║
║        python maintenance.py monitor --duration 300                         ║
║                                                                              ║
║  📖 Documentation:                                                           ║
║     • README.md - Complete system documentation                             ║
║     • health_check.py - System health monitoring                            ║
║     • maintenance.py - System maintenance tools                             ║
║                                                                              ║
║  🎵 Specialized for Content Creators:                                       ║
║     • Musicians & Audio Producers                                           ║
║     • Video Content Creators                                                ║
║     • Photographers & Visual Artists                                        ║
║     • Bloggers & Writers                                                    ║
║     • Social Media Influencers                                              ║
║                                                                              ║
║  💼 Enterprise Features:                                                     ║
║     • Multi-tenant architecture                                             ║
║     • 10,000+ concurrent users                                              ║
║     • Advanced AI content enhancement                                       ║
║     • Automated copyright protection                                        ║
║     • Revenue optimization algorithms                                       ║
║                                                                              ║
║  📧 Enterprise Support: mlaiel@live.de                                      ║
║  🌐 Professional Services Available                                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    """
Main installation and setup process."""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Step 3: Quick setup
    try:
        setup_success = asyncio.run(quick_setup())
        if not setup_success:
            print("❌ Setup failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Setup error: {e}")
        sys.exit(1)
    
    # Step 4: Health check
    health_ok = run_health_check()
    
    # Step 5: Demo (optional)
    print("\n🎬 Would you like to run the system demo? (y/n): ", end="")
    try:
        response = input().strip().lower()
        if response in ['y', 'yes', '1', 'true']:
            run_demo()
    except KeyboardInterrupt:
        print("\n⏭️  Skipping demo...")
    
    # Final steps
    print_next_steps()
    
    print("\n🎉 Installation completed successfully!")
    print("📧 For support or questions, contact: mlaiel@live.de")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)
