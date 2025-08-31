"""🎯 Quality Gates - Automated Quality Gate System

Professional quality gate system for automated quality control checkpoints.
Implements configurable quality gates with pass/fail criteria and automated
decision making for audio content approval workflows.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np

from .standards import QualityProfile
from .metrics import QualityReport, QualityMetrics
from .validator import ValidationResult

logger = logging.getLogger(__name__)


class GateType(Enum):
    """Quality gate types"""    THRESHOLD = "threshold"       # Simple threshold check
    RANGE = "range"              # Value within range
    COMPARISON = "comparison"    # Compare multiple values
    COMPOSITE = "composite"      # Multiple criteria
    CUSTOM = "custom"            # Custom logic


class GateSeverity(Enum):
    """Gate failure severity levels"""    INFO = "info"               # Informational only
    WARNING = "warning"         # Warning but can pass
    ERROR = "error"            # Error, blocks progression
    CRITICAL = "critical"       # Critical failure


@dataclass
class QualityGateResult:
    """Quality gate evaluation result"""    gate_name: str
    gate_type: GateType
    passed: bool
    score: Optional[float] = None
    threshold: Optional[float] = None
    actual_value: Optional[float] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    severity: GateSeverity = GateSeverity.ERROR
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0


class QualityGate(ABC):
    """    🎯 Abstract Quality Gate Base Class
    
    Base class for all quality gates:
    - Configurable pass/fail criteria
    - Detailed evaluation results
    - Performance monitoring
    - Extensible design
    """    
    def __init__(
        self,
        name: str,
        gate_type: GateType = GateType.THRESHOLD,
        severity: GateSeverity = GateSeverity.ERROR,
        enabled: bool = True,
        description: str = ""
    ):
        self.name = name
        self.gate_type = gate_type
        self.severity = severity
        self.enabled = enabled
        self.description = description
        self.evaluation_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.total_processing_time = 0.0
    
    @abstractmethod
    async def evaluate(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_report: QualityReport,
        quality_profile: QualityProfile
    ) -> QualityGateResult:
        """Evaluate quality gate against audio data"""        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get gate evaluation statistics"""        return {
            'name': self.name,
            'type': self.gate_type.value,
            'enabled': self.enabled,
            'total_evaluations': self.evaluation_count,
            'passed': self.pass_count,
            'failed': self.fail_count,
            'pass_rate': self.pass_count / max(self.evaluation_count, 1),
            'average_processing_time': self.total_processing_time / max(self.evaluation_count, 1)
        }
    
    def reset_statistics(self):
        """Reset gate statistics"""        self.evaluation_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.total_processing_time = 0.0
    
    def _update_statistics(self, result: QualityGateResult):
        """Update gate statistics"""        self.evaluation_count += 1
        if result.passed:
            self.pass_count += 1
        else:
            self.fail_count += 1
        self.total_processing_time += result.processing_time


class ThresholdGate(QualityGate):
    """Simple threshold-based quality gate"""    
    def __init__(
        self,
        name: str,
        parameter: str,
        threshold: float,
        operator: str = ">=",
        severity: GateSeverity = GateSeverity.ERROR,
        description: str = ""
    ):
        super().__init__(name, GateType.THRESHOLD, severity, True, description)
        self.parameter = parameter
        self.threshold = threshold
        self.operator = operator
        
        # Validate operator
        if operator not in [">=", "<=", ">", "<", "==", "!="]:
            raise ValueError(f"Invalid operator: {operator}")
    
    async def evaluate(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_report: QualityReport,
        quality_profile: QualityProfile
    ) -> QualityGateResult:
        start_time = datetime.now()
        
        try:
            # Get parameter value from quality report
            actual_value = self._extract_parameter_value(quality_report, self.parameter)
            
            if actual_value is None:
                result = QualityGateResult(
                    gate_name=self.name,
                    gate_type=self.gate_type,
                    passed=False,
                    message=f"Parameter '{self.parameter}' not found in quality report",
                    severity=GateSeverity.ERROR
                )
            else:
                # Evaluate threshold
                passed = self._evaluate_threshold(actual_value, self.threshold, self.operator)
                
                result = QualityGateResult(
                    gate_name=self.name,
                    gate_type=self.gate_type,
                    passed=passed,
                    threshold=self.threshold,
                    actual_value=actual_value,
                    message=f"{self.parameter} {actual_value} {self.operator} {self.threshold}: {'PASS' if passed else 'FAIL'}",
                    severity=self.severity if not passed else GateSeverity.INFO,
                    recommendations=self._get_recommendations(passed, actual_value, self.threshold)
                )
            
        except Exception as e:
            logger.error(f"Threshold gate {self.name} evaluation failed: {e}")
            result = QualityGateResult(
                gate_name=self.name,
                gate_type=self.gate_type,
                passed=False,
                message=f"Evaluation error: {str(e)}",
                severity=GateSeverity.ERROR
            )
        
        # Update timing and statistics
        result.processing_time = (datetime.now() - start_time).total_seconds()
        self._update_statistics(result)
        
        return result
    
    def _extract_parameter_value(self, quality_report: QualityReport, parameter: str) -> Optional[float]:
        """Extract parameter value from quality report"""        
        # Check metrics first
        for score in quality_report.metrics.scores:
            if score.name == parameter:
                return score.value
        
        # Check validation results
        for validation in quality_report.validation_results:
            if hasattr(validation, 'test_name') and validation.test_name == parameter:
                if hasattr(validation, 'actual_value'):
                    return validation.actual_value
                elif hasattr(validation, 'score'):
                    return validation.score
        
        # Check audio properties
        if parameter in quality_report.audio_properties:
            return quality_report.audio_properties[parameter]
        
        # Check processing details
        if parameter in quality_report.processing_details:
            return quality_report.processing_details[parameter]
        
        return None
    
    def _evaluate_threshold(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate threshold condition"""        if operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            return False
    
    def _get_recommendations(self, passed: bool, actual: float, threshold: float) -> List[str]:
        """Get recommendations based on threshold evaluation"""        if passed:
            return []
        
        recommendations = []
        
        if self.parameter == "snr" and actual < threshold:
            recommendations.append("Apply noise reduction to improve signal-to-noise ratio")
        elif self.parameter == "thd" and actual > threshold:
            recommendations.append("Reduce distortion in audio signal")
        elif self.parameter == "clipping_ratio" and actual > threshold:
            recommendations.append("Reduce input levels to prevent clipping")
        elif self.parameter == "dynamic_range" and actual < threshold:
            recommendations.append("Reduce compression to increase dynamic range")
        else:
            recommendations.append(f"Adjust {self.parameter} to meet threshold requirements")
        
        return recommendations


class RangeGate(QualityGate):
    """Range-based quality gate"""    
    def __init__(
        self,
        name: str,
        parameter: str,
        min_value: float,
        max_value: float,
        severity: GateSeverity = GateSeverity.ERROR,
        description: str = ""
    ):
        super().__init__(name, GateType.RANGE, severity, True, description)
        self.parameter = parameter
        self.min_value = min_value
        self.max_value = max_value
        
        if min_value > max_value:
            raise ValueError(f"min_value ({min_value}) cannot be greater than max_value ({max_value})")
    
    async def evaluate(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_report: QualityReport,
        quality_profile: QualityProfile
    ) -> QualityGateResult:
        start_time = datetime.now()
        
        try:
            # Extract parameter value
            actual_value = self._extract_parameter_value(quality_report, self.parameter)
            
            if actual_value is None:
                result = QualityGateResult(
                    gate_name=self.name,
                    gate_type=self.gate_type,
                    passed=False,
                    message=f"Parameter '{self.parameter}' not found",
                    severity=GateSeverity.ERROR
                )
            else:
                # Check if value is within range
                passed = self.min_value <= actual_value <= self.max_value
                
                result = QualityGateResult(
                    gate_name=self.name,
                    gate_type=self.gate_type,
                    passed=passed,
                    actual_value=actual_value,
                    message=f"{self.parameter} {actual_value} in range [{self.min_value}, {self.max_value}]: {'PASS' if passed else 'FAIL'}",
                    severity=self.severity if not passed else GateSeverity.INFO,
                    details={
                        'min_value': self.min_value,
                        'max_value': self.max_value,
                        'range_size': self.max_value - self.min_value
                    },
                    recommendations=self._get_range_recommendations(passed, actual_value)
                )
            
        except Exception as e:
            logger.error(f"Range gate {self.name} evaluation failed: {e}")
            result = QualityGateResult(
                gate_name=self.name,
                gate_type=self.gate_type,
                passed=False,
                message=f"Evaluation error: {str(e)}",
                severity=GateSeverity.ERROR
            )
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        self._update_statistics(result)
        
        return result
    
    def _extract_parameter_value(self, quality_report: QualityReport, parameter: str) -> Optional[float]:
        """Extract parameter value from quality report"""        # Same logic as ThresholdGate
        for score in quality_report.metrics.scores:
            if score.name == parameter:
                return score.value
        
        for validation in quality_report.validation_results:
            if hasattr(validation, 'test_name') and validation.test_name == parameter:
                if hasattr(validation, 'actual_value'):
                    return validation.actual_value
                elif hasattr(validation, 'score'):
                    return validation.score
        
        if parameter in quality_report.audio_properties:
            return quality_report.audio_properties[parameter]
        
        if parameter in quality_report.processing_details:
            return quality_report.processing_details[parameter]
        
        return None
    
    def _get_range_recommendations(self, passed: bool, actual: float) -> List[str]:
        """Get recommendations for range violations"""        if passed:
            return []
        
        recommendations = []
        
        if actual < self.min_value:
            recommendations.append(f"Increase {self.parameter} to at least {self.min_value}")
        elif actual > self.max_value:
            recommendations.append(f"Decrease {self.parameter} to at most {self.max_value}")
        
        # Parameter-specific recommendations
        if self.parameter == "loudness":
            if actual < self.min_value:
                recommendations.append("Increase overall audio level")
            else:
                recommendations.append("Reduce overall audio level")
        elif self.parameter == "duration":
            if actual < self.min_value:
                recommendations.append("Content is too short")
            else:
                recommendations.append("Content is too long, consider editing")
        
        return recommendations


class CompositeGate(QualityGate):
    """Composite quality gate with multiple criteria"""    
    def __init__(
        self,
        name: str,
        criteria: List[Dict[str, Any]],
        logic: str = "AND",  # "AND" or "OR"
        severity: GateSeverity = GateSeverity.ERROR,
        description: str = ""
    ):
        super().__init__(name, GateType.COMPOSITE, severity, True, description)
        self.criteria = criteria
        self.logic = logic.upper()
        
        if self.logic not in ["AND", "OR"]:
            raise ValueError(f"Invalid logic: {logic}. Must be 'AND' or 'OR'")
    
    async def evaluate(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_report: QualityReport,
        quality_profile: QualityProfile
    ) -> QualityGateResult:
        start_time = datetime.now()
        
        try:
            # Evaluate each criterion
            criterion_results = []
            
            for criterion in self.criteria:
                result = await self._evaluate_criterion(criterion, quality_report)
                criterion_results.append(result)
            
            # Apply logic
            if self.logic == "AND":
                passed = all(r['passed'] for r in criterion_results)
            else:  # OR
                passed = any(r['passed'] for r in criterion_results)
            
            # Calculate composite score
            scores = [r['score'] for r in criterion_results if r['score'] is not None]
            composite_score = sum(scores) / len(scores) if scores else None
            
            # Generate message
            passed_count = sum(1 for r in criterion_results if r['passed'])
            total_count = len(criterion_results)
            
            result = QualityGateResult(
                gate_name=self.name,
                gate_type=self.gate_type,
                passed=passed,
                score=composite_score,
                message=f"Composite gate: {passed_count}/{total_count} criteria passed ({'AND' if self.logic == 'AND' else 'OR'} logic): {'PASS' if passed else 'FAIL'}",
                severity=self.severity if not passed else GateSeverity.INFO,
                details={
                    'criteria_results': criterion_results,
                    'logic': self.logic,
                    'passed_count': passed_count,
                    'total_count': total_count
                },
                recommendations=self._get_composite_recommendations(criterion_results, passed)
            )
            
        except Exception as e:
            logger.error(f"Composite gate {self.name} evaluation failed: {e}")
            result = QualityGateResult(
                gate_name=self.name,
                gate_type=self.gate_type,
                passed=False,
                message=f"Evaluation error: {str(e)}",
                severity=GateSeverity.ERROR
            )
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        self._update_statistics(result)
        
        return result
    
    async def _evaluate_criterion(
        self,
        criterion: Dict[str, Any],
        quality_report: QualityReport
    ) -> Dict[str, Any]:
        """Evaluate individual criterion"""        
        parameter = criterion.get('parameter')
        operator = criterion.get('operator', '>=')
        threshold = criterion.get('threshold')
        
        # Extract value
        value = None
        for score in quality_report.metrics.scores:
            if score.name == parameter:
                value = score.value
                break
        
        if value is None:
            return {
                'parameter': parameter,
                'passed': False,
                'score': 0.0,
                'message': f"Parameter '{parameter}' not found"
            }
        
        # Evaluate
        if operator == ">=":
            passed = value >= threshold
        elif operator == "<=":
            passed = value <= threshold
        elif operator == ">":
            passed = value > threshold
        elif operator == "<":
            passed = value < threshold
        elif operator == "==":
            passed = value == threshold
        elif operator == "!=":
            passed = value != threshold
        else:
            passed = False
        
        # Calculate score
        if operator in [">=", ">"]:
            score = min(1.0, value / max(threshold, 0.001))
        elif operator in ["<=", "<"]:
            score = min(1.0, threshold / max(value, 0.001))
        else:
            score = 1.0 if passed else 0.0
        
        return {
            'parameter': parameter,
            'value': value,
            'threshold': threshold,
            'operator': operator,
            'passed': passed,
            'score': score,
            'message': f"{parameter} {value} {operator} {threshold}: {'PASS' if passed else 'FAIL'}"
        }
    
    def _get_composite_recommendations(
        self,
        criterion_results: List[Dict[str, Any]],
        overall_passed: bool
    ) -> List[str]:
        """Get recommendations for composite gate"""        if overall_passed:
            return []
        
        recommendations = []
        
        failed_criteria = [r for r in criterion_results if not r['passed']]
        
        if self.logic == "AND":
            recommendations.append("All criteria must pass:")
            for criterion in failed_criteria:
                recommendations.append(f"- Fix {criterion['parameter']} (current: {criterion.get('value', 'unknown')})")
        else:  # OR
            recommendations.append("At least one criterion must pass:")
            recommendations.append(f"Consider fixing any of: {', '.join([c['parameter'] for c in failed_criteria])}")
        
        return recommendations


# Predefined Quality Gates

class MinimumQualityGate(ThresholdGate):
    """Minimum overall quality gate"""    
    def __init__(self, name: str = "minimum_quality", threshold: float = 0.6):
        super().__init__(
            name=name,
            parameter="overall_score",
            threshold=threshold,
            operator=">=",
            severity=GateSeverity.ERROR,
            description="Ensures minimum overall quality score"
        )


class NoiseGate(ThresholdGate):
    """Signal-to-noise ratio gate"""    
    def __init__(self, name: str = "noise_gate", min_snr: float = 40.0):
        super().__init__(
            name=name,
            parameter="snr",
            threshold=min_snr,
            operator=">=",
            severity=GateSeverity.WARNING,
            description="Ensures adequate signal-to-noise ratio"
        )


class DistortionGate(ThresholdGate):
    """Total harmonic distortion gate"""    
    def __init__(self, name: str = "distortion_gate", max_thd: float = 5.0):
        super().__init__(
            name=name,
            parameter="thd",
            threshold=max_thd,
            operator="<=",
            severity=GateSeverity.ERROR,
            description="Prevents excessive harmonic distortion"
        )


class DynamicRangeGate(ThresholdGate):
    """Dynamic range gate"""    
    def __init__(self, name: str = "dynamic_range_gate", min_range: float = 20.0):
        super().__init__(
            name=name,
            parameter="dynamic_range",
            threshold=min_range,
            operator=">=",
            severity=GateSeverity.WARNING,
            description="Ensures adequate dynamic range"
        )


class FrequencyResponseGate(RangeGate):
    """Frequency response balance gate"""    
    def __init__(self, name: str = "frequency_response_gate"):
        super().__init__(
            name=name,
            parameter="frequency_balance",
            min_value=0.6,
            max_value=1.0,
            severity=GateSeverity.WARNING,
            description="Ensures balanced frequency response"
        )


class ClippingGate(ThresholdGate):
    """Audio clipping prevention gate"""    
    def __init__(self, name: str = "clipping_gate", max_clipping: float = 0.005):
        super().__init__(
            name=name,
            parameter="clipping_ratio",
            threshold=max_clipping,
            operator="<=",
            severity=GateSeverity.CRITICAL,
            description="Prevents audio clipping distortion"
        )


class LoudnessGate(RangeGate):
    """Loudness compliance gate"""    
    def __init__(self, name: str = "loudness_gate", target_lufs: float = -14.0, tolerance: float = 2.0):
        super().__init__(
            name=name,
            parameter="loudness",
            min_value=target_lufs - tolerance,
            max_value=target_lufs + tolerance,
            severity=GateSeverity.WARNING,
            description="Ensures appropriate loudness levels"
        )


class DurationGate(RangeGate):
    """Content duration gate"""    
    def __init__(self, name: str = "duration_gate", min_duration: float = 5.0, max_duration: float = 600.0):
        super().__init__(
            name=name,
            parameter="duration",
            min_value=min_duration,
            max_value=max_duration,
            severity=GateSeverity.WARNING,
            description="Validates content duration requirements"
        )


class CustomGate(QualityGate):
    """Custom quality gate with user-defined evaluation function"""    
    def __init__(
        self,
        name: str,
        evaluation_function: Callable,
        severity: GateSeverity = GateSeverity.ERROR,
        description: str = ""
    ):
        super().__init__(name, GateType.CUSTOM, severity, True, description)
        self.evaluation_function = evaluation_function
    
    async def evaluate(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_report: QualityReport,
        quality_profile: QualityProfile
    ) -> QualityGateResult:
        start_time = datetime.now()
        
        try:
            # Call custom evaluation function
            result = await self.evaluation_function(audio_data, sample_rate, quality_report, quality_profile)
            
            # Ensure result is QualityGateResult
            if not isinstance(result, QualityGateResult):
                result = QualityGateResult(
                    gate_name=self.name,
                    gate_type=self.gate_type,
                    passed=bool(result),
                    message=f"Custom gate result: {result}",
                    severity=self.severity
                )
            
        except Exception as e:
            logger.error(f"Custom gate {self.name} evaluation failed: {e}")
            result = QualityGateResult(
                gate_name=self.name,
                gate_type=self.gate_type,
                passed=False,
                message=f"Custom evaluation error: {str(e)}",
                severity=GateSeverity.ERROR
            )
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        self._update_statistics(result)
        
        return result


class QualityGateManager:
    """    🎯 Quality Gate Manager
    
    Manages collection of quality gates:
    - Gate registration and configuration
    - Batch gate evaluation
    - Gate performance monitoring
    - Gate result aggregation
    """    
    def __init__(self):
        self.gates: Dict[str, QualityGate] = {}
        self.gate_groups: Dict[str, List[str]] = {}
        self.evaluation_history = []
        
        logger.info("QualityGateManager initialized")
    
    def add_gate(self, gate: QualityGate):
        """Add quality gate"""        self.gates[gate.name] = gate
        logger.info(f"Added quality gate: {gate.name}")
    
    def remove_gate(self, gate_name: str):
        """Remove quality gate"""        if gate_name in self.gates:
            del self.gates[gate_name]
            logger.info(f"Removed quality gate: {gate_name}")
        else:
            logger.warning(f"Gate not found: {gate_name}")
    
    def create_gate_group(self, group_name: str, gate_names: List[str]):
        """Create named group of gates"""        valid_gates = [name for name in gate_names if name in self.gates]
        self.gate_groups[group_name] = valid_gates
        logger.info(f"Created gate group '{group_name}' with {len(valid_gates)} gates")
    
    async def evaluate_gates(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_report: QualityReport,
        quality_profile: QualityProfile,
        gate_names: Optional[List[str]] = None,
        group_name: Optional[str] = None
    ) -> List[QualityGateResult]:
        """Evaluate specified gates or gate group"""        
        # Determine gates to evaluate
        if group_name:
            gates_to_evaluate = self.gate_groups.get(group_name, [])
        elif gate_names:
            gates_to_evaluate = [name for name in gate_names if name in self.gates]
        else:
            gates_to_evaluate = list(self.gates.keys())
        
        # Filter enabled gates
        gates_to_evaluate = [name for name in gates_to_evaluate if self.gates[name].enabled]
        
        # Evaluate gates
        results = []
        for gate_name in gates_to_evaluate:
            try:
                gate = self.gates[gate_name]
                result = await gate.evaluate(audio_data, sample_rate, quality_report, quality_profile)
                results.append(result)
            except Exception as e:
                logger.error(f"Gate evaluation failed for {gate_name}: {e}")
                results.append(QualityGateResult(
                    gate_name=gate_name,
                    gate_type=GateType.CUSTOM,
                    passed=False,
                    message=f"Evaluation failed: {str(e)}",
                    severity=GateSeverity.ERROR
                ))
        
        # Store evaluation history
        self.evaluation_history.append({
            'timestamp': datetime.now(),
            'gates_evaluated': len(results),
            'gates_passed': len([r for r in results if r.passed]),
            'results': results
        })
        
        return results
    
    def get_gate_statistics(self, gate_name: Optional[str] = None) -> Dict[str, Any]:
        """Get gate performance statistics"""        if gate_name:
            if gate_name in self.gates:
                return self.gates[gate_name].get_statistics()
            else:
                return {}
        else:
            return {name: gate.get_statistics() for name, gate in self.gates.items()}
    
    def get_evaluation_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get evaluation summary for specified period"""        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_evaluations = [
            eval_data for eval_data in self.evaluation_history 
            if eval_data['timestamp'] >= cutoff_time
        ]
        
        if not recent_evaluations:
            return {'period': f'{hours} hours', 'no_data': True}
        
        total_evaluations = len(recent_evaluations)
        total_gates_evaluated = sum(eval_data['gates_evaluated'] for eval_data in recent_evaluations)
        total_gates_passed = sum(eval_data['gates_passed'] for eval_data in recent_evaluations)
        
        # Gate-specific statistics
        gate_performance = {}
        for gate_name in self.gates.keys():
            gate_results = []
            for eval_data in recent_evaluations:
                for result in eval_data['results']:
                    if result.gate_name == gate_name:
                        gate_results.append(result)
            
            if gate_results:
                gate_performance[gate_name] = {
                    'evaluations': len(gate_results),
                    'passed': len([r for r in gate_results if r.passed]),
                    'failed': len([r for r in gate_results if not r.passed]),
                    'pass_rate': len([r for r in gate_results if r.passed]) / len(gate_results),
                    'avg_processing_time': sum(r.processing_time for r in gate_results) / len(gate_results)
                }
        
        return {
            'period': f'{hours} hours',
            'total_evaluations': total_evaluations,
            'total_gates_evaluated': total_gates_evaluated,
            'total_gates_passed': total_gates_passed,
            'overall_pass_rate': total_gates_passed / max(total_gates_evaluated, 1),
            'gate_performance': gate_performance
        }
    
    def configure_standard_gates(self, profile: QualityProfile):
        """Configure standard gates based on quality profile"""        
        # Clear existing gates
        self.gates.clear()
        
        # Add standard gates based on profile
        requirements = profile.requirements
        
        # Minimum quality gate
        self.add_gate(MinimumQualityGate("minimum_quality", profile.pass_threshold))
        
        # SNR gate
        if 'min_snr' in requirements:
            self.add_gate(NoiseGate("snr_gate", requirements['min_snr']))
        
        # Distortion gate
        if 'max_thd' in requirements:
            self.add_gate(DistortionGate("thd_gate", requirements['max_thd']))
        
        # Dynamic range gate
        if 'min_dynamic_range' in requirements:
            self.add_gate(DynamicRangeGate("dynamic_range_gate", requirements['min_dynamic_range']))
        
        # Clipping gate
        max_clipping = requirements.get('max_clipping', 0.005)
        self.add_gate(ClippingGate("clipping_gate", max_clipping))
        
        # Duration gate
        if 'min_duration' in requirements and 'max_duration' in requirements:
            self.add_gate(DurationGate(
                "duration_gate",
                requirements['min_duration'],
                requirements['max_duration']
            ))
        
        # Loudness gate (if target specified)
        if 'target_lufs' in requirements:
            tolerance = requirements.get('lufs_tolerance', 2.0)
            self.add_gate(LoudnessGate(
                "loudness_gate",
                requirements['target_lufs'],
                tolerance
            ))
        
        logger.info(f"Configured {len(self.gates)} standard gates for profile: {profile.name}")
    
    def enable_gate(self, gate_name: str, enabled: bool = True):
        """Enable or disable a gate"""        if gate_name in self.gates:
            self.gates[gate_name].enabled = enabled
            logger.info(f"Gate {gate_name} {'enabled' if enabled else 'disabled'}")
    
    def list_gates(self) -> List[str]:
        """List all registered gates"""        return list(self.gates.keys())
    
    def list_enabled_gates(self) -> List[str]:
        """List enabled gates"""        return [name for name, gate in self.gates.items() if gate.enabled]
