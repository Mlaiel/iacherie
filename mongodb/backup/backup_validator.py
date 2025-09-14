"""MongoDB Backup Validator
=========================

Backup integrity validation and corruption detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import os
import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Backup validation result."""
    is_valid: bool
    checksum_valid: bool
    structure_valid: bool
    size_valid: bool
    errors: List[str]
    warnings: List[str]

class BackupValidator:
    """Backup integrity validator with checksums and structure validation."""
    
    def __init__(self) -> None:
        """Initialize backup validator."""
        pass
    
    def validate_backup(self, backup_path: str, expected_checksum: str = None) -> ValidationResult:
        """Validate backup file integrity.
        
        Args:
            backup_path: Path to backup file
            expected_checksum: Expected file checksum
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check file exists
        if not os.path.exists(backup_path):
            errors.append(f"Backup file not found: {backup_path}")
            return ValidationResult(False, False, False, False, errors, warnings)
        
        # Validate checksum
        checksum_valid = True
        if expected_checksum:
            actual_checksum = self._calculate_checksum(backup_path)
            if actual_checksum != expected_checksum:
                errors.append(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
                checksum_valid = False
        
        # Validate file size
        size_valid = self._validate_file_size(backup_path)
        if not size_valid:
            warnings.append("Backup file size is unusually small")
        
        # Validate structure
        structure_valid = self._validate_backup_structure(backup_path)
        if not structure_valid:
            errors.append("Invalid backup file structure")
        
        is_valid = checksum_valid and structure_valid and len(errors) == 0
        
        return ValidationResult(is_valid, checksum_valid, structure_valid, size_valid, errors, warnings)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _validate_file_size(self, file_path: str) -> bool:
        """Validate file size is reasonable."""
        file_size = os.path.getsize(file_path)
        return file_size > 100  # At least 100 bytes
    
    def _validate_backup_structure(self, file_path: str) -> bool:
        """Validate backup file structure."""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    json.load(f)
                return True
            else:
                # For other formats, just check if file is readable
                with open(file_path, 'rb') as f:
                    f.read(1024)  # Read first 1KB
                return True
        except Exception:
            return False

__all__ = ['BackupValidator', 'ValidationResult']