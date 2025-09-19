#!/usr/bin/env python3
"""
Dependency Update Manager - Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Role: DevOps Engineer
Purpose: Enterprise dependency management and automated updates
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
import pkg_resources
from packaging import version

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DependencyUpdater:
    """Enterprise dependency update manager with safety checks"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/home/runner/work/Ainfluencer/Ainfluencer")
        self.requirements_files = [
            "requirements.txt",
            "requirements-dev.txt", 
            "requirements-ml.txt",
            "requirements-pipeline.txt",
            "requirements-production.txt",
            "requirements-security.txt"
        ]
        self.package_json = self.project_root / "frontend" / "package.json"
        self.backup_dir = self.project_root / "backups" / "dependencies"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    async def check_outdated_packages(self) -> Dict[str, List[Dict]]:
        """Check for outdated packages in all environments"""
        results = {
            "python": [],
            "nodejs": []
        }
        
        # Check Python packages
        for req_file in self.requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                outdated = await self._check_python_outdated(req_path)
                if outdated:
                    results["python"].extend(outdated)
                    
        # Check Node.js packages
        if self.package_json.exists():
            outdated = await self._check_nodejs_outdated()
            if outdated:
                results["nodejs"] = outdated
                
        return results
    
    async def _check_python_outdated(self, req_file: Path) -> List[Dict]:
        """Check outdated Python packages in specific requirements file"""
        try:
            # Parse requirements file
            with open(req_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            outdated_packages = []
            
            for req in requirements:
                if '==' in req:
                    package_name = req.split('==')[0].strip()
                    current_version = req.split('==')[1].strip()
                    
                    # Get latest version from PyPI
                    try:
                        result = subprocess.run(
                            ['pip', 'index', 'versions', package_name],
                            capture_output=True, text=True, timeout=30
                        )
                        
                        if result.returncode == 0:
                            # Parse pip index output for latest version
                            lines = result.stdout.strip().split('\n')
                            for line in lines:
                                if 'Available versions:' in line:
                                    versions_line = lines[lines.index(line) + 1]
                                    latest_version = versions_line.split(',')[0].strip()
                                    
                                    if version.parse(latest_version) > version.parse(current_version):
                                        outdated_packages.append({
                                            'name': package_name,
                                            'current': current_version,
                                            'latest': latest_version,
                                            'file': str(req_file)
                                        })
                                    break
                                    
                    except (subprocess.TimeoutExpired, Exception) as e:
                        logger.warning(f"Failed to check {package_name}: {e}")
                        
            return outdated_packages
            
        except Exception as e:
            logger.error(f"Error checking {req_file}: {e}")
            return []
    
    async def _check_nodejs_outdated(self) -> List[Dict]:
        """Check outdated Node.js packages"""
        try:
            frontend_dir = self.project_root / "frontend"
            
            result = subprocess.run(
                ['npm', 'outdated', '--json'],
                cwd=frontend_dir,
                capture_output=True, text=True, timeout=60
            )
            
            if result.stdout:
                outdated_data = json.loads(result.stdout)
                return [
                    {
                        'name': name,
                        'current': info['current'],
                        'latest': info['latest'],
                        'wanted': info['wanted']
                    }
                    for name, info in outdated_data.items()
                ]
                
        except Exception as e:
            logger.error(f"Error checking Node.js packages: {e}")
            
        return []
    
    async def backup_dependencies(self) -> bool:
        """Backup current dependency files"""
        try:
            timestamp = int(time.time())
            backup_subdir = self.backup_dir / f"backup_{timestamp}"
            backup_subdir.mkdir(exist_ok=True)
            
            # Backup Python requirements
            for req_file in self.requirements_files:
                req_path = self.project_root / req_file
                if req_path.exists():
                    backup_path = backup_subdir / req_file
                    backup_path.write_text(req_path.read_text())
                    
            # Backup package.json and package-lock.json
            if self.package_json.exists():
                (backup_subdir / "package.json").write_text(self.package_json.read_text())
                
                package_lock = self.project_root / "frontend" / "package-lock.json"
                if package_lock.exists():
                    (backup_subdir / "package-lock.json").write_text(package_lock.read_text())
                    
            logger.info(f"Dependencies backed up to {backup_subdir}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    async def update_python_package(self, package_name: str, target_version: str = None) -> bool:
        """Update specific Python package"""
        try:
            cmd = ['pip', 'install', '--upgrade']
            if target_version:
                cmd.append(f"{package_name}=={target_version}")
            else:
                cmd.append(package_name)
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Successfully updated {package_name}")
                return True
            else:
                logger.error(f"Failed to update {package_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating {package_name}: {e}")
            return False
    
    async def update_nodejs_packages(self, specific_packages: List[str] = None) -> bool:
        """Update Node.js packages"""
        try:
            frontend_dir = self.project_root / "frontend"
            
            if specific_packages:
                for package in specific_packages:
                    result = subprocess.run(
                        ['npm', 'update', package],
                        cwd=frontend_dir,
                        capture_output=True, text=True, timeout=300
                    )
                    
                    if result.returncode != 0:
                        logger.error(f"Failed to update {package}: {result.stderr}")
                        return False
            else:
                result = subprocess.run(
                    ['npm', 'update'],
                    cwd=frontend_dir,
                    capture_output=True, text=True, timeout=600
                )
                
                if result.returncode != 0:
                    logger.error(f"Failed to update Node.js packages: {result.stderr}")
                    return False
                    
            logger.info("Node.js packages updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Node.js packages: {e}")
            return False
    
    async def run_security_audit(self) -> Dict[str, any]:
        """Run security audit on dependencies"""
        results = {
            "python": {"vulnerabilities": 0, "details": []},
            "nodejs": {"vulnerabilities": 0, "details": []}
        }
        
        # Python security audit with safety
        try:
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True, text=True, timeout=120
            )
            
            if result.stdout:
                safety_data = json.loads(result.stdout)
                results["python"]["vulnerabilities"] = len(safety_data)
                results["python"]["details"] = safety_data
                
        except Exception as e:
            logger.warning(f"Python security audit failed: {e}")
        
        # Node.js security audit
        try:
            frontend_dir = self.project_root / "frontend"
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                cwd=frontend_dir,
                capture_output=True, text=True, timeout=120
            )
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                results["nodejs"]["vulnerabilities"] = audit_data.get("metadata", {}).get("vulnerabilities", {}).get("total", 0)
                results["nodejs"]["details"] = audit_data
                
        except Exception as e:
            logger.warning(f"Node.js security audit failed: {e}")
            
        return results
    
    async def generate_update_report(self) -> Dict:
        """Generate comprehensive dependency update report"""
        report = {
            "timestamp": time.time(),
            "outdated_packages": await self.check_outdated_packages(),
            "security_audit": await self.run_security_audit(),
            "recommendations": []
        }
        
        # Generate recommendations
        python_outdated = report["outdated_packages"]["python"]
        nodejs_outdated = report["outdated_packages"]["nodejs"]
        
        if python_outdated:
            report["recommendations"].append({
                "type": "python_updates",
                "priority": "medium",
                "action": f"Update {len(python_outdated)} Python packages",
                "packages": [pkg["name"] for pkg in python_outdated]
            })
            
        if nodejs_outdated:
            report["recommendations"].append({
                "type": "nodejs_updates", 
                "priority": "medium",
                "action": f"Update {len(nodejs_outdated)} Node.js packages",
                "packages": [pkg["name"] for pkg in nodejs_outdated]
            })
            
        # Security recommendations
        python_vulns = report["security_audit"]["python"]["vulnerabilities"]
        nodejs_vulns = report["security_audit"]["nodejs"]["vulnerabilities"]
        
        if python_vulns > 0:
            report["recommendations"].append({
                "type": "security_fix",
                "priority": "high",
                "action": f"Fix {python_vulns} Python security vulnerabilities"
            })
            
        if nodejs_vulns > 0:
            report["recommendations"].append({
                "type": "security_fix",
                "priority": "high", 
                "action": f"Fix {nodejs_vulns} Node.js security vulnerabilities"
            })
            
        return report

async def main():
    """Main dependency updater execution"""
    updater = DependencyUpdater()
    
    print("🔄 Dependency Update Manager - Ainflue Platform")
    print("=" * 50)
    
    # Generate report
    print("📊 Generating dependency report...")
    report = await updater.generate_update_report()
    
    print(f"\n📋 Dependency Status:")
    print(f"   Python outdated: {len(report['outdated_packages']['python'])}")
    print(f"   Node.js outdated: {len(report['outdated_packages']['nodejs'])}")
    print(f"   Python vulnerabilities: {report['security_audit']['python']['vulnerabilities']}")
    print(f"   Node.js vulnerabilities: {report['security_audit']['nodejs']['vulnerabilities']}")
    
    # Show recommendations
    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            priority_icon = "🔴" if rec["priority"] == "high" else "🟡"
            print(f"   {priority_icon} {rec['action']}")
    
    # Save report
    report_file = updater.project_root / "reports" / f"dependency_report_{int(time.time())}.json"
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2))
    
    print(f"\n💾 Report saved to: {report_file}")
    print("✅ Dependency check completed!")

if __name__ == "__main__":
    asyncio.run(main())