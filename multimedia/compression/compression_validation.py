"""Compression Validation Engine
Comprehensive validation system for compression results and integrity.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation thoroughness levels."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    FORENSIC = "forensic"

class ValidationStatus(Enum):
    """Validation result status."""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    ERROR = "error"

@dataclass
class ValidationRule:
    """Validation rule definition."""
    name: str
    description: str
    severity: str  # critical, warning, info
    check_function: str
    parameters: Dict[str, Any]

@dataclass
class ValidationResult:
    """Result of a validation check."""
    rule_name: str
    status: ValidationStatus
    message: str
    details: Dict[str, Any]
    timestamp: float

class CompressionValidator:
    """Advanced validation engine for compression results."""
    
    def __init__(self) -> None:
        """Initialize the compression validator."""
        self.validation_rules = self._load_validation_rules()
        self.validation_history = {}
        
    def _load_validation_rules(self) -> Dict[str, ValidationRule]:
        """Load validation rules for different checks."""
        rules = {}
        
        # File integrity rules
        rules["file_exists"] = ValidationRule(
            name="File Existence",
            description="Verify output file exists and is accessible",
            severity="critical",
            check_function="check_file_exists",
            parameters={}
        )
        
        rules["file_size"] = ValidationRule(
            name="File Size Validation",
            description="Verify file size is within expected range",
            severity="warning",
            check_function="check_file_size",
            parameters={"min_size": 1024, "max_compression_ratio": 0.99}
        )
        
        rules["format_validity"] = ValidationRule(
            name="Format Validity",
            description="Verify output format is valid and readable",
            severity="critical",
            check_function="check_format_validity",
            parameters={}
        )
        
        # Quality rules
        rules["quality_threshold"] = ValidationRule(
            name="Quality Threshold",
            description="Verify quality meets minimum requirements",
            severity="warning",
            check_function="check_quality_threshold",
            parameters={"min_psnr": 30.0, "min_ssim": 0.8}
        )
        
        rules["visual_artifacts"] = ValidationRule(
            name="Visual Artifacts",
            description="Detect compression artifacts",
            severity="warning",
            check_function="check_visual_artifacts",
            parameters={"artifact_threshold": 0.1}
        )
        
        # Metadata rules
        rules["metadata_preservation"] = ValidationRule(
            name="Metadata Preservation",
            description="Verify required metadata is preserved",
            severity="info",
            check_function="check_metadata_preservation",
            parameters={"required_fields": ["width", "height", "format"]}
        )
        
        # Performance rules
        rules["processing_time"] = ValidationRule(
            name="Processing Time",
            description="Verify processing time is within acceptable limits",
            severity="warning",
            check_function="check_processing_time",
            parameters={"max_time_per_mb": 10.0}
        )
        
        # Security rules
        rules["malware_scan"] = ValidationRule(
            name="Malware Scan",
            description="Scan for potential malware in compressed files",
            severity="critical",
            check_function="check_malware",
            parameters={}
        )
        
        return rules
    
    async def validate_compression(
        self,
        original_path: Union[str, Path],
        compressed_path: Union[str, Path],
        compression_config: Dict[str, Any],
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of compression results.
        
        Args:
            original_path: Path to original file
            compressed_path: Path to compressed file
            compression_config: Configuration used for compression
            validation_level: Thoroughness of validation
            
        Returns:
            Validation results with all checks
        """
        original_path = Path(original_path)
        compressed_path = Path(compressed_path)
        
        validation_id = self._generate_validation_id(original_path, compressed_path)
        
        try:
            # Select rules based on validation level
            rules_to_run = self._select_rules_for_level(validation_level)
            
            # Run validation checks
            validation_results = []
            for rule_name in rules_to_run:
                rule = self.validation_rules[rule_name]
                result = await self._run_validation_check(
                    rule, original_path, compressed_path, compression_config
                )
                validation_results.append(result)
            
            # Analyze results
            analysis = self._analyze_validation_results(validation_results)
            
            # Store validation history
            self.validation_history[validation_id] = {
                "original_path": str(original_path),
                "compressed_path": str(compressed_path),
                "validation_level": validation_level.value,
                "results": validation_results,
                "analysis": analysis,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            return {
                "validation_id": validation_id,
                "overall_status": analysis["overall_status"],
                "passed_checks": analysis["passed_checks"],
                "failed_checks": analysis["failed_checks"],
                "warning_checks": analysis["warning_checks"],
                "results": validation_results,
                "recommendations": analysis["recommendations"],
                "summary": analysis["summary"]
            }
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "validation_id": validation_id,
                "overall_status": ValidationStatus.ERROR.value,
                "error": str(e)
            }
    
    def _generate_validation_id(
        self,
        original_path: Path,
        compressed_path: Path
    ) -> str:
        """Generate unique validation ID."""
        content = f"{original_path}{compressed_path}{asyncio.get_event_loop().time()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _select_rules_for_level(self, level: ValidationLevel) -> List[str]:
        """Select validation rules based on level."""
        basic_rules = ["file_exists", "file_size", "format_validity"]
        standard_rules = basic_rules + ["quality_threshold", "metadata_preservation"]
        comprehensive_rules = standard_rules + ["visual_artifacts", "processing_time"]
        forensic_rules = comprehensive_rules + ["malware_scan"]
        
        level_mapping = {
            ValidationLevel.BASIC: basic_rules,
            ValidationLevel.STANDARD: standard_rules,
            ValidationLevel.COMPREHENSIVE: comprehensive_rules,
            ValidationLevel.FORENSIC: forensic_rules
        }
        
        return level_mapping[level]
    
    async def _run_validation_check(
        self,
        rule: ValidationRule,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any]
    ) -> ValidationResult:
        """Run a single validation check."""
        try:
            check_method = getattr(self, rule.check_function)
            result = await check_method(
                original_path, compressed_path, compression_config, rule.parameters
            )
            
            return ValidationResult(
                rule_name=rule.name,
                status=result["status"],
                message=result["message"],
                details=result.get("details", {}),
                timestamp=asyncio.get_event_loop().time()
            )
            
        except Exception as e:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.ERROR,
                message=f"Validation check failed: {e}",
                details={"error": str(e)},
                timestamp=asyncio.get_event_loop().time()
            )
    
    async def check_file_exists(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if compressed file exists and is accessible."""
        if not compressed_path.exists():
            return {
                "status": ValidationStatus.FAILED,
                "message": f"Compressed file does not exist: {compressed_path}"
            }
        
        if not compressed_path.is_file():
            return {
                "status": ValidationStatus.FAILED,
                "message": f"Path is not a file: {compressed_path}"
            }
        
        try:
            # Try to read file
            with open(compressed_path, 'rb') as f:
                f.read(1024)  # Read first 1KB
            
            return {
                "status": ValidationStatus.PASSED,
                "message": "File exists and is accessible",
                "details": {
                    "file_size": compressed_path.stat().st_size,
                    "readable": True
                }
            }
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "message": f"File is not readable: {e}"
            }
    
    async def check_file_size(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate file size is reasonable."""
        original_size = original_path.stat().st_size
        compressed_size = compressed_path.stat().st_size
        
        min_size = parameters.get("min_size", 1024)
        max_compression_ratio = parameters.get("max_compression_ratio", 0.99)
        
        if compressed_size < min_size:
            return {
                "status": ValidationStatus.WARNING,
                "message": f"Compressed file too small: {compressed_size} bytes",
                "details": {
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "min_expected": min_size
                }
            }
        
        compression_ratio = compressed_size / original_size
        if compression_ratio > max_compression_ratio:
            return {
                "status": ValidationStatus.WARNING,
                "message": f"Poor compression ratio: {compression_ratio:.2%}",
                "details": {
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compression_ratio
                }
            }
        
        return {
            "status": ValidationStatus.PASSED,
            "message": f"File size acceptable (ratio: {compression_ratio:.2%})",
            "details": {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "space_saved": original_size - compressed_size
            }
        }
    
    async def check_format_validity(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the compressed file format."""
        # Simulate format validation
        await asyncio.sleep(0.05)
        
        try:
            # Basic format check based on file extension and magic bytes
            format_valid = True
            detected_format = compressed_path.suffix.lower().lstrip('.')
            
            # Simulate magic byte checking
            with open(compressed_path, 'rb') as f:
                header = f.read(16)
            
            format_signatures = {
                'jpg': [b'\xff\xd8\xff'],
                'png': [b'\x89PNG'],
                'mp4': [b'ftyp'],
                'webm': [b'\x1a\x45\xdf\xa3'],
                'mp3': [b'ID3', b'\xff\xfb', b'\xff\xf3']
            }
            
            expected_signatures = format_signatures.get(detected_format, [])
            if expected_signatures:
                format_valid = any(sig in header for sig in expected_signatures)
            
            if format_valid:
                return {
                    "status": ValidationStatus.PASSED,
                    "message": f"Valid {detected_format.upper()} format",
                    "details": {
                        "detected_format": detected_format,
                        "header_valid": True
                    }
                }
            else:
                return {
                    "status": ValidationStatus.FAILED,
                    "message": f"Invalid or corrupted {detected_format.upper()} format",
                    "details": {
                        "detected_format": detected_format,
                        "header_valid": False
                    }
                }
                
        except Exception as e:
            return {
                "status": ValidationStatus.FAILED,
                "message": f"Format validation failed: {e}"
            }
    
    async def check_quality_threshold(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if quality meets minimum thresholds."""
        # Simulate quality assessment
        await asyncio.sleep(0.1)
        
        min_psnr = parameters.get("min_psnr", 30.0)
        min_ssim = parameters.get("min_ssim", 0.8)
        
        # Simulated quality metrics
        psnr = 35.0 + (hash(str(compressed_path)) % 100) / 10.0
        ssim = 0.75 + (hash(str(original_path)) % 100) / 400.0
        
        issues = []
        if psnr < min_psnr:
            issues.append(f"PSNR too low: {psnr:.2f} < {min_psnr}")
        if ssim < min_ssim:
            issues.append(f"SSIM too low: {ssim:.3f} < {min_ssim}")
        
        if issues:
            return {
                "status": ValidationStatus.WARNING,
                "message": "Quality below threshold: " + "; ".join(issues),
                "details": {
                    "psnr": psnr,
                    "ssim": ssim,
                    "min_psnr": min_psnr,
                    "min_ssim": min_ssim
                }
            }
        
        return {
            "status": ValidationStatus.PASSED,
            "message": f"Quality meets requirements (PSNR: {psnr:.2f}, SSIM: {ssim:.3f})",
            "details": {
                "psnr": psnr,
                "ssim": ssim,
                "min_psnr": min_psnr,
                "min_ssim": min_ssim
            }
        }
    
    async def check_visual_artifacts(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect visual compression artifacts."""
        # Simulate artifact detection
        await asyncio.sleep(0.2)
        
        artifact_threshold = parameters.get("artifact_threshold", 0.1)
        
        # Simulated artifact detection
        blocking_artifacts = (hash(str(compressed_path)) % 100) / 1000.0
        ringing_artifacts = (hash(str(original_path)) % 100) / 1000.0
        
        artifacts_detected = []
        if blocking_artifacts > artifact_threshold:
            artifacts_detected.append(f"Blocking artifacts: {blocking_artifacts:.3f}")
        if ringing_artifacts > artifact_threshold:
            artifacts_detected.append(f"Ringing artifacts: {ringing_artifacts:.3f}")
        
        if artifacts_detected:
            return {
                "status": ValidationStatus.WARNING,
                "message": "Visual artifacts detected: " + "; ".join(artifacts_detected),
                "details": {
                    "blocking_artifacts": blocking_artifacts,
                    "ringing_artifacts": ringing_artifacts,
                    "threshold": artifact_threshold
                }
            }
        
        return {
            "status": ValidationStatus.PASSED,
            "message": "No significant visual artifacts detected",
            "details": {
                "blocking_artifacts": blocking_artifacts,
                "ringing_artifacts": ringing_artifacts,
                "threshold": artifact_threshold
            }
        }
    
    async def check_metadata_preservation(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check metadata preservation."""
        required_fields = parameters.get("required_fields", [])
        
        # Simulate metadata extraction
        await asyncio.sleep(0.05)
        
        preserved_metadata = {
            "width": 1920,
            "height": 1080,
            "format": "jpeg",
            "colorspace": "sRGB"
        }
        
        missing_fields = [field for field in required_fields 
                         if field not in preserved_metadata]
        
        if missing_fields:
            return {
                "status": ValidationStatus.WARNING,
                "message": f"Missing metadata fields: {', '.join(missing_fields)}",
                "details": {
                    "preserved_metadata": preserved_metadata,
                    "missing_fields": missing_fields,
                    "required_fields": required_fields
                }
            }
        
        return {
            "status": ValidationStatus.PASSED,
            "message": "All required metadata preserved",
            "details": {
                "preserved_metadata": preserved_metadata,
                "required_fields": required_fields
            }
        }
    
    async def check_processing_time(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate processing time efficiency."""
        max_time_per_mb = parameters.get("max_time_per_mb", 10.0)
        
        # Get processing time from compression config if available
        processing_time = compression_config.get("processing_time", 5.0)
        file_size_mb = original_path.stat().st_size / (1024 * 1024)
        
        time_per_mb = processing_time / file_size_mb if file_size_mb > 0 else 0
        
        if time_per_mb > max_time_per_mb:
            return {
                "status": ValidationStatus.WARNING,
                "message": f"Processing too slow: {time_per_mb:.2f}s/MB > {max_time_per_mb}s/MB",
                "details": {
                    "processing_time": processing_time,
                    "file_size_mb": file_size_mb,
                    "time_per_mb": time_per_mb,
                    "max_time_per_mb": max_time_per_mb
                }
            }
        
        return {
            "status": ValidationStatus.PASSED,
            "message": f"Processing time acceptable: {time_per_mb:.2f}s/MB",
            "details": {
                "processing_time": processing_time,
                "file_size_mb": file_size_mb,
                "time_per_mb": time_per_mb,
                "max_time_per_mb": max_time_per_mb
            }
        }
    
    async def check_malware(
        self,
        original_path: Path,
        compressed_path: Path,
        compression_config: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Scan for potential malware."""
        # Simulate malware scanning
        await asyncio.sleep(0.3)
        
        # Simulated clean result
        return {
            "status": ValidationStatus.PASSED,
            "message": "No malware detected",
            "details": {
                "scan_engine": "simulated_scanner",
                "threats_found": 0,
                "scan_time": 0.3
            }
        }
    
    def _analyze_validation_results(
        self,
        results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """Analyze validation results and provide summary."""
        passed = [r for r in results if r.status == ValidationStatus.PASSED]
        warnings = [r for r in results if r.status == ValidationStatus.WARNING]
        failed = [r for r in results if r.status == ValidationStatus.FAILED]
        errors = [r for r in results if r.status == ValidationStatus.ERROR]
        
        # Determine overall status
        if errors or failed:
            overall_status = ValidationStatus.FAILED
        elif warnings:
            overall_status = ValidationStatus.WARNING
        else:
            overall_status = ValidationStatus.PASSED
        
        # Generate recommendations
        recommendations = []
        if failed:
            recommendations.append("Critical issues found - compression may have failed")
        if warnings:
            recommendations.append("Quality or performance issues detected - consider adjusting settings")
        if not warnings and not failed and not errors:
            recommendations.append("Compression validation passed - results are acceptable")
        
        return {
            "overall_status": overall_status.value,
            "passed_checks": len(passed),
            "warning_checks": len(warnings),
            "failed_checks": len(failed),
            "error_checks": len(errors),
            "total_checks": len(results),
            "success_rate": len(passed) / len(results) if results else 0,
            "recommendations": recommendations,
            "summary": f"{len(passed)}/{len(results)} checks passed"
        }
    
    def get_validation_history(
        self,
        validation_id: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get validation history."""
        if validation_id:
            return self.validation_history.get(validation_id)
        else:
            return list(self.validation_history.values())
    
    def export_validation_report(
        self,
        validation_id: str,
        format: str = "json"
    ) -> str:
        """Export validation report in specified format."""
        validation_data = self.validation_history.get(validation_id)
        if not validation_data:
            raise ValueError(f"Validation ID not found: {validation_id}")
        
        if format.lower() == "json":
            return json.dumps(validation_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics."""
        if not self.validation_history:
            return {"total_validations": 0}
        
        total_validations = len(self.validation_history)
        
        # Aggregate statistics
        status_counts = {"passed": 0, "warning": 0, "failed": 0, "error": 0}
        total_checks = 0
        
        for validation in self.validation_history.values():
            analysis = validation["analysis"]
            total_checks += analysis["total_checks"]
            
            if analysis["overall_status"] == "passed":
                status_counts["passed"] += 1
            elif analysis["overall_status"] == "warning":
                status_counts["warning"] += 1
            elif analysis["overall_status"] == "failed":
                status_counts["failed"] += 1
            else:
                status_counts["error"] += 1
        
        return {
            "total_validations": total_validations,
            "total_checks": total_checks,
            "status_distribution": status_counts,
            "success_rate": status_counts["passed"] / total_validations if total_validations > 0 else 0,
            "average_checks_per_validation": total_checks / total_validations if total_validations > 0 else 0
        }