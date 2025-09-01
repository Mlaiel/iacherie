#!/usr/bin/env python3
"""
Development Environment Health Check
Validates the development environment setup and reports any issues.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import asyncio
import aiohttp

console = Console()

class HealthChecker:
    """Comprehensive health checker for development environment."""
    
    def __init__(self):
        self.results = []
        self.project_root = Path(__file__).parent.parent
        
    def check_result(self, name: str, status: bool, message: str = "", details: str = ""):
        """Record a check result."""
        self.results.append({
            "name": name,
            "status": status,
            "message": message,
            "details": details
        })
        
        if status:
            console.print(f"✅ {name}: {message}", style="green")
        else:
            console.print(f"❌ {name}: {message}", style="red")
            if details:
                console.print(f"   Details: {details}", style="yellow")
    
    def check_python_version(self):
        """Check Python version compatibility."""
        version = sys.version_info
        required_major, required_minor = 3, 11
        
        if version.major >= required_major and version.minor >= required_minor:
            self.check_result(
                "Python Version",
                True,
                f"Python {version.major}.{version.minor}.{version.micro} (Compatible)"
            )
        else:
            self.check_result(
                "Python Version",
                False,
                f"Python {version.major}.{version.minor}.{version.micro} (Requires {required_major}.{required_minor}+)",
                f"Please upgrade to Python {required_major}.{required_minor} or later"
            )
    
    def check_required_files(self):
        """Check for required configuration files."""
        required_files = [
            "requirements.txt",
            "requirements-dev.txt",
            ".pre-commit-config.yaml",
            "docker-compose.dev.yml",
            "pytest.ini",
            "setup.cfg",
            ".vscode/settings.json",
            ".vscode/launch.json"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.check_result(
                    f"File: {file_path}",
                    True,
                    "Exists"
                )
            else:
                self.check_result(
                    f"File: {file_path}",
                    False,
                    "Missing",
                    f"Create this file: {full_path}"
                )
    
    def check_python_packages(self):
        """Check for required Python packages."""
        required_packages = [
            "fastapi",
            "uvicorn",
            "pytest",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
            "rich",
            "aiohttp"
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package)
                self.check_result(
                    f"Package: {package}",
                    True,
                    "Installed"
                )
            except ImportError:
                self.check_result(
                    f"Package: {package}",
                    False,
                    "Not installed",
                    f"Install with: pip install {package}"
                )
    
    def check_docker(self):
        """Check Docker installation and status."""
        try:
            # Check docker command
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.check_result(
                    "Docker",
                    True,
                    f"Installed ({version})"
                )
                
                # Check docker-compose
                result = subprocess.run(
                    ["docker-compose", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    compose_version = result.stdout.strip()
                    self.check_result(
                        "Docker Compose",
                        True,
                        f"Installed ({compose_version})"
                    )
                else:
                    self.check_result(
                        "Docker Compose",
                        False,
                        "Not installed",
                        "Install Docker Compose"
                    )
            else:
                self.check_result(
                    "Docker",
                    False,
                    "Not installed",
                    "Install Docker Desktop or Docker Engine"
                )
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.check_result(
                "Docker",
                False,
                "Not available",
                "Install Docker and ensure it's in PATH"
            )
    
    def check_git(self):
        """Check Git installation and repository status."""
        try:
            # Check git command
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.check_result(
                    "Git",
                    True,
                    f"Installed ({version})"
                )
                
                # Check if we're in a git repository
                result = subprocess.run(
                    ["git", "rev-parse", "--git-dir"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    self.check_result(
                        "Git Repository",
                        True,
                        "Valid repository"
                    )
                else:
                    self.check_result(
                        "Git Repository",
                        False,
                        "Not a git repository",
                        "Initialize with: git init"
                    )
            else:
                self.check_result(
                    "Git",
                    False,
                    "Not installed",
                    "Install Git"
                )
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.check_result(
                "Git",
                False,
                "Not available",
                "Install Git and ensure it's in PATH"
            )
    
    def check_pre_commit(self):
        """Check pre-commit hooks setup."""
        try:
            result = subprocess.run(
                ["pre-commit", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.check_result(
                    "Pre-commit",
                    True,
                    "Installed"
                )
                
                # Check if hooks are installed
                hooks_dir = self.project_root / ".git" / "hooks" / "pre-commit"
                if hooks_dir.exists():
                    self.check_result(
                        "Pre-commit Hooks",
                        True,
                        "Installed"
                    )
                else:
                    self.check_result(
                        "Pre-commit Hooks",
                        False,
                        "Not installed",
                        "Run: pre-commit install"
                    )
            else:
                self.check_result(
                    "Pre-commit",
                    False,
                    "Not installed",
                    "Install with: pip install pre-commit"
                )
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.check_result(
                "Pre-commit",
                False,
                "Not available",
                "Install pre-commit package"
            )
    
    async def check_docker_services(self):
        """Check if Docker development services are running."""
        services = [
            ("ainflue-dev", "http://localhost:8000/health"),
            ("swagger-ui", "http://localhost:8080"),
            ("postgres-dev", "localhost:5433"),
            ("redis-dev", "localhost:6380"),
            ("mongodb-dev", "localhost:27018")
        ]
        
        for service_name, endpoint in services:
            if endpoint.startswith("http"):
                # HTTP service check
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status in [200, 404]:  # 404 is OK for some services
                                self.check_result(
                                    f"Service: {service_name}",
                                    True,
                                    f"Running ({endpoint})"
                                )
                            else:
                                self.check_result(
                                    f"Service: {service_name}",
                                    False,
                                    f"HTTP {response.status}",
                                    f"Check service at {endpoint}"
                                )
                except Exception as e:
                    self.check_result(
                        f"Service: {service_name}",
                        False,
                        "Not accessible",
                        f"Start with: docker-compose -f docker-compose.dev.yml up -d"
                    )
            else:
                # Port check for databases
                import socket
                host, port = endpoint.split(":")
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(5)
                        result = sock.connect_ex((host, int(port)))
                        if result == 0:
                            self.check_result(
                                f"Service: {service_name}",
                                True,
                                f"Running ({endpoint})"
                            )
                        else:
                            self.check_result(
                                f"Service: {service_name}",
                                False,
                                "Not accessible",
                                f"Start with: docker-compose -f docker-compose.dev.yml up -d"
                            )
                except Exception as e:
                    self.check_result(
                        f"Service: {service_name}",
                        False,
                        "Connection failed",
                        str(e)
                    )
    
    def check_environment_variables(self):
        """Check important environment variables."""
        important_vars = [
            "PYTHONPATH",
            "ENVIRONMENT"
        ]
        
        for var in important_vars:
            value = os.getenv(var)
            if value:
                self.check_result(
                    f"Env Var: {var}",
                    True,
                    f"Set to: {value}"
                )
            else:
                self.check_result(
                    f"Env Var: {var}",
                    False,
                    "Not set",
                    f"Consider setting {var} in your environment"
                )
    
    def check_application_imports(self):
        """Check if main application modules can be imported."""
        try:
            # Add project root to path for imports
            sys.path.insert(0, str(self.project_root))
            
            modules_to_check = [
                "main",
                "config.app_config",
                "core.logging"
            ]
            
            for module_name in modules_to_check:
                try:
                    importlib.import_module(module_name)
                    self.check_result(
                        f"Import: {module_name}",
                        True,
                        "Successful"
                    )
                except ImportError as e:
                    self.check_result(
                        f"Import: {module_name}",
                        False,
                        "Failed",
                        str(e)
                    )
        except Exception as e:
            self.check_result(
                "Application Imports",
                False,
                "Check failed",
                str(e)
            )
    
    def check_code_quality_tools(self):
        """Check code quality tools."""
        tools = [
            ("black", ["black", "--version"]),
            ("flake8", ["flake8", "--version"]),
            ("mypy", ["mypy", "--version"]),
            ("pytest", ["pytest", "--version"])
        ]
        
        for tool_name, command in tools:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.check_result(
                        f"Tool: {tool_name}",
                        True,
                        f"Available ({version})"
                    )
                else:
                    self.check_result(
                        f"Tool: {tool_name}",
                        False,
                        "Not working",
                        result.stderr.strip()
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.check_result(
                    f"Tool: {tool_name}",
                    False,
                    "Not available",
                    f"Install with: pip install {tool_name}"
                )
    
    def generate_summary_table(self):
        """Generate a summary table of all checks."""
        table = Table(title="Development Environment Health Check Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")
        
        categories = {}
        for result in self.results:
            category = result["name"].split(":")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "details": []}
            
            if result["status"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
                categories[category]["details"].append(result["message"])
        
        for category, stats in categories.items():
            total = stats["passed"] + stats["failed"]
            status_text = f"{stats['passed']}/{total}"
            
            if stats["failed"] == 0:
                status = f"[green]✅ {status_text}[/green]"
            else:
                status = f"[red]❌ {status_text}[/red]"
            
            details = ", ".join(stats["details"][:3])  # Show first 3 issues
            if len(stats["details"]) > 3:
                details += f" (+{len(stats['details']) - 3} more)"
            
            table.add_row(category, status, details)
        
        return table
    
    async def run_all_checks(self):
        """Run all health checks."""
        console.print(Panel.fit(
            "🏥 Development Environment Health Check",
            title="Health Check",
            border_style="blue"
        ))
        
        checks = [
            ("Python Environment", self.check_python_version),
            ("Required Files", self.check_required_files), 
            ("Python Packages", self.check_python_packages),
            ("Docker", self.check_docker),
            ("Git", self.check_git),
            ("Pre-commit", self.check_pre_commit),
            ("Environment Variables", self.check_environment_variables),
            ("Application Imports", self.check_application_imports),
            ("Code Quality Tools", self.check_code_quality_tools),
            ("Docker Services", self.check_docker_services)
        ]
        
        for check_name, check_func in track(checks, description="Running checks..."):
            console.print(f"\n🔍 Checking {check_name}...")
            
            if asyncio.iscoroutinefunction(check_func):
                await check_func()
            else:
                check_func()
        
        # Generate summary
        console.print("\n")
        summary_table = self.generate_summary_table()
        console.print(summary_table)
        
        # Final status
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r["status"])
        failed_checks = total_checks - passed_checks
        
        console.print(f"\n📊 Summary: {passed_checks}/{total_checks} checks passed")
        
        if failed_checks == 0:
            console.print("🎉 All checks passed! Your development environment is ready.", style="bold green")
            return True
        else:
            console.print(f"⚠️ {failed_checks} checks failed. Please review the issues above.", style="bold yellow")
            
            # Provide quick fix suggestions
            console.print("\n🔧 Quick fixes:")
            console.print("1. Install missing packages: pip install -r requirements-dev.txt")
            console.print("2. Setup pre-commit: pre-commit install")
            console.print("3. Start Docker services: docker-compose -f docker-compose.dev.yml up -d")
            console.print("4. Set PYTHONPATH: export PYTHONPATH=\"$PYTHONPATH:$(pwd)\"")
            
            return False

async def main():
    """Main function."""
    checker = HealthChecker()
    success = await checker.run_all_checks()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())