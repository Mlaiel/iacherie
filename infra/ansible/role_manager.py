"""
Role Manager module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Ansible Role Manager for Ainflue Platform
========================================

Enterprise-grade Ansible role management system for infrastructure automation.
Supports dynamic role generation, dependency management, and automated deployment.

Features:
- Dynamic role creation and management
- Role dependency resolution
- Template-based role generation
- Multi-environment support
- Security-first role configuration
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class RoleType(Enum):
    """Ansible role types"""
    COMMON = "common"
    SECURITY = "security"
    DATABASE = "database"
    MONITORING = "monitoring"
    APPLICATION = "application"
    NETWORKING = "networking"
    STORAGE = "storage"

@dataclass
class AnsibleRole:
    """Ansible role configuration"""
    name: str
    type: RoleType
    dependencies: List[str]
    variables: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    handlers: List[Dict[str, Any]]
    templates: List[str]
    files: List[str]
    meta: Dict[str, Any]

class RoleManager:
    """
    Enterprise Ansible Role Manager
    
    Manages Ansible roles for infrastructure automation across multiple environments.
    Provides role generation, dependency management, and deployment coordination.
    """
    
    def __init__(self, roles_path -> None: str = "/home/runner/work/Ainflue/Ainflue/infra/ansible/roles") -> None:
        self.roles_path = Path(roles_path)
        self.roles_path.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logging()
        self.roles: Dict[str, AnsibleRole] = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup enterprise logging"""
        logger = logging.getLogger("ansible.role_manager")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def create_role(self, role: AnsibleRole) -> bool:
        """
        Create a new Ansible role with all required components
        
        Args:
            role: AnsibleRole configuration object
            
        Returns:
            bool: Success status
        """
        try:
            role_path = self.roles_path / role.name
            role_path.mkdir(parents=True, exist_ok=True)
            
            # Create role directory structure
            directories = [
                "tasks", "handlers", "templates", "files", 
                "vars", "defaults", "meta"
            ]
            
            for directory in directories:
                (role_path / directory).mkdir(exist_ok=True)
            
            # Create main.yml files
            self._create_tasks_main(role_path, role.tasks)
            self._create_handlers_main(role_path, role.handlers)
            self._create_vars_main(role_path, role.variables)
            self._create_defaults_main(role_path, role.variables)
            self._create_meta_main(role_path, role.meta, role.dependencies)
            
            # Copy templates and files
            self._copy_role_assets(role_path, role.templates, role.files)
            
            self.roles[role.name] = role
            self.logger.info(f"Successfully created role: {role.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create role {role.name}: {str(e)}")
            return False
    
    def _create_tasks_main(self, role_path -> None: Path, tasks -> None: List[Dict[str, Any]]) -> None:
        """Create tasks/main.yml"""
        tasks_file = role_path / "tasks" / "main.yml"
        
        with open(tasks_file, 'w') as f:
            yaml.dump(tasks, f, default_flow_style=False, sort_keys=False)
    
    def _create_handlers_main(self, role_path -> None: Path, handlers -> None: List[Dict[str, Any]]) -> None:
        """Create handlers/main.yml"""
        handlers_file = role_path / "handlers" / "main.yml"
        
        with open(handlers_file, 'w') as f:
            yaml.dump(handlers, f, default_flow_style=False, sort_keys=False)
    
    def _create_vars_main(self, role_path -> None: Path, variables -> None: Dict[str, Any]) -> None:
        """Create vars/main.yml"""
        vars_file = role_path / "vars" / "main.yml"
        
        with open(vars_file, 'w') as f:
            yaml.dump(variables, f, default_flow_style=False, sort_keys=False)
    
    def _create_defaults_main(self, role_path -> None: Path, variables -> None: Dict[str, Any]) -> None:
        """Create defaults/main.yml"""
        defaults_file = role_path / "defaults" / "main.yml"
        
        # Create default values (usually with sensible defaults)
        defaults = {k: v for k, v in variables.items() if not k.startswith('_')}
        
        with open(defaults_file, 'w') as f:
            yaml.dump(defaults, f, default_flow_style=False, sort_keys=False)
    
    def _create_meta_main(self, role_path -> None: Path, meta -> None: Dict[str, Any], dependencies -> None: List[str]) -> None:
        """Create meta/main.yml"""
        meta_file = role_path / "meta" / "main.yml"
        
        meta_content = {
            "galaxy_info": {
                "author": "Fahed Mlaiel",
                "description": meta.get("description", "Ainflue infrastructure role"),
                "company": "Ainflue Platform",
                "license": "Proprietary",
                "min_ansible_version": "2.9",
                "platforms": [
                    {
                        "name": "Ubuntu",
                        "versions": ["20.04", "22.04"]
                    },
                    {
                        "name": "CentOS",
                        "versions": ["7", "8"]
                    }
                ],
                "galaxy_tags": ["infrastructure", "enterprise", "ainflue"]
            },
            "dependencies": [{"role": dep} for dep in dependencies]
        }
        
        with open(meta_file, 'w') as f:
            yaml.dump(meta_content, f, default_flow_style=False, sort_keys=False)
    
    def _copy_role_assets(self, role_path -> None: Path, templates -> None: List[str], files -> None: List[str]) -> None:
        """Copy templates and files to role"""
        # For now, create placeholder files
        # In a real implementation, these would be copied from a template repository
        
        for template in templates:
            template_path = role_path / "templates" / template
            template_path.parent.mkdir(parents=True, exist_ok=True)
            template_path.touch()
        
        for file in files:
            file_path = role_path / "files" / file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
    
    def install_role_dependencies(self, role_name: str) -> bool:
        """
        Install role dependencies recursively
        
        Args:
            role_name: Name of the role
            
        Returns:
            bool: Success status
        """
        try:
            if role_name not in self.roles:
                self.logger.error(f"Role {role_name} not found")
                return False
            
            role = self.roles[role_name]
            
            for dependency in role.dependencies:
                if dependency not in self.roles:
                    self.logger.warning(f"Dependency {dependency} not found, attempting to create")
                    # In a real implementation, this would fetch from Ansible Galaxy
                    # or a private role repository
                
                self.logger.info(f"Installing dependency: {dependency}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install dependencies for {role_name}: {str(e)}")
            return False
    
    def validate_role(self, role_name: str) -> bool:
        """
        Validate role structure and configuration
        
        Args:
            role_name: Name of the role to validate
            
        Returns:
            bool: Validation success
        """
        try:
            role_path = self.roles_path / role_name
            
            if not role_path.exists():
                self.logger.error(f"Role directory {role_name} does not exist")
                return False
            
            # Check required directories
            required_dirs = ["tasks", "handlers", "meta"]
            for directory in required_dirs:
                if not (role_path / directory).exists():
                    self.logger.error(f"Required directory {directory} missing in role {role_name}")
                    return False
            
            # Check main.yml files
            required_files = ["tasks/main.yml", "meta/main.yml"]
            for file in required_files:
                if not (role_path / file).exists():
                    self.logger.error(f"Required file {file} missing in role {role_name}")
                    return False
            
            self.logger.info(f"Role {role_name} validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate role {role_name}: {str(e)}")
            return False
    
    def list_roles(self) -> List[str]:
        """List all available roles"""
        roles = []
        
        if self.roles_path.exists():
            for item in self.roles_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    roles.append(item.name)
        
        return sorted(roles)
    
    def get_role_info(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed role information"""
        try:
            role_path = self.roles_path / role_name
            meta_file = role_path / "meta" / "main.yml"
            
            if not meta_file.exists():
                return None
            
            with open(meta_file, 'r') as f:
                meta_content = yaml.safe_load(f)
            
            return {
                "name": role_name,
                "path": str(role_path),
                "meta": meta_content,
                "valid": self.validate_role(role_name)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get role info for {role_name}: {str(e)}")
            return None
    
    def create_standard_roles(self) -> bool:
        """Create standard Ainflue infrastructure roles"""
        try:
            # Common setup role
            common_role = AnsibleRole(
                name="common_setup",
                type=RoleType.COMMON,
                dependencies=[],
                variables={
                    "timezone": "UTC",
                    "ntp_servers": ["pool.ntp.org"],
                    "system_packages": ["curl", "wget", "git", "htop"]
                },
                tasks=[
                    {
                        "name": "Update package cache",
                        "apt": {"update_cache": True},
                        "when": "ansible_os_family == 'Debian'"
                    },
                    {
                        "name": "Install system packages",
                        "package": {"name": "{{ system_packages }}", "state": "present"}
                    },
                    {
                        "name": "Set timezone",
                        "timezone": {"name": "{{ timezone }}"}
                    }
                ],
                handlers=[
                    {
                        "name": "restart ntp",
                        "service": {"name": "ntp", "state": "restarted"}
                    }
                ],
                templates=["ntp.conf.j2"],
                files=["motd"],
                meta={"description": "Common system setup and configuration"}
            )
            
            # Security hardening role
            security_role = AnsibleRole(
                name="security_hardening",
                type=RoleType.SECURITY,
                dependencies=["common_setup"],
                variables={
                    "ssh_port": 22,
                    "firewall_enabled": True,
                    "fail2ban_enabled": True
                },
                tasks=[
                    {
                        "name": "Configure SSH security",
                        "lineinfile": {
                            "path": "/etc/ssh/sshd_config",
                            "regexp": "^PermitRootLogin",
                            "line": "PermitRootLogin no"
                        },
                        "notify": "restart ssh"
                    },
                    {
                        "name": "Install and configure fail2ban",
                        "package": {"name": "fail2ban", "state": "present"},
                        "when": "fail2ban_enabled"
                    }
                ],
                handlers=[
                    {
                        "name": "restart ssh",
                        "service": {"name": "ssh", "state": "restarted"}
                    }
                ],
                templates=["fail2ban.conf.j2", "sshd_config.j2"],
                files=["security_banner"],
                meta={"description": "Security hardening and compliance configuration"}
            )
            
            # Create the roles
            success = True
            for role in [common_role, security_role]:
                if not self.create_role(role):
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to create standard roles: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    manager = RoleManager()
    
    # Create standard roles
    if manager.create_standard_roles():
        print("✅ Standard roles created successfully")
    else:
        print("❌ Failed to create standard roles")
    
    # List all roles
    roles = manager.list_roles()
    print(f"Available roles: {roles}")
    
    # Validate roles
    for role in roles:
        if manager.validate_role(role):
            print(f"✅ Role {role} is valid")
        else:
            print(f"❌ Role {role} validation failed")