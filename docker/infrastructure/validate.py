#!/usr/bin/env python3
"""
Ainflue Infrastructure Validation Script

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Validates all Docker Compose infrastructure files for syntax and dependencies.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

# Infrastructure directory
INFRA_DIR = Path(__file__).parent
COMPOSE_FILES = [
    "docker-compose.yml",
    "docker-compose.production.yml", 
    "docker-compose.monitoring.yml",
    "docker-compose.registry.yml",
    "docker-compose.audio.yml",
    "docker-compose.protection.yml",
    "docker-compose.monetization.yml",
    "docker-compose.analytics.yml"
]

def validate_compose_syntax(compose_file: Path) -> Dict:
    """Validate Docker Compose file syntax."""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "config", "--quiet"],
            cwd=INFRA_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "file": compose_file.name,
            "valid": result.returncode == 0,
            "warnings": result.stderr if result.stderr else None,
            "error": None
        }
    except subprocess.TimeoutExpired:
        return {
            "file": compose_file.name,
            "valid": False,
            "warnings": None,
            "error": "Validation timeout"
        }
    except Exception as e:
        return {
            "file": compose_file.name,
            "valid": False,
            "warnings": None,
            "error": str(e)
        }

async def main():
    """Main validation function."""
    print("🔍 Ainflue Infrastructure Validation")
    print("=" * 50)
    
    # Check if Docker Compose is available
    try:
        subprocess.run(["docker", "compose", "version"], check=True, capture_output=True)
        print("✅ Docker Compose available")
    except subprocess.CalledProcessError:
        print("❌ Docker Compose not available")
        sys.exit(1)
    
    print("\n📋 Validating Compose Files:")
    print("-" * 30)
    
    valid_files = 0
    total_files = 0
    
    for filename in COMPOSE_FILES:
        compose_file = INFRA_DIR / filename
        if compose_file.exists():
            total_files += 1
            result = validate_compose_syntax(compose_file)
            
            if result["valid"]:
                print(f"✅ {result['file']}")
                valid_files += 1
                if result["warnings"]:
                    print(f"   ⚠️  Warnings: {result['warnings']}")
            else:
                print(f"❌ {result['file']}")
                if result["error"]:
                    print(f"   Error: {result['error']}")
        else:
            print(f"⚠️  {filename} - File not found")
    
    print(f"\n📊 Validation Summary:")
    print(f"   Total files: {total_files}")
    print(f"   Valid files: {valid_files}")
    print(f"   Success rate: {(valid_files/total_files*100):.1f}%" if total_files > 0 else "N/A")
    
    # Test orchestrator configuration
    print(f"\n🔧 Testing Orchestrator Configuration:")
    print("-" * 40)
    
    try:
        from index import DockerInfrastructureOrchestrator, INFRASTRUCTURE_SERVICES, CREATOR_INFRASTRUCTURE
        
        orchestrator = DockerInfrastructureOrchestrator()
        print(f"✅ Orchestrator loaded successfully")
        print(f"   Infrastructure services: {len(INFRASTRUCTURE_SERVICES)}")
        print(f"   Creator types: {len(CREATOR_INFRASTRUCTURE)}")
        
        # Test configuration consistency
        missing_files = []
        for service_name, service_config in INFRASTRUCTURE_SERVICES.items():
            compose_file = INFRA_DIR / service_config["compose_file"]
            if not compose_file.exists():
                missing_files.append(service_config["compose_file"])
        
        if missing_files:
            print(f"❌ Missing compose files: {missing_files}")
        else:
            print(f"✅ All required compose files exist")
            
    except Exception as e:
        print(f"❌ Orchestrator configuration error: {e}")
    
    # Final status
    print(f"\n🎯 Infrastructure Status:")
    print("-" * 25)
    if valid_files == total_files and valid_files > 0:
        print("✅ Infrastructure validation PASSED")
        print("🚀 Ready for deployment")
        return 0
    else:
        print("❌ Infrastructure validation FAILED")
        print("🔧 Please fix the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))