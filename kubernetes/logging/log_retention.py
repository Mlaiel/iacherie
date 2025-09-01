"""IA Influencer Agent - Log Retention Manager
Advanced log retention policies and lifecycle management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import shutil
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import json
import gzip
import tarfile
from concurrent.futures import ThreadPoolExecutor
import boto3
from botocore.exceptions import ClientError

from ...core.config import settings
from ...core.exceptions import LoggingError, RetentionError
from .elasticsearch_manager import ElasticsearchManager


class RetentionPeriod(str, Enum):
    """
Log retention periods"""

    DAYS_7 = "7d"
    DAYS_30 = "30d"
    DAYS_90 = "90d"
    DAYS_180 = "180d"
    DAYS_365 = "365d"
    DAYS_2555 = "2555d"  # 7 years for compliance


class CompressionType(str, Enum):
    """Compression types for archived logs"""

    GZIP = "gzip"
    BZIP2 = "bzip2"
    XZ = "xz"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"


class StorageTier(str, Enum):
    """Storage tiers for log archival"""

    HOT = "hot"          # Immediate access
    WARM = "warm"        # Infrequent access
    COLD = "cold"        # Archive
    FROZEN = "frozen"    # Deep archive


@dataclass
class RetentionPolicy:
    """Log retention policy configuration"""
    name: str
    log_patterns: List[str]
    hot_retention: RetentionPeriod
    warm_retention: Optional[RetentionPeriod] = None
    cold_retention: Optional[RetentionPeriod] = None
    delete_after: Optional[RetentionPeriod] = None
    compression: CompressionType = CompressionType.GZIP
    archive_to_s3: bool = False
    s3_bucket: Optional[str] = None
    s3_prefix: Optional[str] = None
    enabled: bool = True
    
    def get_retention_days(self, period: RetentionPeriod) -> int:
        """
Convert retention period to days"""
        return int(period.value[:-1])
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return asdict(self)


class LogFile:
    """
Log file metadata and operations"""
    
    def __init__(self, path: Path):
        self.path = path
        self.size = 0
        self.created_at: Optional[datetime] = None
        self.modified_at: Optional[datetime] = None
        self.accessed_at: Optional[datetime] = None
        self.is_compressed = False
        self.is_archived = False
        self.storage_tier = StorageTier.HOT
        self._load_metadata()
    
    def _load_metadata(self):
        """
Load file metadata"""
        if self.path.exists():
            stat = self.path.stat()
            self.size = stat.st_size
            self.created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
            self.modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            self.accessed_at = datetime.fromtimestamp(stat.st_atime, tz=timezone.utc)
            self.is_compressed = self.path.suffix in ['.gz', '.bz2', '.xz']
    
    def get_age_days(self) -> int:
        """
Get file age in days"""
        if self.created_at:
            return (datetime.now(timezone.utc) - self.created_at).days
        return 0
    
    def get_size_mb(self) -> float:
        """
Get file size in MB"""
        return self.size / (1024 * 1024)
    
    def matches_pattern(self, pattern: str) -> bool:
        """
Check if file matches pattern"""
        return self.path.match(pattern)


class LogCompressor:
    """
Log file compression utilities"""
    
    @staticmethod
    async def compress_file(file_path: Path, 
                           compression: CompressionType = CompressionType.GZIP,
                           remove_original: bool = True) -> Path:
        """
Compress a log file"""
        
        def _compress():
            if compression == CompressionType.GZIP:
                compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        
            elif compression == CompressionType.TAR_GZ:
                compressed_path = file_path.with_suffix('.tar.gz')
                with tarfile.open(compressed_path, 'w:gz') as tar:
                    tar.add(file_path, arcname=file_path.name)
                    
            elif compression == CompressionType.TAR_BZ2:
                compressed_path = file_path.with_suffix('.tar.bz2')
                with tarfile.open(compressed_path, 'w:bz2') as tar:
                    tar.add(file_path, arcname=file_path.name)
                    
            else:
                raise RetentionError(f"Unsupported compression type: {compression}")
            
            if remove_original and compressed_path.exists():
                file_path.unlink()
            
            return compressed_path
        
        # Run compression in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            compressed_path = await loop.run_in_executor(executor, _compress)
        
        logging.info(f"Compressed {file_path} to {compressed_path}")
        return compressed_path
    
    @staticmethod
    async def compress_directory(directory: Path,
                                compression: CompressionType = CompressionType.TAR_GZ,
                                output_path: Optional[Path] = None) -> Path:
        """Compress entire directory"""
        
        if not output_path:
            output_path = directory.with_suffix('.tar.gz')
        
        def _compress_dir():
            with tarfile.open(output_path, f'w:{compression.value.split(".")[-1]}') as tar:
                tar.add(directory, arcname=directory.name)
            return output_path
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, _compress_dir)
        
        logging.info(f"Compressed directory {directory} to {output_path}")
        return result


class S3Archiver:
    """S3 archival service for log files"""
    
    def __init__(self, bucket: str, region: str = "eu-central-1"):
        self.bucket = bucket
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)
    
    async def upload_file(self, 
                         local_path: Path,
                         s3_key: str,
                         storage_class: str = "STANDARD_IA") -> bool:
        """Upload file to S3"""
        
        def _upload():
            try:
                self.s3_client.upload_file(
                    str(local_path),
                    self.bucket,
                    s3_key,
                    ExtraArgs={'StorageClass': storage_class}
                )
                return True
            except ClientError as e:
                logging.error(f"Failed to upload {local_path} to S3: {e}")
                return False
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, _upload)
        
        if result:
            logging.info(f"Uploaded {local_path} to s3://{self.bucket}/{s3_key}")
        
        return result
    
    async def upload_directory(self,
                              local_directory: Path,
                              s3_prefix: str,
                              storage_class: str = "STANDARD_IA") -> Dict[str, Any]:
        """Upload directory to S3"""
        
        uploaded_files = []
        failed_files = []
        
        for file_path in local_directory.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_directory)
                s3_key = f"{s3_prefix}/{relative_path}"
                
                success = await self.upload_file(file_path, s3_key, storage_class)
                if success:
                    uploaded_files.append(str(file_path))
                else:
                    failed_files.append(str(file_path))
        
        return {
            "uploaded": len(uploaded_files),
            "failed": len(failed_files),
            "uploaded_files": uploaded_files,
            "failed_files": failed_files
        }
    
    async def list_archived_files(self, prefix: str) -> List[Dict[str, Any]]:
        """List files in S3 bucket"""
        
        def _list_files():
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket,
                    Prefix=prefix
                )
                
                files = []
                for obj in response.get('Contents', []):
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'storage_class': obj.get('StorageClass', 'STANDARD')
                    })
                
                return files
            
            except ClientError as e:
                logging.error(f"Failed to list S3 objects: {e}")
                return []
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, _list_files)
        
        return result
    
    async def transition_storage_class(self, 
                                     s3_key: str,
                                     new_storage_class: str) -> bool:
        """Transition file to different storage class"""
        
        def _transition():
            try:
                # Copy object to itself with new storage class
                copy_source = {'Bucket': self.bucket, 'Key': s3_key}
                
                self.s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=self.bucket,
                    Key=s3_key,
                    StorageClass=new_storage_class,
                    MetadataDirective='COPY'
                )
                return True
            
            except ClientError as e:
                logging.error(f"Failed to transition storage class: {e}")
                return False
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, _transition)
        
        return result


class RetentionRule:
    """Individual retention rule processor"""
    
    def __init__(self, policy: RetentionPolicy):
        self.policy = policy
        self.compressor = LogCompressor()
        self.archiver = None
        
        if policy.archive_to_s3 and policy.s3_bucket:
            self.archiver = S3Archiver(policy.s3_bucket)
    
    async def process_files(self, base_directory: Path) -> Dict[str, Any]:
        """
Process files according to retention policy"""
        
        results = {
            "processed": 0,
            "compressed": 0,
            "archived": 0,
            "deleted": 0,
            "errors": 0,
            "size_freed": 0,
            "actions": []
        }
        
        # Find matching files
        matching_files = []
        for pattern in self.policy.log_patterns:
            for file_path in base_directory.rglob(pattern):
                if file_path.is_file():
                    matching_files.append(LogFile(file_path))
        
        now = datetime.now(timezone.utc)
        
        for log_file in matching_files:
            try:
                age_days = log_file.get_age_days()
                action_taken = None
                
                # Determine action based on age and current tier
                if self.policy.delete_after:
                    delete_days = self.policy.get_retention_days(self.policy.delete_after)
                    if age_days >= delete_days:
                        # Delete file
                        original_size = log_file.size
                        log_file.path.unlink()
                        results["deleted"] += 1
                        results["size_freed"] += original_size
                        action_taken = f"deleted (age: {age_days} days)"
                        
                elif self.policy.cold_retention and log_file.storage_tier != StorageTier.FROZEN:
                    cold_days = self.policy.get_retention_days(self.policy.cold_retention)
                    if age_days >= cold_days:
                        # Move to cold storage / deep archive
                        if self.archiver:
                            s3_key = f"{self.policy.s3_prefix or 'logs'}/cold/{log_file.path.name}"
                            success = await self.archiver.upload_file(
                                log_file.path, 
                                s3_key, 
                                storage_class="DEEP_ARCHIVE"
                            )
                            if success:
                                log_file.path.unlink()
                                results["archived"] += 1
                                results["size_freed"] += log_file.size
                                action_taken = f"archived to deep storage (age: {age_days} days)"
                
                elif self.policy.warm_retention and log_file.storage_tier == StorageTier.HOT:
                    warm_days = self.policy.get_retention_days(self.policy.warm_retention)
                    if age_days >= warm_days:
                        # Move to warm storage / compress
                        if not log_file.is_compressed:
                            original_size = log_file.size
                            compressed_path = await self.compressor.compress_file(
                                log_file.path, 
                                self.policy.compression
                            )
                            new_size = compressed_path.stat().st_size
                            results["compressed"] += 1
                            results["size_freed"] += (original_size - new_size)
                            action_taken = f"compressed (age: {age_days} days, saved: {(original_size - new_size) / 1024 / 1024:.1f} MB)"
                
                elif log_file.storage_tier == StorageTier.HOT:
                    hot_days = self.policy.get_retention_days(self.policy.hot_retention)
                    if age_days >= hot_days and self.archiver:
                        # Move to warm storage
                        s3_key = f"{self.policy.s3_prefix or 'logs'}/warm/{log_file.path.name}"
                        success = await self.archiver.upload_file(
                            log_file.path,
                            s3_key,
                            storage_class="STANDARD_IA"
                        )
                        if success:
                            log_file.path.unlink()
                            results["archived"] += 1
                            results["size_freed"] += log_file.size
                            action_taken = f"archived to warm storage (age: {age_days} days)"
                
                if action_taken:
                    results["actions"].append({
                        "file": str(log_file.path),
                        "action": action_taken,
                        "age_days": age_days,
                        "original_size": log_file.size
                    })
                
                results["processed"] += 1
                
            except Exception as e:
                logging.error(f"Error processing file {log_file.path}: {e}")
                results["errors"] += 1
        
        return results


class LogRetentionManager:
    """Advanced log retention manager for IA Influencer Agent"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("/etc/ia-influencer/retention.json")
        self.policies: List[RetentionPolicy] = []
        self.elasticsearch_manager: Optional[ElasticsearchManager] = None
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Load default retention policies for IA Influencer Agent"""
        
        # Application logs - 90 days hot, 180 days warm, 365 days cold
        app_policy = RetentionPolicy(
            name="application_logs",
            log_patterns=["*.log", "app-*.log", "api-*.log"],
            hot_retention=RetentionPeriod.DAYS_90,
            warm_retention=RetentionPeriod.DAYS_180,
            cold_retention=RetentionPeriod.DAYS_365,
            delete_after=RetentionPeriod.DAYS_2555,  # 7 years for compliance
            compression=CompressionType.GZIP,
            archive_to_s3=True,
            s3_bucket="ia-influencer-logs-archive",
            s3_prefix="application"
        )
        
        # AI processing logs - 30 days hot, 90 days warm, 180 days cold
        ai_policy = RetentionPolicy(
            name="ai_processing_logs",
            log_patterns=["ai-*.log", "*-ml-*.log", "*-fingerprint-*.log"],
            hot_retention=RetentionPeriod.DAYS_30,
            warm_retention=RetentionPeriod.DAYS_90,
            cold_retention=RetentionPeriod.DAYS_180,
            delete_after=RetentionPeriod.DAYS_365,
            compression=CompressionType.GZIP,
            archive_to_s3=True,
            s3_bucket="ia-influencer-logs-archive",
            s3_prefix="ai-processing"
        )
        
        # Error logs - longer retention for debugging
        error_policy = RetentionPolicy(
            name="error_logs",
            log_patterns=["*error*.log", "*exception*.log", "*crash*.log"],
            hot_retention=RetentionPeriod.DAYS_180,
            warm_retention=RetentionPeriod.DAYS_365,
            cold_retention=RetentionPeriod.DAYS_2555,
            compression=CompressionType.GZIP,
            archive_to_s3=True,
            s3_bucket="ia-influencer-logs-archive",
            s3_prefix="errors"
        )
        
        # Audit logs - longest retention for compliance
        audit_policy = RetentionPolicy(
            name="audit_logs",
            log_patterns=["audit-*.log", "*-security-*.log", "*-access-*.log"],
            hot_retention=RetentionPeriod.DAYS_365,
            warm_retention=RetentionPeriod.DAYS_2555,
            compression=CompressionType.GZIP,
            archive_to_s3=True,
            s3_bucket="ia-influencer-logs-archive",
            s3_prefix="audit"
        )
        
        # Performance logs - shorter retention
        performance_policy = RetentionPolicy(
            name="performance_logs",
            log_patterns=["*-performance-*.log", "*-metrics-*.log", "*-stats-*.log"],
            hot_retention=RetentionPeriod.DAYS_7,
            warm_retention=RetentionPeriod.DAYS_30,
            cold_retention=RetentionPeriod.DAYS_90,
            delete_after=RetentionPeriod.DAYS_180,
            compression=CompressionType.GZIP,
            archive_to_s3=False
        )
        
        self.policies = [app_policy, ai_policy, error_policy, audit_policy, performance_policy]
    
    async def load_config(self):
        """Load retention configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                self.policies = []
                for policy_data in config_data.get("policies", []):
                    policy = RetentionPolicy(**policy_data)
                    self.policies.append(policy)
                
                logging.info(f"Loaded {len(self.policies)} retention policies from {self.config_path}")
                
            except Exception as e:
                logging.error(f"Failed to load retention config: {e}")
                # Keep default policies
    
    async def save_config(self):
        """Save retention configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "policies": [policy.to_dict() for policy in self.policies],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logging.info(f"Saved retention configuration to {self.config_path}")
            
        except Exception as e:
            logging.error(f"Failed to save retention config: {e}")
            raise RetentionError(f"Config save failed: {e}")
    
    def add_policy(self, policy: RetentionPolicy):
        """Add retention policy"""
        self.policies.append(policy)
    
    def remove_policy(self, policy_name: str) -> bool:
        """
Remove retention policy by name"""
        for i, policy in enumerate(self.policies):
            if policy.name == policy_name:
                del self.policies[i]
                return True
        return False
    
    def get_policy(self, policy_name: str) -> Optional[RetentionPolicy]:
        """
Get retention policy by name"""
        for policy in self.policies:
            if policy.name == policy_name:
                return policy
        return None
    
    async def run_retention(self, log_directory: Path) -> Dict[str, Any]:
        """
Run retention policies on log directory"""
        
        if not log_directory.exists():
            raise RetentionError(f"Log directory does not exist: {log_directory}")
        
        start_time = datetime.now(timezone.utc)
        overall_results = {
            "start_time": start_time.isoformat(),
            "policies_processed": 0,
            "total_processed": 0,
            "total_compressed": 0,
            "total_archived": 0,
            "total_deleted": 0,
            "total_errors": 0,
            "total_size_freed": 0,
            "policy_results": {},
            "duration_seconds": 0
        }
        
        for policy in self.policies:
            if not policy.enabled:
                continue
            
            try:
                rule = RetentionRule(policy)
                policy_results = await rule.process_files(log_directory)
                
                overall_results["policy_results"][policy.name] = policy_results
                overall_results["policies_processed"] += 1
                overall_results["total_processed"] += policy_results["processed"]
                overall_results["total_compressed"] += policy_results["compressed"]
                overall_results["total_archived"] += policy_results["archived"]
                overall_results["total_deleted"] += policy_results["deleted"]
                overall_results["total_errors"] += policy_results["errors"]
                overall_results["total_size_freed"] += policy_results["size_freed"]
                
                logging.info(f"Completed retention policy '{policy.name}': "
                           f"processed={policy_results['processed']}, "
                           f"compressed={policy_results['compressed']}, "
                           f"archived={policy_results['archived']}, "
                           f"deleted={policy_results['deleted']}")
                
            except Exception as e:
                logging.error(f"Error running retention policy '{policy.name}': {e}")
                overall_results["total_errors"] += 1
        
        end_time = datetime.now(timezone.utc)
        overall_results["end_time"] = end_time.isoformat()
        overall_results["duration_seconds"] = (end_time - start_time).total_seconds()
        
        self.last_run = end_time
        
        # Log summary
        freed_mb = overall_results["total_size_freed"] / 1024 / 1024
        logging.info(f"Retention run completed: "
                   f"processed={overall_results['total_processed']} files, "
                   f"freed={freed_mb:.1f} MB, "
                   f"duration={overall_results['duration_seconds']:.1f}s")
        
        return overall_results
    
    async def cleanup_elasticsearch_indices(self) -> Dict[str, Any]:
        """Cleanup old Elasticsearch indices"""
        if not self.elasticsearch_manager:
            return {"error": "Elasticsearch manager not configured"}
        
        try:
            # Find retention policy for Elasticsearch logs
            es_policy = None
            for policy in self.policies:
                if "elasticsearch" in policy.name.lower() or "index" in policy.name.lower():
                    es_policy = policy
                    break
            
            if not es_policy:
                # Use default retention
                retention_days = 30
            else:
                retention_days = es_policy.get_retention_days(es_policy.delete_after or es_policy.cold_retention)
            
            deleted_indices = await self.elasticsearch_manager.cleanup_old_indices(retention_days)
            
            return {
                "deleted_indices": deleted_indices,
                "retention_days": retention_days,
                "count": len(deleted_indices)
            }
            
        except Exception as e:
            logging.error(f"Failed to cleanup Elasticsearch indices: {e}")
            return {"error": str(e)}
    
    async def get_retention_statistics(self, log_directory: Path) -> Dict[str, Any]:
        """Get retention statistics for log directory"""
        
        stats = {
            "total_files": 0,
            "total_size": 0,
            "compressed_files": 0,
            "compressed_size": 0,
            "file_age_distribution": {},
            "size_by_age": {},
            "policy_coverage": {}
        }
        
        all_files = []
        for file_path in log_directory.rglob('*'):
            if file_path.is_file():
                all_files.append(LogFile(file_path))
        
        stats["total_files"] = len(all_files)
        
        for log_file in all_files:
            stats["total_size"] += log_file.size
            
            if log_file.is_compressed:
                stats["compressed_files"] += 1
                stats["compressed_size"] += log_file.size
            
            # Age distribution
            age_days = log_file.get_age_days()
            age_bucket = f"{age_days//30*30}-{age_days//30*30+29} days"
            stats["file_age_distribution"][age_bucket] = stats["file_age_distribution"].get(age_bucket, 0) + 1
            stats["size_by_age"][age_bucket] = stats["size_by_age"].get(age_bucket, 0) + log_file.size
            
            # Policy coverage
            for policy in self.policies:
                if any(log_file.matches_pattern(pattern) for pattern in policy.log_patterns):
                    stats["policy_coverage"][policy.name] = stats["policy_coverage"].get(policy.name, 0) + 1
        
        # Convert sizes to human readable
        stats["total_size_mb"] = stats["total_size"] / 1024 / 1024
        stats["compressed_size_mb"] = stats["compressed_size"] / 1024 / 1024
        stats["compression_ratio"] = stats["compressed_size"] / max(stats["total_size"], 1)
        
        return stats
    
    async def start_scheduler(self, interval_hours: int = 24):
        """Start automatic retention scheduler"""
        self.is_running = True
        
        while self.is_running:
            try:
                # Run retention on default log directory
                log_dir = Path(getattr(settings, 'LOG_DIRECTORY', '/var/log/ia-influencer'))
                if log_dir.exists():
                    await self.run_retention(log_dir)
                
                # Cleanup Elasticsearch indices
                await self.cleanup_elasticsearch_indices()
                
            except Exception as e:
                logging.error(f"Error in retention scheduler: {e}")
            
            # Wait for next run
            await asyncio.sleep(interval_hours * 3600)
    
    async def stop_scheduler(self):
        """Stop automatic retention scheduler"""
        self.is_running = False
        logging.info("Retention scheduler stopped")
    
    def set_elasticsearch_manager(self, es_manager: ElasticsearchManager):
        """Set Elasticsearch manager for index cleanup"""
        self.elasticsearch_manager = es_manager
