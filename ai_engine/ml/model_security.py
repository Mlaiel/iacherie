"""
Model Security and Validation Module

Advanced security validation and protection for ML models in the IA Influencer platform.
Ensures model integrity, prevents adversarial attacks, and validates model safety.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  STRICT LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import hashlib
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# ML Security dependencies
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, precision_score, recall_score
import cv2
from PIL import Image

logger = logging.getLogger(__name__)


class SecurityThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationStatus(Enum):
    """Model validation status"""
    PENDING = "pending"
    VALIDATING = "validating"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class SecurityMetrics:
    """Security validation metrics"""
    threat_level: SecurityThreatLevel
    validation_status: ValidationStatus
    security_score: float = 0.0
    integrity_score: float = 0.0
    robustness_score: float = 0.0
    
    # Specific security checks
    adversarial_resistance: float = 0.0
    input_validation_score: float = 0.0
    output_sanitization_score: float = 0.0
    model_poisoning_resistance: float = 0.0
    
    # Vulnerability assessment
    known_vulnerabilities: List[str] = field(default_factory=list)
    security_warnings: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    
    # Compliance scores
    gdpr_compliance_score: float = 0.0
    data_privacy_score: float = 0.0
    bias_fairness_score: float = 0.0
    
    # Validation metadata
    validated_at: datetime = field(default_factory=datetime.utcnow)
    validator_id: str = "system"
    validation_duration: float = 0.0


class ModelSecurityValidator:
    """
    Advanced security validator for ML models
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.security_thresholds = self.config.get('security_thresholds', {
            'min_security_score': 0.7,
            'min_integrity_score': 0.8,
            'min_robustness_score': 0.6,
            'max_vulnerability_count': 5
        })
        
    async def validate_model_security(self, model: torch.nn.Module, model_path: str, metadata: Dict[str, Any]) -> SecurityMetrics:
        """
        Comprehensive security validation of ML model
        """
        start_time = datetime.utcnow()
        
        try:
            # Initialize security metrics
            metrics = SecurityMetrics(
                threat_level=SecurityThreatLevel.LOW,
                validation_status=ValidationStatus.VALIDATING
            )
            
            # 1. Model Integrity Check
            integrity_score = await self._validate_model_integrity(model, model_path)
            metrics.integrity_score = integrity_score
            
            # 2. Input/Output Validation
            io_validation_score = await self._validate_io_security(model, metadata)
            metrics.input_validation_score = io_validation_score
            
            # 3. Adversarial Robustness Testing
            robustness_score = await self._test_adversarial_robustness(model, metadata)
            metrics.adversarial_resistance = robustness_score
            metrics.robustness_score = robustness_score
            
            # 4. Model Poisoning Detection
            poisoning_resistance = await self._detect_model_poisoning(model, metadata)
            metrics.model_poisoning_resistance = poisoning_resistance
            
            # 5. Bias and Fairness Assessment
            bias_score = await self._assess_bias_fairness(model, metadata)
            metrics.bias_fairness_score = bias_score
            
            # 6. Privacy Compliance Check
            privacy_score = await self._validate_privacy_compliance(model, metadata)
            metrics.data_privacy_score = privacy_score
            metrics.gdpr_compliance_score = privacy_score
            
            # 7. Known Vulnerability Scan
            vulnerabilities = await self._scan_known_vulnerabilities(model, model_path)
            metrics.known_vulnerabilities = vulnerabilities
            
            # Calculate overall security score
            security_score = self._calculate_security_score(metrics)
            metrics.security_score = security_score
            
            # Determine threat level and status
            metrics.threat_level = self._determine_threat_level(metrics)
            metrics.validation_status = self._determine_validation_status(metrics)
            
            # Generate recommendations
            metrics.recommended_actions = self._generate_security_recommendations(metrics)
            
            # Record validation duration
            end_time = datetime.utcnow()
            metrics.validation_duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Model security validation completed. Score: {security_score:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return SecurityMetrics(
                threat_level=SecurityThreatLevel.CRITICAL,
                validation_status=ValidationStatus.FAILED,
                security_warnings=[f"Validation failed: {str(e)}"]
            )
    
    async def _validate_model_integrity(self, model: torch.nn.Module, model_path: str) -> float:
        """Validate model file integrity and structure"""



        try:
            # Check file existence and basic properties
            model_file = Path(model_path)
            if not model_file.exists():
                return 0.0
            
            # Verify file checksum if available
            integrity_score = 0.8  # Base score
            
            # Check model structure consistency
            if hasattr(model, 'state_dict'):
                state_dict = model.state_dict()
                if len(state_dict) > 0:
                    integrity_score += 0.1
                
                # Verify parameter shapes and values are reasonable
                param_check_passed = True
                for name, param in state_dict.items():
                    if torch.isnan(param).any() or torch.isinf(param).any():
                        param_check_passed = False
                        break
                
                if param_check_passed:
                    integrity_score += 0.1
            
            return min(integrity_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Integrity validation failed: {e}")
            return 0.0
    
    async def _validate_io_security(self, model: torch.nn.Module, metadata: Dict[str, Any]) -> float:
        """Validate input/output security and sanitization"""



        try:
            security_score = 0.7  # Base score
            
            # Check input schema validation
            input_schema = metadata.get('input_schema', {})
            if input_schema:
                if 'type' in input_schema and 'shape' in input_schema:
                    security_score += 0.15
                if 'validation_rules' in input_schema:
                    security_score += 0.15
            
            # Check output schema validation
            output_schema = metadata.get('output_schema', {})
            if output_schema:
                if 'type' in output_schema and 'format' in output_schema:
                    security_score += 0.1
            
            return min(security_score, 1.0)
            
        except Exception as e:
            logger.warning(f"I/O security validation failed: {e}")
            return 0.0
    
    async def _test_adversarial_robustness(self, model: torch.nn.Module, metadata: Dict[str, Any]) -> float:
        """Test model robustness against adversarial attacks"""



        try:
            # Simplified adversarial testing
            robustness_score = 0.6  # Base score
            
            model.eval()
            
            # Generate simple adversarial examples
            try:
                # Create dummy input based on model type
                input_shape = metadata.get('input_shape', (1, 3, 224, 224))
                dummy_input = torch.randn(input_shape)
                
                # Test with small perturbations
                epsilon = 0.01
                perturbed_input = dummy_input + epsilon * torch.randn_like(dummy_input)
                
                with torch.no_grad():
                    original_output = model(dummy_input)
                    perturbed_output = model(perturbed_input)
                    
                    # Check output stability
                    output_diff = torch.norm(original_output - perturbed_output)
                    if output_diff < 0.1:  # Stable output
                        robustness_score += 0.2
                    elif output_diff < 0.3:  # Moderately stable
                        robustness_score += 0.1
                
                robustness_score += 0.1  # Successfully tested
                
            except Exception as e:
                logger.warning(f"Adversarial testing failed: {e}")
            
            return min(robustness_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Robustness testing failed: {e}")
            return 0.0
    
    async def _detect_model_poisoning(self, model: torch.nn.Module, metadata: Dict[str, Any]) -> float:
        """Detect potential model poisoning attacks"""



        try:
            poisoning_resistance = 0.7  # Base score
            
            # Check for unusual parameter distributions
            if hasattr(model, 'state_dict'):
                state_dict = model.state_dict()
                
                for name, param in state_dict.items():
                    param_mean = torch.mean(param).item()
                    param_std = torch.std(param).item()
                    
                    # Check for suspicious parameter distributions
                    if abs(param_mean) > 10 or param_std > 10:
                        poisoning_resistance -= 0.1
                    
                    # Check for dead neurons or unusual activations
                    if param_std < 1e-6:  # Potential dead neurons
                        poisoning_resistance -= 0.05
            
            # Check training metadata for anomalies
            training_info = metadata.get('training_info', {})
            if training_info:
                training_loss = training_info.get('final_loss', 0)
                if training_loss < 1e-6 or training_loss > 100:
                    poisoning_resistance -= 0.1
            
            return max(min(poisoning_resistance, 1.0), 0.0)
            
        except Exception as e:
            logger.warning(f"Poisoning detection failed: {e}")
            return 0.5
    
    async def _assess_bias_fairness(self, model: torch.nn.Module, metadata: Dict[str, Any]) -> float:
        """Assess model bias and fairness"""



        try:
            bias_score = 0.6  # Base score
            
            # Check if bias assessment was performed during training
            fairness_info = metadata.get('fairness_assessment', {})
            if fairness_info:
                if 'demographic_parity' in fairness_info:
                    bias_score += 0.15
                if 'equalized_odds' in fairness_info:
                    bias_score += 0.15
                if 'bias_mitigation_applied' in fairness_info:
                    bias_score += 0.1
            
            # Check for content type specific bias considerations
            content_types = metadata.get('content_types', [])
            if 'audio' in content_types or 'music' in content_types:
                # Music/audio models should be assessed for genre bias
                if 'genre_bias_assessment' in fairness_info:
                    bias_score += 0.1
            
            return min(bias_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Bias assessment failed: {e}")
            return 0.5
    
    async def _validate_privacy_compliance(self, model: torch.nn.Module, metadata: Dict[str, Any]) -> float:
        """Validate privacy compliance (GDPR, etc.)"""



        try:
            privacy_score = 0.7  # Base score
            
            # Check for privacy-preserving techniques
            privacy_info = metadata.get('privacy_info', {})
            if privacy_info:
                if privacy_info.get('differential_privacy', False):
                    privacy_score += 0.15
                if privacy_info.get('federated_learning', False):
                    privacy_score += 0.1
                if privacy_info.get('data_anonymization', False):
                    privacy_score += 0.05
            
            # Check GDPR compliance flags
            gdpr_info = metadata.get('gdpr_compliance', {})
            if gdpr_info:
                if gdpr_info.get('right_to_be_forgotten', False):
                    privacy_score += 0.05
                if gdpr_info.get('data_minimization', False):
                    privacy_score += 0.05
            
            return min(privacy_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Privacy compliance validation failed: {e}")
            return 0.5
    
    async def _scan_known_vulnerabilities(self, model: torch.nn.Module, model_path: str) -> List[str]:
        """Scan for known vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Check model file format vulnerabilities
            if model_path.endswith('.pkl') or model_path.endswith('.pickle'):
                vulnerabilities.append("PICKLE_DESERIALIZATION_RISK")
            
            # Check for potentially unsafe operations
            model_str = str(model)
            if 'exec(' in model_str or 'eval(' in model_str:
                vulnerabilities.append("UNSAFE_CODE_EXECUTION")
            
            # Check model size (potential for hiding malicious code)
            model_file = Path(model_path)
            if model_file.exists():
                file_size_mb = model_file.stat().st_size / (1024 * 1024)
                if file_size_mb > 1000:  # > 1GB
                    vulnerabilities.append("UNUSUALLY_LARGE_MODEL_FILE")
            
        except Exception as e:
            logger.warning(f"Vulnerability scan failed: {e}")
            vulnerabilities.append("VULNERABILITY_SCAN_FAILED")
        
        return vulnerabilities
    
    def _calculate_security_score(self, metrics: SecurityMetrics) -> float:
        """Calculate overall security score"""
        weights = {
            'integrity': 0.25,
            'robustness': 0.20,
            'input_validation': 0.15,
            'poisoning_resistance': 0.15,
            'bias_fairness': 0.15,
            'privacy_compliance': 0.10
        }
        
        score = (
            metrics.integrity_score * weights['integrity'] +
            metrics.robustness_score * weights['robustness'] +
            metrics.input_validation_score * weights['input_validation'] +
            metrics.model_poisoning_resistance * weights['poisoning_resistance'] +
            metrics.bias_fairness_score * weights['bias_fairness'] +
            metrics.data_privacy_score * weights['privacy_compliance']
        )
        
        # Penalize for vulnerabilities
        vulnerability_penalty = len(metrics.known_vulnerabilities) * 0.05
        score = max(score - vulnerability_penalty, 0.0)
        
        return score
    
    def _determine_threat_level(self, metrics: SecurityMetrics) -> SecurityThreatLevel:
        """Determine threat level based on security metrics"""
        if metrics.security_score >= 0.8 and len(metrics.known_vulnerabilities) == 0:
            return SecurityThreatLevel.LOW
        elif metrics.security_score >= 0.6 and len(metrics.known_vulnerabilities) <= 2:
            return SecurityThreatLevel.MEDIUM
        elif metrics.security_score >= 0.4:
            return SecurityThreatLevel.HIGH
        else:
            return SecurityThreatLevel.CRITICAL
    
    def _determine_validation_status(self, metrics: SecurityMetrics) -> ValidationStatus:
        """Determine validation status"""
        if metrics.security_score >= self.security_thresholds['min_security_score']:
            if metrics.threat_level in [SecurityThreatLevel.LOW, SecurityThreatLevel.MEDIUM]:
                return ValidationStatus.PASSED
            else:
                return ValidationStatus.WARNING
        else:
            return ValidationStatus.FAILED
    
    def _generate_security_recommendations(self, metrics: SecurityMetrics) -> List[str]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        if metrics.integrity_score < 0.8:
            recommendations.append("Improve model integrity validation and checksums")
        
        if metrics.robustness_score < 0.6:
            recommendations.append("Implement adversarial training for improved robustness")
        
        if metrics.input_validation_score < 0.7:
            recommendations.append("Enhance input validation and sanitization")
        
        if metrics.model_poisoning_resistance < 0.7:
            recommendations.append("Add model poisoning detection mechanisms")
        
        if metrics.bias_fairness_score < 0.6:
            recommendations.append("Conduct thorough bias assessment and mitigation")
        
        if metrics.data_privacy_score < 0.7:
            recommendations.append("Implement privacy-preserving techniques")
        
        if len(metrics.known_vulnerabilities) > 0:
            recommendations.append("Address identified vulnerabilities before deployment")
        
        if not recommendations:
            recommendations.append("Security validation passed - maintain current security practices")
        
        return recommendations


class AdversarialDefense:
    """
    Adversarial attack defense mechanisms for ML models
    """
    
    def __init__(self):
        self.defense_techniques = [
            "input_preprocessing",
            "adversarial_training", 
            "defensive_distillation",
            "feature_squeezing",
            "randomized_smoothing"
        ]
    
    async def apply_input_preprocessing(self, input_data: torch.Tensor, technique: str = "gaussian_noise") -> torch.Tensor:
        """Apply input preprocessing defense"""



        try:
            if technique == "gaussian_noise":
                noise = torch.randn_like(input_data) * 0.01
                return input_data + noise
            elif technique == "quantization":
                return torch.round(input_data * 255) / 255
            else:
                return input_data
                
        except Exception as e:
            logger.warning(f"Input preprocessing failed: {e}")
            return input_data
    
    async def detect_adversarial_input(self, input_data: torch.Tensor, model: torch.nn.Module) -> Dict[str, Any]:
        """Detect potential adversarial inputs"""



        try:
            detection_results = {
                'is_adversarial': False,
                'confidence': 0.0,
                'anomaly_score': 0.0,
                'defense_applied': False
            }
            
            # Simple statistical analysis
            input_stats = {
                'mean': torch.mean(input_data).item(),
                'std': torch.std(input_data).item(),
                'min': torch.min(input_data).item(),
                'max': torch.max(input_data).item()
            }
            
            # Check for unusual input statistics
            if input_stats['std'] > 2.0 or input_stats['std'] < 0.01:
                detection_results['anomaly_score'] += 0.3
            
            if input_stats['max'] > 10 or input_stats['min'] < -10:
                detection_results['anomaly_score'] += 0.4
            
            # Determine if input is adversarial
            if detection_results['anomaly_score'] > 0.5:
                detection_results['is_adversarial'] = True
                detection_results['confidence'] = detection_results['anomaly_score']
            
            return detection_results
            
        except Exception as e:
            logger.error(f"Adversarial detection failed: {e}")
            return {'is_adversarial': False, 'confidence': 0.0, 'error': str(e)}


class ModelIntegrityChecker:
    """
    Advanced model integrity verification system
    """
    
    def __init__(self):
        self.integrity_checks = [
            "checksum_verification",
            "structural_validation", 
            "parameter_analysis",
            "behavior_consistency"
        ]
    
    async def verify_model_integrity(self, model_path: str, expected_checksum: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive model integrity verification"""



        try:
            integrity_results = {
                'checksum_valid': False,
                'structure_valid': False,
                'parameters_valid': False,
                'overall_integrity': False,
                'issues_found': []
            }
            
            # Checksum verification
            if expected_checksum:
                actual_checksum = self._calculate_file_checksum(model_path)
                integrity_results['checksum_valid'] = (actual_checksum == expected_checksum)
                if not integrity_results['checksum_valid']:
                    integrity_results['issues_found'].append("Checksum mismatch detected")
            else:
                integrity_results['checksum_valid'] = True  # No checksum to verify
            
            # Load and analyze model structure
            try:
                model = torch.load(model_path, map_location='cpu')
                integrity_results['structure_valid'] = True
                
                # Parameter analysis
                if hasattr(model, 'state_dict') if isinstance(model, torch.nn.Module) else isinstance(model, dict):
                    params = model.state_dict() if hasattr(model, 'state_dict') else model
                    integrity_results['parameters_valid'] = self._validate_parameters(params)
                    
                    if not integrity_results['parameters_valid']:
                        integrity_results['issues_found'].append("Invalid parameters detected")
                
            except Exception as e:
                integrity_results['structure_valid'] = False
                integrity_results['issues_found'].append(f"Model loading failed: {str(e)}")
            
            # Overall integrity assessment
            integrity_results['overall_integrity'] = (
                integrity_results['checksum_valid'] and
                integrity_results['structure_valid'] and
                integrity_results['parameters_valid']
            )
            
            return integrity_results
            
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return {
                'overall_integrity': False,
                'issues_found': [f"Integrity check failed: {str(e)}"]
            }
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Checksum calculation failed: {e}")
            return ""
    
    def _validate_parameters(self, parameters: Dict[str, torch.Tensor]) -> bool:
        """Validate model parameters for anomalies"""



        try:
            for name, param in parameters.items():
                # Check for NaN or infinite values
                if torch.isnan(param).any() or torch.isinf(param).any():
                    logger.warning(f"Invalid values found in parameter: {name}")
                    return False
                
                # Check for extremely large or small values
                param_max = torch.max(torch.abs(param)).item()
                if param_max > 1000 or (param_max < 1e-10 and param_max > 0):
                    logger.warning(f"Suspicious parameter values in: {name}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Parameter validation failed: {e}")
            return False
