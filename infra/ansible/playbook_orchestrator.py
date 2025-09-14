"""
Playbook Orchestrator module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module - Ansible Playbook Orchestrator
# =============================================================
# 
# Enterprise-grade Ansible playbook orchestration for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Ansible Playbook Orchestrator - Enterprise Configuration Management

Provides comprehensive Ansible playbook orchestration including:
- Playbook execution and management
- Multi-environment deployment
- Configuration drift detection
- Rollback and recovery capabilities
- Integration with CI/CD pipelines
"""

import asyncio
import logging
import subprocess
import yaml
import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaybookStatus(Enum):
    """Playbook execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class ExecutionMode(Enum):
    """Execution mode enumeration"""
    CHECK = "check"
    DIFF = "diff"
    NORMAL = "normal"
    DRY_RUN = "dry_run"

class Environment(Enum):
    """Deployment environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

@dataclass
class PlaybookConfig:
    """Playbook configuration dataclass"""
    name: str
    path: str
    inventory: str = "inventory.yml"
    environment: Environment = Environment.DEVELOPMENT
    variables: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    skip_tags: List[str] = field(default_factory=list)
    limit: Optional[str] = None
    vault_password_file: Optional[str] = None
    become: bool = False
    check_mode: bool = False
    diff_mode: bool = False
    timeout: int = 3600  # 1 hour default

@dataclass
class ExecutionResult:
    """Playbook execution result dataclass"""
    playbook_name: str
    status: PlaybookStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    changed_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    ok_tasks: int = 0
    unreachable_hosts: int = 0
    execution_id: str = ""

@dataclass
class InventoryHost:
    """Inventory host configuration"""
    name: str
    ansible_host: str
    groups: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    ansible_user: Optional[str] = None
    ansible_port: int = 22
    ansible_ssh_private_key_file: Optional[str] = None

class PlaybookOrchestrator:
    """
    Enterprise Ansible Playbook Orchestrator
    
    Manages Ansible playbook execution, configuration management,
    and deployment orchestration across multi-cloud environments.
    """
    
    def __init__(self, ansible_config_path -> None: Optional[str] = None) -> None:
        """Initialize playbook orchestrator"""
        self.ansible_config_path = ansible_config_path or "/home/runner/work/Ainflue/Ainflue/infra/ansible"
        self.playbooks: Dict[str, PlaybookConfig] = {}
        self.execution_history: List[ExecutionResult] = []
        self.active_executions: Dict[str, subprocess.Popen] = {}
        self.inventories: Dict[str, Dict[str, Any]] = {}
        
        # Enterprise configuration
        self.max_concurrent_executions = 5
        self.default_timeout = 3600
        self.retry_attempts = 3
        self.rollback_enabled = True
        
        # Initialize orchestrator
        self._initialize_orchestrator()
    
    def _initialize_orchestrator(self) -> None:
        """Initialize Ansible orchestrator"""
        try:
            # Ensure ansible directories exist
            os.makedirs(self.ansible_config_path, exist_ok=True)
            os.makedirs(f"{self.ansible_config_path}/playbooks", exist_ok=True)
            os.makedirs(f"{self.ansible_config_path}/inventories", exist_ok=True)
            os.makedirs(f"{self.ansible_config_path}/group_vars", exist_ok=True)
            os.makedirs(f"{self.ansible_config_path}/host_vars", exist_ok=True)
            os.makedirs(f"{self.ansible_config_path}/roles", exist_ok=True)
            
            # Load existing playbooks
            self._discover_playbooks()
            
            # Load inventories
            self._load_inventories()
            
            logger.info("Ansible playbook orchestrator initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    def _discover_playbooks(self) -> None:
        """Discover existing playbooks"""
        try:
            playbooks_dir = Path(f"{self.ansible_config_path}/playbooks")
            if playbooks_dir.exists():
                for playbook_file in playbooks_dir.glob("*.yml"):
                    playbook_name = playbook_file.stem
                    config = PlaybookConfig(
                        name=playbook_name,
                        path=str(playbook_file)
                    )
                    self.playbooks[playbook_name] = config
            
            logger.info(f"Discovered {len(self.playbooks)} playbooks")
            
        except Exception as e:
            logger.error(f"Failed to discover playbooks: {e}")
    
    def _load_inventories(self) -> None:
        """Load inventory configurations"""
        try:
            inventories_dir = Path(f"{self.ansible_config_path}/inventories")
            if inventories_dir.exists():
                for inv_file in inventories_dir.glob("*.yml"):
                    with open(inv_file, 'r') as f:
                        inventory_data = yaml.safe_load(f)
                        self.inventories[inv_file.stem] = inventory_data
            
            logger.info(f"Loaded {len(self.inventories)} inventories")
            
        except Exception as e:
            logger.error(f"Failed to load inventories: {e}")
    
    def register_playbook(self, config: PlaybookConfig) -> bool:
        """Register a new playbook"""
        try:
            # Validate playbook file exists
            if not os.path.exists(config.path):
                logger.error(f"Playbook file not found: {config.path}")
                return False
            
            # Validate playbook syntax
            if not self._validate_playbook_syntax(config.path):
                logger.error(f"Invalid playbook syntax: {config.path}")
                return False
            
            self.playbooks[config.name] = config
            logger.info(f"Playbook registered: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register playbook {config.name}: {e}")
            return False
    
    def _validate_playbook_syntax(self, playbook_path: str) -> bool:
        """Validate Ansible playbook syntax"""
        try:
            cmd = [
                "ansible-playbook",
                "--syntax-check",
                playbook_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error(f"Syntax check timeout for playbook: {playbook_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to validate playbook syntax: {e}")
            return False
    
    async def execute_playbook(self, playbook_name: str, mode: ExecutionMode = ExecutionMode.NORMAL) -> ExecutionResult:
        """Execute an Ansible playbook"""
        try:
            if playbook_name not in self.playbooks:
                raise ValueError(f"Playbook not found: {playbook_name}")
            
            config = self.playbooks[playbook_name]
            execution_id = self._generate_execution_id(playbook_name)
            
            # Check concurrent execution limit
            if len(self.active_executions) >= self.max_concurrent_executions:
                logger.warning("Maximum concurrent executions reached")
                return ExecutionResult(
                    playbook_name=playbook_name,
                    status=PlaybookStatus.FAILED,
                    start_time=datetime.now(),
                    execution_id=execution_id,
                    stderr="Maximum concurrent executions reached"
                )
            
            # Build ansible command
            cmd = self._build_ansible_command(config, mode)
            
            # Start execution
            start_time = datetime.now()
            result = ExecutionResult(
                playbook_name=playbook_name,
                status=PlaybookStatus.RUNNING,
                start_time=start_time,
                execution_id=execution_id
            )
            
            logger.info(f"Starting playbook execution: {playbook_name}")
            
            # Execute playbook
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.ansible_config_path
            )
            
            self.active_executions[execution_id] = process
            
            try:
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout
                )
                
                # Update result
                end_time = datetime.now()
                result.end_time = end_time
                result.duration = (end_time - start_time).total_seconds()
                result.exit_code = process.returncode
                result.stdout = stdout.decode() if stdout else ""
                result.stderr = stderr.decode() if stderr else ""
                
                # Parse execution statistics
                self._parse_execution_stats(result)
                
                # Determine final status
                if process.returncode == 0:
                    result.status = PlaybookStatus.SUCCESS
                else:
                    result.status = PlaybookStatus.FAILED
                
                logger.info(f"Playbook execution completed: {playbook_name} ({result.status.value})")
                
            except asyncio.TimeoutError:
                # Kill process on timeout
                process.kill()
                await process.wait()
                
                result.status = PlaybookStatus.FAILED
                result.end_time = datetime.now()
                result.duration = config.timeout
                result.stderr = "Execution timeout"
                
                logger.error(f"Playbook execution timeout: {playbook_name}")
            
            finally:
                # Remove from active executions
                if execution_id in self.active_executions:
                    del self.active_executions[execution_id]
            
            # Add to execution history
            self.execution_history.append(result)
            
            # Trigger post-execution hooks
            await self._post_execution_hooks(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute playbook {playbook_name}: {e}")
            return ExecutionResult(
                playbook_name=playbook_name,
                status=PlaybookStatus.FAILED,
                start_time=datetime.now(),
                execution_id=self._generate_execution_id(playbook_name),
                stderr=str(e)
            )
    
    def _build_ansible_command(self, config: PlaybookConfig, mode: ExecutionMode) -> List[str]:
        """Build Ansible command with options"""
        cmd = ["ansible-playbook"]
        
        # Add playbook path
        cmd.append(config.path)
        
        # Add inventory
        cmd.extend(["-i", config.inventory])
        
        # Add execution mode options
        if mode == ExecutionMode.CHECK or config.check_mode:
            cmd.append("--check")
        
        if mode == ExecutionMode.DIFF or config.diff_mode:
            cmd.append("--diff")
        
        # Add tags
        if config.tags:
            cmd.extend(["--tags", ",".join(config.tags)])
        
        if config.skip_tags:
            cmd.extend(["--skip-tags", ",".join(config.skip_tags)])
        
        # Add limit
        if config.limit:
            cmd.extend(["--limit", config.limit])
        
        # Add vault password file
        if config.vault_password_file:
            cmd.extend(["--vault-password-file", config.vault_password_file])
        
        # Add become
        if config.become:
            cmd.append("--become")
        
        # Add extra variables
        if config.variables:
            for key, value in config.variables.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        # Add verbosity for debugging
        cmd.append("-v")
        
        return cmd
    
    def _parse_execution_stats(self, result: ExecutionResult) -> None:
        """Parse execution statistics from output"""
        try:
            output = result.stdout
            
            # Look for play recap
            if "PLAY RECAP" in output:
                lines = output.split('\n')
                recap_index = next(i for i, line in enumerate(lines) if "PLAY RECAP" in line)
                
                # Parse stats from recap section
                for line in lines[recap_index + 1:]:
                    if ":" in line and ("ok=" in line or "changed=" in line):
                        parts = line.split()
                        for part in parts:
                            if part.startswith("ok="):
                                result.ok_tasks += int(part.split("=")[1])
                            elif part.startswith("changed="):
                                result.changed_tasks += int(part.split("=")[1])
                            elif part.startswith("unreachable="):
                                result.unreachable_hosts += int(part.split("=")[1])
                            elif part.startswith("failed="):
                                result.failed_tasks += int(part.split("=")[1])
                            elif part.startswith("skipped="):
                                result.skipped_tasks += int(part.split("=")[1])
            
        except Exception as e:
            logger.warning(f"Failed to parse execution stats: {e}")
    
    def _generate_execution_id(self, playbook_name: str) -> str:
        """Generate unique execution ID"""
        timestamp = datetime.now().isoformat()
        data = f"{playbook_name}-{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    async def _post_execution_hooks(self, result: ExecutionResult) -> None:
        """Execute post-execution hooks"""
        try:
            # Send notifications
            if result.status == PlaybookStatus.FAILED:
                await self._send_failure_notification(result)
            
            # Update monitoring metrics
            await self._update_execution_metrics(result)
            
            # Trigger rollback if configured
            if result.status == PlaybookStatus.FAILED and self.rollback_enabled:
                await self._trigger_rollback(result)
            
        except Exception as e:
            logger.error(f"Failed to execute post-execution hooks: {e}")
    
    async def _send_failure_notification(self, result: ExecutionResult) -> None:
        """Send failure notification"""
        try:
            # This would integrate with notification systems
            logger.error(f"Playbook execution failed: {result.playbook_name}")
            logger.error(f"Error output: {result.stderr}")
            
        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")
    
    async def _update_execution_metrics(self, result: ExecutionResult) -> None:
        """Update execution metrics"""
        try:
            # This would integrate with monitoring systems
            metrics = {
                "playbook": result.playbook_name,
                "status": result.status.value,
                "duration": result.duration,
                "changed_tasks": result.changed_tasks,
                "failed_tasks": result.failed_tasks
            }
            
            logger.info(f"Execution metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"Failed to update execution metrics: {e}")
    
    async def _trigger_rollback(self, result: ExecutionResult) -> None:
        """Trigger rollback for failed execution"""
        try:
            rollback_playbook = f"{result.playbook_name}-rollback"
            
            if rollback_playbook in self.playbooks:
                logger.info(f"Triggering rollback: {rollback_playbook}")
                await self.execute_playbook(rollback_playbook)
            else:
                logger.warning(f"No rollback playbook found: {rollback_playbook}")
            
        except Exception as e:
            logger.error(f"Failed to trigger rollback: {e}")
    
    def create_inventory(self, name: str, hosts: List[InventoryHost], groups: Dict[str, List[str]] = None) -> bool:
        """Create dynamic inventory"""
        try:
            inventory = {
                "all": {
                    "children": {}
                }
            }
            
            # Add hosts
            for host in hosts:
                for group in host.groups:
                    if group not in inventory["all"]["children"]:
                        inventory["all"]["children"][group] = {
                            "hosts": {}
                        }
                    
                    inventory["all"]["children"][group]["hosts"][host.name] = {
                        "ansible_host": host.ansible_host,
                        "ansible_port": host.ansible_port,
                        **host.variables
                    }
                    
                    if host.ansible_user:
                        inventory["all"]["children"][group]["hosts"][host.name]["ansible_user"] = host.ansible_user
                    
                    if host.ansible_ssh_private_key_file:
                        inventory["all"]["children"][group]["hosts"][host.name]["ansible_ssh_private_key_file"] = host.ansible_ssh_private_key_file
            
            # Add additional groups
            if groups:
                for group_name, group_hosts in groups.items():
                    if group_name not in inventory["all"]["children"]:
                        inventory["all"]["children"][group_name] = {
                            "hosts": {}
                        }
                    
                    for host_name in group_hosts:
                        if host_name not in inventory["all"]["children"][group_name]["hosts"]:
                            inventory["all"]["children"][group_name]["hosts"][host_name] = {}
            
            # Save inventory
            inventory_path = f"{self.ansible_config_path}/inventories/{name}.yml"
            with open(inventory_path, 'w') as f:
                yaml.dump(inventory, f, default_flow_style=False)
            
            self.inventories[name] = inventory
            logger.info(f"Inventory created: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create inventory {name}: {e}")
            return False
    
    async def run_ad_hoc_command(self, module: str, args: str, inventory: str = "all", hosts: str = "all") -> Dict[str, Any]:
        """Run ad-hoc Ansible command"""
        try:
            cmd = [
                "ansible",
                hosts,
                "-i", inventory,
                "-m", module,
                "-a", args,
                "-v"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.ansible_config_path
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "module": module,
                "args": args,
                "exit_code": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "success": process.returncode == 0
            }
            
        except Exception as e:
            logger.error(f"Failed to run ad-hoc command: {e}")
            return {
                "module": module,
                "args": args,
                "exit_code": 1,
                "stderr": str(e),
                "success": False
            }
    
    def get_execution_history(self, playbook_name: str = None, limit: int = 50) -> List[ExecutionResult]:
        """Get playbook execution history"""
        try:
            history = self.execution_history
            
            # Filter by playbook name if specified
            if playbook_name:
                history = [r for r in history if r.playbook_name == playbook_name]
            
            # Sort by start time (most recent first)
            history.sort(key=lambda x: x.start_time, reverse=True)
            
            # Apply limit
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "active_executions": len(self.active_executions),
            "registered_playbooks": len(self.playbooks),
            "available_inventories": len(self.inventories),
            "execution_history_count": len(self.execution_history),
            "max_concurrent_executions": self.max_concurrent_executions,
            "default_timeout": self.default_timeout,
            "rollback_enabled": self.rollback_enabled
        }
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running execution"""
        try:
            if execution_id in self.active_executions:
                process = self.active_executions[execution_id]
                process.terminate()
                
                # Wait a bit for graceful termination
                await asyncio.sleep(5)
                
                # Force kill if still running
                if process.poll() is None:
                    process.kill()
                
                del self.active_executions[execution_id]
                logger.info(f"Execution cancelled: {execution_id}")
                return True
            else:
                logger.warning(f"Execution not found: {execution_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to cancel execution {execution_id}: {e}")
            return False

# Enterprise Playbook Orchestrator instance
playbook_orchestrator = PlaybookOrchestrator()

# Export for use in other modules
__all__ = [
    "PlaybookOrchestrator",
    "PlaybookConfig",
    "ExecutionResult",
    "InventoryHost",
    "PlaybookStatus",
    "ExecutionMode",
    "Environment",
    "playbook_orchestrator"
]