"""
Infrastructure Provisioner module
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
Infrastructure Provisioner

This module provides enterprise-grade infrastructure provisioning capabilities
using Terraform for the Ainflue platform.

Features:
    - Multi-cloud infrastructure provisioning
    - Environment-specific deployments
    - Infrastructure validation and testing
    - Resource dependency management
    - Rollback capabilities
"""

import logging
import subprocess
import json
import yaml
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProvisioningStatus(Enum):
    """Infrastructure provisioning status."""
    PENDING = "pending"
    PLANNING = "planning"
    APPLYING = "applying"
    COMPLETE = "complete"
    FAILED = "failed"
    DESTROYING = "destroying"

@dataclass
class ProvisioningResult:
    """Result of infrastructure provisioning operation."""
    status: ProvisioningStatus
    message: str
    outputs: Optional[Dict[str, Any]] = None
    resources_created: Optional[int] = None
    resources_updated: Optional[int] = None
    resources_destroyed: Optional[int] = None
    duration: Optional[float] = None
    errors: Optional[List[str]] = None

class InfrastructureProvisioner:
    """
    Enterprise infrastructure provisioning with Terraform.
    
    Provides comprehensive infrastructure deployment capabilities
    with validation, testing, and rollback support.
    """
    
    def __init__(self, project_name -> None: str, environment -> None: str, terraform_dir -> None: str) -> None:
        """
        Initialize infrastructure provisioner.
        
        Args:
            project_name: Name of the project
            environment: Environment (dev, staging, prod)
            terraform_dir: Path to Terraform configuration directory
        """
        self.project_name = project_name
        self.environment = environment
        self.terraform_dir = Path(terraform_dir)
        self.state_manager = None
        
        # Validate Terraform directory
        if not self.terraform_dir.exists():
            raise ValueError(f"Terraform directory does not exist: {terraform_dir}")
    
    def set_state_manager(self, state_manager) -> None:
        """Set Terraform state manager."""
        self.state_manager = state_manager
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """
        Validate Terraform configuration.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Check for required files
            required_files = ['main.tf', 'variables.tf', 'outputs.tf']
            for file_name in required_files:
                file_path = self.terraform_dir / file_name
                if not file_path.exists():
                    errors.append(f"Required file missing: {file_name}")
            
            # Validate Terraform syntax
            result = subprocess.run(
                ["terraform", "validate"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                errors.append(f"Terraform validation failed: {result.stderr}")
            
            # Check for Terraform formatting
            result = subprocess.run(
                ["terraform", "fmt", "-check"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                errors.append("Terraform files are not properly formatted")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Configuration validation failed: {str(e)}")
            return False, errors
    
    def plan_infrastructure(self, variables: Optional[Dict[str, Any]] = None) -> ProvisioningResult:
        """
        Create Terraform execution plan.
        
        Args:
            variables: Terraform variables to override
            
        Returns:
            ProvisioningResult: Plan result
        """
        import time
        start_time = time.time()
        
        try:
            # Validate configuration first
            is_valid, errors = self.validate_configuration()
            if not is_valid:
                return ProvisioningResult(
                    status=ProvisioningStatus.FAILED,
                    message="Configuration validation failed",
                    errors=errors,
                    duration=time.time() - start_time
                )
            
            # Initialize Terraform if state manager is available
            if self.state_manager:
                self.state_manager.init_terraform(str(self.terraform_dir))
            
            # Build terraform plan command
            cmd = ["terraform", "plan", "-detailed-exitcode"]
            
            # Add variable files
            var_files = list(self.terraform_dir.glob("*.tfvars"))
            for var_file in var_files:
                cmd.extend(["-var-file", str(var_file)])
            
            # Add environment-specific variables
            env_var_file = self.terraform_dir / f"{self.environment}.tfvars"
            if env_var_file.exists():
                cmd.extend(["-var-file", str(env_var_file)])
            
            # Add inline variables
            if variables:
                for key, value in variables.items():
                    cmd.extend(["-var", f"{key}={value}"])
            
            # Execute plan
            result = subprocess.run(
                cmd,
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return ProvisioningResult(
                    status=ProvisioningStatus.COMPLETE,
                    message="No changes needed",
                    duration=duration
                )
            elif result.returncode == 2:
                return ProvisioningResult(
                    status=ProvisioningStatus.PENDING,
                    message="Changes detected, ready to apply",
                    duration=duration
                )
            else:
                return ProvisioningResult(
                    status=ProvisioningStatus.FAILED,
                    message="Plan failed",
                    errors=[result.stderr],
                    duration=duration
                )
                
        except Exception as e:
            return ProvisioningResult(
                status=ProvisioningStatus.FAILED,
                message=f"Plan execution failed: {str(e)}",
                duration=time.time() - start_time
            )
    
    def apply_infrastructure(self, auto_approve: bool = False, 
                           variables: Optional[Dict[str, Any]] = None) -> ProvisioningResult:
        """
        Apply Terraform configuration.
        
        Args:
            auto_approve: Skip interactive approval
            variables: Terraform variables to override
            
        Returns:
            ProvisioningResult: Apply result
        """
        import time
        start_time = time.time()
        
        try:
            # Create backup if state manager is available
            if self.state_manager:
                backup_key = self.state_manager.backup_state()
                if backup_key:
                    logger.info(f"State backup created: {backup_key}")
            
            # Build terraform apply command
            cmd = ["terraform", "apply"]
            
            if auto_approve:
                cmd.append("-auto-approve")
            
            # Add variable files
            var_files = list(self.terraform_dir.glob("*.tfvars"))
            for var_file in var_files:
                cmd.extend(["-var-file", str(var_file)])
            
            # Add environment-specific variables
            env_var_file = self.terraform_dir / f"{self.environment}.tfvars"
            if env_var_file.exists():
                cmd.extend(["-var-file", str(env_var_file)])
            
            # Add inline variables
            if variables:
                for key, value in variables.items():
                    cmd.extend(["-var", f"{key}={value}"])
            
            # Execute apply
            result = subprocess.run(
                cmd,
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                # Get outputs
                outputs = self._get_terraform_outputs()
                
                # Parse resource changes from output
                resources_created, resources_updated = self._parse_apply_output(result.stdout)
                
                return ProvisioningResult(
                    status=ProvisioningStatus.COMPLETE,
                    message="Infrastructure applied successfully",
                    outputs=outputs,
                    resources_created=resources_created,
                    resources_updated=resources_updated,
                    duration=duration
                )
            else:
                return ProvisioningResult(
                    status=ProvisioningStatus.FAILED,
                    message="Apply failed",
                    errors=[result.stderr],
                    duration=duration
                )
                
        except Exception as e:
            return ProvisioningResult(
                status=ProvisioningStatus.FAILED,
                message=f"Apply execution failed: {str(e)}",
                duration=time.time() - start_time
            )
    
    def destroy_infrastructure(self, auto_approve: bool = False,
                             variables: Optional[Dict[str, Any]] = None) -> ProvisioningResult:
        """
        Destroy Terraform-managed infrastructure.
        
        Args:
            auto_approve: Skip interactive approval
            variables: Terraform variables to override
            
        Returns:
            ProvisioningResult: Destroy result
        """
        import time
        start_time = time.time()
        
        try:
            # Create backup before destruction
            if self.state_manager:
                backup_key = self.state_manager.backup_state()
                if backup_key:
                    logger.info(f"State backup created before destruction: {backup_key}")
            
            # Build terraform destroy command
            cmd = ["terraform", "destroy"]
            
            if auto_approve:
                cmd.append("-auto-approve")
            
            # Add variable files
            var_files = list(self.terraform_dir.glob("*.tfvars"))
            for var_file in var_files:
                cmd.extend(["-var-file", str(var_file)])
            
            # Add environment-specific variables
            env_var_file = self.terraform_dir / f"{self.environment}.tfvars"
            if env_var_file.exists():
                cmd.extend(["-var-file", str(env_var_file)])
            
            # Add inline variables
            if variables:
                for key, value in variables.items():
                    cmd.extend(["-var", f"{key}={value}"])
            
            # Execute destroy
            result = subprocess.run(
                cmd,
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                # Parse resource changes from output
                resources_destroyed = self._parse_destroy_output(result.stdout)
                
                return ProvisioningResult(
                    status=ProvisioningStatus.COMPLETE,
                    message="Infrastructure destroyed successfully",
                    resources_destroyed=resources_destroyed,
                    duration=duration
                )
            else:
                return ProvisioningResult(
                    status=ProvisioningStatus.FAILED,
                    message="Destroy failed",
                    errors=[result.stderr],
                    duration=duration
                )
                
        except Exception as e:
            return ProvisioningResult(
                status=ProvisioningStatus.FAILED,
                message=f"Destroy execution failed: {str(e)}",
                duration=time.time() - start_time
            )
    
    def _get_terraform_outputs(self) -> Optional[Dict[str, Any]]:
        """Get Terraform outputs as JSON."""
        try:
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
            
        except Exception:
            return None
    
    def _parse_apply_output(self, output: str) -> Tuple[int, int]:
        """Parse apply output to count created and updated resources."""
        lines = output.split('\n')
        created = 0
        updated = 0
        
        for line in lines:
            if " created" in line:
                try:
                    created = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
            elif " changed" in line:
                try:
                    updated = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
        
        return created, updated
    
    def _parse_destroy_output(self, output: str) -> int:
        """Parse destroy output to count destroyed resources."""
        lines = output.split('\n')
        destroyed = 0
        
        for line in lines:
            if " destroyed" in line:
                try:
                    destroyed = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
        
        return destroyed
    
    def get_infrastructure_state(self) -> Dict[str, Any]:
        """
        Get current infrastructure state information.
        
        Returns:
            Dict: State information
        """
        try:
            # Get state info from state manager
            state_info = {}
            if self.state_manager:
                state_info = self.state_manager.get_state_info()
            
            # Get Terraform outputs
            outputs = self._get_terraform_outputs()
            
            # Get resource list
            result = subprocess.run(
                ["terraform", "state", "list"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            resources = []
            if result.returncode == 0:
                resources = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            return {
                'state_info': state_info,
                'outputs': outputs,
                'resources': resources,
                'resource_count': len(resources),
                'project': self.project_name,
                'environment': self.environment
            }
            
        except Exception as e:
            logger.error(f"Failed to get infrastructure state: {str(e)}")
            return {'error': str(e)}
    
    def refresh_state(self) -> bool:
        """
        Refresh Terraform state to sync with actual infrastructure.
        
        Returns:
            bool: True if successful
        """
        try:
            result = subprocess.run(
                ["terraform", "refresh"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to refresh state: {str(e)}")
            return False
    
    def import_resource(self, resource_address: str, resource_id: str) -> bool:
        """
        Import existing resource into Terraform state.
        
        Args:
            resource_address: Terraform resource address
            resource_id: Cloud provider resource ID
            
        Returns:
            bool: True if successful
        """
        try:
            result = subprocess.run(
                ["terraform", "import", resource_address, resource_id],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully imported resource: {resource_address}")
                return True
            else:
                logger.error(f"Failed to import resource: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Import operation failed: {str(e)}")
            return False