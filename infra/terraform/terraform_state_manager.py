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
Terraform State Manager

This module provides enterprise-grade Terraform state management capabilities
for the Ainflue platform infrastructure.

Features:
    - Remote state management with S3 backend
    - State locking with DynamoDB
    - Multi-environment state isolation
    - State backup and recovery
    - State encryption and security
"""

import json
import logging
import boto3
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class TerraformStateManager:
    """
    Enterprise Terraform state management for multi-cloud infrastructure.
    
    Provides secure, scalable state management with remote backends,
    state locking, and backup capabilities.
    """
    
    def __init__(self, project_name: str, environment: str, region: str = "us-west-2"):
        """
        Initialize Terraform state manager.
        
        Args:
            project_name: Name of the project
            environment: Environment (dev, staging, prod)
            region: AWS region for state backend
        """
        self.project_name = project_name
        self.environment = environment
        self.region = region
        self.bucket_name = f"{project_name}-terraform-state-{environment}"
        self.dynamodb_table = f"{project_name}-terraform-locks-{environment}"
        
        # Initialize AWS clients
        self.s3_client = boto3.client('s3', region_name=region)
        self.dynamodb_client = boto3.client('dynamodb', region_name=region)
        
    def setup_backend(self) -> Dict[str, Any]:
        """
        Set up Terraform remote backend infrastructure.
        
        Returns:
            Dict: Backend configuration details
        """
        try:
            # Create S3 bucket for state storage
            self._create_state_bucket()
            
            # Create DynamoDB table for state locking
            self._create_lock_table()
            
            # Generate backend configuration
            backend_config = self._generate_backend_config()
            
            logger.info(f"Terraform backend setup completed for {self.environment}")
            return backend_config
            
        except Exception as e:
            logger.error(f"Failed to setup Terraform backend: {str(e)}")
            raise
    
    def _create_state_bucket(self) -> None:
        """Create S3 bucket for Terraform state storage."""
        try:
            # Check if bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"State bucket {self.bucket_name} already exists")
                return
            except ClientError as e:
                if e.response['Error']['Code'] != '404':
                    raise
            
            # Create bucket
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            # Enable versioning
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Enable encryption
            self.s3_client.put_bucket_encryption(
                Bucket=self.bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )
            
            # Block public access
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            logger.info(f"Created state bucket {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"Failed to create state bucket: {str(e)}")
            raise
    
    def _create_lock_table(self) -> None:
        """Create DynamoDB table for Terraform state locking."""
        try:
            # Check if table exists
            try:
                self.dynamodb_client.describe_table(TableName=self.dynamodb_table)
                logger.info(f"Lock table {self.dynamodb_table} already exists")
                return
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceNotFoundException':
                    raise
            
            # Create table
            self.dynamodb_client.create_table(
                TableName=self.dynamodb_table,
                KeySchema=[
                    {
                        'AttributeName': 'LockID',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'LockID',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {
                        'Key': 'Project',
                        'Value': self.project_name
                    },
                    {
                        'Key': 'Environment',
                        'Value': self.environment
                    },
                    {
                        'Key': 'Purpose',
                        'Value': 'terraform-state-locking'
                    }
                ]
            )
            
            # Wait for table to be active
            waiter = self.dynamodb_client.get_waiter('table_exists')
            waiter.wait(TableName=self.dynamodb_table)
            
            logger.info(f"Created lock table {self.dynamodb_table}")
            
        except Exception as e:
            logger.error(f"Failed to create lock table: {str(e)}")
            raise
    
    def _generate_backend_config(self) -> Dict[str, Any]:
        """Generate Terraform backend configuration."""
        return {
            "terraform": {
                "backend": {
                    "s3": {
                        "bucket": self.bucket_name,
                        "key": f"{self.environment}/terraform.tfstate",
                        "region": self.region,
                        "dynamodb_table": self.dynamodb_table,
                        "encrypt": True
                    }
                }
            }
        }
    
    def init_terraform(self, terraform_dir: str) -> bool:
        """
        Initialize Terraform with remote backend.
        
        Args:
            terraform_dir: Path to Terraform configuration directory
            
        Returns:
            bool: True if successful
        """
        try:
            terraform_path = Path(terraform_dir)
            
            # Generate backend.tf file
            backend_config = self._generate_backend_config()
            backend_file = terraform_path / "backend.tf"
            
            with open(backend_file, 'w') as f:
                f.write(f"""# Terraform Backend Configuration
# Generated by TerraformStateManager

terraform {{
  backend "s3" {{
    bucket         = "{self.bucket_name}"
    key            = "{self.environment}/terraform.tfstate"
    region         = "{self.region}"
    dynamodb_table = "{self.dynamodb_table}"
    encrypt        = true
  }}
}}
""")
            
            # Run terraform init
            result = subprocess.run(
                ["terraform", "init"],
                cwd=terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Terraform initialization successful")
                return True
            else:
                logger.error(f"Terraform init failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Terraform: {str(e)}")
            return False
    
    def backup_state(self) -> Optional[str]:
        """
        Create backup of current Terraform state.
        
        Returns:
            str: Backup version ID if successful
        """
        try:
            state_key = f"{self.environment}/terraform.tfstate"
            backup_key = f"{self.environment}/backups/terraform.tfstate.{int(__import__('time').time())}"
            
            # Copy current state to backup location
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': state_key
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=backup_key
            )
            
            logger.info(f"State backup created: {backup_key}")
            return backup_key
            
        except Exception as e:
            logger.error(f"Failed to backup state: {str(e)}")
            return None
    
    def list_state_backups(self) -> List[str]:
        """
        List available state backups.
        
        Returns:
            List[str]: List of backup keys
        """
        try:
            backup_prefix = f"{self.environment}/backups/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=backup_prefix
            )
            
            backups = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    backups.append(obj['Key'])
            
            return sorted(backups, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            return []
    
    def restore_state(self, backup_key: str) -> bool:
        """
        Restore Terraform state from backup.
        
        Args:
            backup_key: S3 key of the backup to restore
            
        Returns:
            bool: True if successful
        """
        try:
            state_key = f"{self.environment}/terraform.tfstate"
            
            # Copy backup to current state location
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': backup_key
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=state_key
            )
            
            logger.info(f"State restored from backup: {backup_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore state: {str(e)}")
            return False
    
    def get_state_info(self) -> Dict[str, Any]:
        """
        Get information about current state.
        
        Returns:
            Dict: State information
        """
        try:
            state_key = f"{self.environment}/terraform.tfstate"
            
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=state_key
            )
            
            return {
                'bucket': self.bucket_name,
                'key': state_key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'etag': response['ETag'],
                'version_id': response.get('VersionId')
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {'status': 'not_found'}
            raise
        except Exception as e:
            logger.error(f"Failed to get state info: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old state backups, keeping only the specified number.
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            int: Number of backups deleted
        """
        try:
            backups = self.list_state_backups()
            
            if len(backups) <= keep_count:
                return 0
            
            to_delete = backups[keep_count:]
            deleted_count = 0
            
            for backup_key in to_delete:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=backup_key
                )
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {str(e)}")
            return 0