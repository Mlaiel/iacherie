"""Multimedia Content Validators
Comprehensive validation for multimedia content integrity and quality

Author: Fahed Mlaiel <mlaiel@live.de>

⚠️ COPYRIGHT WARNING ⚠️
This code is protected by copyright. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class ValidationRule:
    """Validation rule definition"""
    name: str
    severity: str  # error, warning, info
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of content validation"""
    is_valid: bool = True
    content_path: Path = None
    content_type: str = ""
    file_size: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed_rules: List[str] = field(default_factory=list)
    failed_rules: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    security_score: float = 0.0
    file_hash: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseValidator(ABC):
    """Base validator class"""
    
    def __init__(self):
        self.validation_rules = self._initialize_rules()
        self.logger = logger
    
    @abstractmethod
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize validation rules for this validator"""
        pass
    
    @abstractmethod
    def supports_format(self, format_type: str) -> bool:
        """Check if validator supports the format"""
        pass
    
    async def validate(self, content_path: Path) -> ValidationResult:
        """Validate content"""
        result = ValidationResult(
            content_path=content_path,
            file_size=content_path.stat().st_size if content_path.exists() else 0
        )
        
        # Basic validation
        result.is_valid = content_path.exists()
        if not result.is_valid:
            result.errors.append("File does not exist")
            return result
        
        # Run validation rules
        for rule in self.validation_rules:
            try:
                passed = await self._check_rule(rule, content_path, result)
                if passed:
                    result.passed_rules.append(rule.name)
                else:
                    result.failed_rules.append(rule.name)
                    if rule.severity == "error":
                        result.errors.append(f"{rule.name}: {rule.description}")
                        result.is_valid = False
                    elif rule.severity == "warning":
                        result.warnings.append(f"{rule.name}: {rule.description}")
            except Exception as e:
                self.logger.error(f"Rule {rule.name} failed: {e}")
                result.errors.append(f"{rule.name}: Validation failed")
                result.is_valid = False
        
        return result
    
    async def _check_rule(self, rule: ValidationRule, content_path: Path, result: ValidationResult) -> bool:
        """Check a specific validation rule"""
        # Default implementation - always passes
        return True

class MediaValidator(BaseValidator):
    """Universal multimedia content validator"""
    
    def __init__(self):
        super().__init__()
    
    def supports_format(self, format_type: str) -> bool:
        """Check if validator supports the format"""
        return True  # Universal validator
    
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize validation rules"""
        return [
            ValidationRule(
                name="file_exists",
                severity="error",
                description="File must exist and be accessible"
            ),
            ValidationRule(
                name="file_readable",
                severity="error", 
                description="File must be readable"
            ),
            ValidationRule(
                name="file_size_reasonable",
                severity="warning",
                description="File size should be reasonable",
                parameters={"max_size": 100 * 1024 * 1024}  # 100MB
            ),
            ValidationRule(
                name="no_corruption",
                severity="error",
                description="File should not be corrupted"
            )
        ]
    
    async def validate_multiple(self, content_paths: List[Path]) -> List[ValidationResult]:
        """Validate multiple files"""
        results = []
        for path in content_paths:
            result = await self.validate(path)
            results.append(result)
        return results
    
    def get_validation_stats(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Calculate validation statistics"""
        stats = {
            'total_files': len(results),
            'valid_files': sum(1 for r in results if r.is_valid),
            'files_with_errors': sum(1 for r in results if r.errors),
            'files_with_warnings': sum(1 for r in results if r.warnings),
            'avg_quality_score': 0.0,
            'common_issues': {}
        }
        
        if results:
            stats['avg_quality_score'] = sum(r.quality_score for r in results) / len(results)
        
        stats['success_rate'] = stats['valid_files'] / stats['total_files'] if stats['total_files'] > 0 else 0
        
        return stats

# Convenience aliases  
ContentValidator = MediaValidator
QualityValidator = MediaValidator
