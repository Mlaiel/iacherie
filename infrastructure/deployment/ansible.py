"""Ansible Configuration Management - Consolidated Module
========================================================
All Ansible functionality consolidated into a single module

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

import asyncio
import logging
import subprocess
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class PlaybookType(Enum):
    """Ansible playbook types"""
    SETUP = "setup"
    DEPLOY = "deploy"
    CONFIGURE = "configure"
    MAINTENANCE = "maintenance"
    SECURITY = "security"

@dataclass
class AnsibleConfig:
    """Ansible configuration"""
    inventory_path: str
    vault_password_file: Optional[str] = None
    private_key_file: Optional[str] = None
    remote_user: str = "ubuntu"
    host_key_checking: bool = False

class AnsibleManager:
    """Unified Ansible management interface"""
    
    def __init__(self, config -> None: AnsibleConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.playbook_runner = PlaybookRunner(config)
        self.configuration_manager = ConfigurationManager(config)
        self.inventory_manager = InventoryManager(config)
    
    async def initialize_ansible(self) -> bool:
        """Initialize Ansible environment"""
        try:
            await self._create_ansible_structure()
            await self._generate_ansible_config()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Ansible: {e}")
            return False
    
    async def _create_ansible_structure(self) -> None:
        """Create Ansible directory structure"""
        directories = [
            'playbooks',
            'roles',
            'group_vars',
            'host_vars',
            'inventories'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def _generate_ansible_config(self) -> None:
        """Generate ansible.cfg"""
        config_content = f'''[defaults]
inventory = {self.config.inventory_path}
remote_user = {self.config.remote_user}
host_key_checking = {str(self.config.host_key_checking).lower()}
retry_files_enabled = False
stdout_callback = yaml

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
'''
        
        if self.config.private_key_file:
            config_content += f"private_key_file = {self.config.private_key_file}\n"
        
        if self.config.vault_password_file:
            config_content += f"vault_password_file = {self.config.vault_password_file}\n"
        
        with open('ansible.cfg', 'w') as f:
            f.write(config_content)

class PlaybookRunner:
    """Ansible playbook execution"""
    
    def __init__(self, config -> None: AnsibleConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def run_playbook(self, 
                          playbook_path: str, 
                          inventory: Optional[str] = None,
                          extra_vars: Optional[Dict[str, Any]] = None,
                          tags: Optional[List[str]] = None,
                          limit: Optional[str] = None) -> bool:
        """Run Ansible playbook"""
        try:
            cmd = ["ansible-playbook", playbook_path]
            
            if inventory:
                cmd.extend(["-i", inventory])
            
            if extra_vars:
                cmd.extend(["--extra-vars", self._format_extra_vars(extra_vars)])
            
            if tags:
                cmd.extend(["--tags", ",".join(tags)])
            
            if limit:
                cmd.extend(["--limit", limit])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"Playbook {playbook_path} executed successfully")
            self.logger.debug(f"Output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Playbook execution failed: {e.stderr}")
            return False
    
    def _format_extra_vars(self, extra_vars: Dict[str, Any]) -> str:
        """Format extra variables for Ansible"""
        return " ".join([f"{k}={v}" for k, v in extra_vars.items()])
    
    async def create_playbook(self, 
                            name: str, 
                            playbook_type: PlaybookType,
                            tasks: List[Dict[str, Any]],
                            hosts: str = "all") -> str:
        """Create Ansible playbook"""
        try:
            playbook_content = {
                'name': f"{name} - {playbook_type.value}",
                'hosts': hosts,
                'become': True,
                'tasks': tasks
            }
            
            playbook_path = f"playbooks/{name}_{playbook_type.value}.yml"
            
            with open(playbook_path, 'w') as f:
                yaml.dump([playbook_content], f, default_flow_style=False)
            
            self.logger.info(f"Created playbook: {playbook_path}")
            return playbook_path
            
        except Exception as e:
            self.logger.error(f"Failed to create playbook: {e}")
            return ""

class ConfigurationManager:
    """Configuration management with Ansible"""
    
    def __init__(self, config -> None: AnsibleConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def configure_docker(self, hosts: str = "all") -> bool:
        """Configure Docker on target hosts"""
        tasks = [
            {
                'name': 'Update apt cache',
                'apt': {
                    'update_cache': True
                }
            },
            {
                'name': 'Install required packages',
                'apt': {
                    'name': ['apt-transport-https', 'ca-certificates', 'curl', 'software-properties-common'],
                    'state': 'present'
                }
            },
            {
                'name': 'Add Docker GPG key',
                'apt_key': {
                    'url': 'https://download.docker.com/linux/ubuntu/gpg',
                    'state': 'present'
                }
            },
            {
                'name': 'Add Docker repository',
                'apt_repository': {
                    'repo': 'deb https://download.docker.com/linux/ubuntu focal stable',
                    'state': 'present'
                }
            },
            {
                'name': 'Install Docker',
                'apt': {
                    'name': 'docker-ce',
                    'state': 'present'
                }
            },
            {
                'name': 'Start and enable Docker service',
                'systemd': {
                    'name': 'docker',
                    'state': 'started',
                    'enabled': True
                }
            }
        ]
        
        playbook_runner = PlaybookRunner(self.config)
        playbook_path = await playbook_runner.create_playbook(
            "docker_setup",
            PlaybookType.SETUP,
            tasks,
            hosts
        )
        
        return await playbook_runner.run_playbook(playbook_path)
    
    async def configure_kubernetes(self, hosts: str = "all") -> bool:
        """Configure Kubernetes on target hosts"""
        tasks = [
            {
                'name': 'Install kubelet, kubeadm, kubectl',
                'apt': {
                    'name': ['kubelet', 'kubeadm', 'kubectl'],
                    'state': 'present'
                }
            },
            {
                'name': 'Hold kubelet, kubeadm, kubectl',
                'dpkg_selections': {
                    'name': '{{ item }}',
                    'selection': 'hold'
                },
                'loop': ['kubelet', 'kubeadm', 'kubectl']
            },
            {
                'name': 'Start and enable kubelet',
                'systemd': {
                    'name': 'kubelet',
                    'state': 'started',
                    'enabled': True
                }
            }
        ]
        
        playbook_runner = PlaybookRunner(self.config)
        playbook_path = await playbook_runner.create_playbook(
            "kubernetes_setup",
            PlaybookType.SETUP,
            tasks,
            hosts
        )
        
        return await playbook_runner.run_playbook(playbook_path)
    
    async def configure_monitoring(self, hosts: str = "monitoring") -> bool:
        """Configure monitoring stack"""
        tasks = [
            {
                'name': 'Create monitoring user',
                'user': {
                    'name': 'monitoring',
                    'system': True,
                    'shell': '/bin/false',
                    'home': '/var/lib/monitoring'
                }
            },
            {
                'name': 'Install Prometheus',
                'get_url': {
                    'url': 'https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz',
                    'dest': '/tmp/prometheus.tar.gz'
                }
            },
            {
                'name': 'Extract Prometheus',
                'unarchive': {
                    'src': '/tmp/prometheus.tar.gz',
                    'dest': '/opt/',
                    'remote_src': True,
                    'owner': 'monitoring',
                    'group': 'monitoring'
                }
            }
        ]
        
        playbook_runner = PlaybookRunner(self.config)
        playbook_path = await playbook_runner.create_playbook(
            "monitoring_setup",
            PlaybookType.SETUP,
            tasks,
            hosts
        )
        
        return await playbook_runner.run_playbook(playbook_path)

class InventoryManager:
    """Ansible inventory management"""
    
    def __init__(self, config -> None: AnsibleConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.inventory = {}
    
    async def create_inventory(self, 
                             groups: Dict[str, List[str]],
                             group_vars: Optional[Dict[str, Dict[str, Any]]] = None) -> bool:
        """Create Ansible inventory"""
        try:
            inventory_content = {}
            
            # Add groups and hosts
            for group_name, hosts in groups.items():
                inventory_content[group_name] = {
                    'hosts': {}
                }
                
                for host in hosts:
                    inventory_content[group_name]['hosts'][host] = {}
            
            # Add group variables
            if group_vars:
                for group_name, vars_dict in group_vars.items():
                    if group_name in inventory_content:
                        inventory_content[group_name]['vars'] = vars_dict
            
            # Write inventory file
            with open(self.config.inventory_path, 'w') as f:
                yaml.dump(inventory_content, f, default_flow_style=False)
            
            self.logger.info(f"Created inventory: {self.config.inventory_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create inventory: {e}")
            return False
    
    async def add_host(self, group: str, hostname: str, host_vars: Optional[Dict[str, Any]] = None) -> bool:
        """Add host to inventory"""
        try:
            if group not in self.inventory:
                self.inventory[group] = {'hosts': {}}
            
            self.inventory[group]['hosts'][hostname] = host_vars or {}
            
            self.logger.info(f"Added host {hostname} to group {group}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add host: {e}")
            return False

# Global instances
ansible_config = AnsibleConfig(
    inventory_path="inventories/production.yml",
    remote_user="ubuntu",
    host_key_checking=False
)

ansible_manager = AnsibleManager(ansible_config)
playbook_runner = PlaybookRunner(ansible_config)
configuration_manager = ConfigurationManager(ansible_config)
inventory_manager = InventoryManager(ansible_config)

# Consolidated exports
__all__ = [
    "AnsibleManager",
    "PlaybookRunner",
    "ConfigurationManager",
    "InventoryManager",
    "AnsibleConfig",
    "PlaybookType",
    "ansible_manager",
    "playbook_runner",
    "configuration_manager",
    "inventory_manager"
]