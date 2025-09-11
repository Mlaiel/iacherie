"""MongoDB Backup Retention Policy
=================================

Intelligent backup retention with lifecycle management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class RetentionPeriod(Enum):
    """Retention period enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

@dataclass
class RetentionRule:
    """Backup retention rule."""
    period: RetentionPeriod
    count: int  # Number of backups to retain

class RetentionPolicy:
    """Intelligent backup retention policy manager."""
    
    def __init__(self, rules: List[RetentionRule] = None):
        """Initialize retention policy.
        
        Args:
            rules: List of retention rules
        """
        self.rules = rules or [
            RetentionRule(RetentionPeriod.DAILY, 7),
            RetentionRule(RetentionPeriod.WEEKLY, 4),
            RetentionRule(RetentionPeriod.MONTHLY, 12),
            RetentionRule(RetentionPeriod.YEARLY, 5)
        ]
    
    def apply_retention_policy(self, backup_files: List[str]) -> List[str]:
        """Apply retention policy and return files to delete.
        
        Args:
            backup_files: List of backup file paths
            
        Returns:
            List of files to delete
        """
        files_to_delete = []
        
        # Group files by age
        file_ages = {}
        for file_path in backup_files:
            try:
                mtime = os.path.getmtime(file_path)
                file_ages[file_path] = datetime.fromtimestamp(mtime)
            except OSError:
                continue
        
        # Apply each retention rule
        for rule in self.rules:
            files_in_period = self._get_files_in_period(file_ages, rule.period)
            
            # Sort by date descending (newest first)
            sorted_files = sorted(files_in_period, key=lambda f: file_ages[f], reverse=True)
            
            # Mark excess files for deletion
            if len(sorted_files) > rule.count:
                files_to_delete.extend(sorted_files[rule.count:])
        
        return list(set(files_to_delete))
    
    def _get_files_in_period(self, file_ages: Dict[str, datetime], period: RetentionPeriod) -> List[str]:
        """Get files within retention period."""
        now = datetime.now()
        
        if period == RetentionPeriod.DAILY:
            cutoff = now - timedelta(days=1)
        elif period == RetentionPeriod.WEEKLY:
            cutoff = now - timedelta(weeks=1)
        elif period == RetentionPeriod.MONTHLY:
            cutoff = now - timedelta(days=30)
        elif period == RetentionPeriod.YEARLY:
            cutoff = now - timedelta(days=365)
        else:
            cutoff = now
        
        return [file_path for file_path, age in file_ages.items() if age >= cutoff]

__all__ = ['RetentionPolicy', 'RetentionRule', 'RetentionPeriod']