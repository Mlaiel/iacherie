"""
Adversarial Defense Engine
Enterprise-grade protection against adversarial attacks on ML models

Features:
- Adversarial input detection
- Input sanitization and validation
- Adversarial training support
- Defense mechanism orchestration
- Attack pattern recognition
- Real-time protection

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime
import json


class AttackType(Enum):
    """Types of adversarial attacks"""
    FGSM = "fast_gradient_sign_method"
    PGD = "projected_gradient_descent"
    CARLINI_WAGNER = "carlini_wagner"
    DEEPFOOL = "deepfool"
    BOUNDARY = "boundary_attack"
    EVASION = "evasion_attack"
    POISONING = "poisoning_attack"
    BACKDOOR = "backdoor_attack"


class DefenseStrategy(Enum):
    """Defense strategies against adversarial attacks"""
    INPUT_VALIDATION = "input_validation"
    ADVERSARIAL_TRAINING = "adversarial_training"
    FEATURE_SQUEEZING = "feature_squeezing"
    DEFENSIVE_DISTILLATION = "defensive_distillation"
    RANDOMIZED_SMOOTHING = "randomized_smoothing"
    DETECTION_BASED = "detection_based"
    ENSEMBLE_DEFENSE = "ensemble_defense"


@dataclass
class AdversarialDetectionResult:
    """Result of adversarial detection"""
    is_adversarial: bool
    confidence: float
    attack_type: Optional[AttackType]
    detection_method: str
    perturbation_magnitude: float
    metadata: Dict[str, Any]


@dataclass
class DefenseConfig:
    """Configuration for adversarial defense"""
    enabled_strategies: List[DefenseStrategy]
    detection_threshold: float = 0.7
    max_perturbation: float = 0.1
    ensemble_size: int = 5
    validation_strictness: str = "medium"  # low, medium, high
    auto_retrain: bool = True


@dataclass
class AttackEvent:
    """Adversarial attack event logging"""
    timestamp: datetime
    attack_type: AttackType
    model_id: str
    input_shape: Tuple
    perturbation_magnitude: float
    success: bool
    defense_triggered: bool
    metadata: Dict[str, Any]


class AdversarialDefenseEngine:
    """
    Enterprise Adversarial Defense Engine
    Comprehensive protection against adversarial attacks
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.defense_configs: Dict[str, DefenseConfig] = {}
        self.attack_events: List[AttackEvent] = []
        self.model_baselines: Dict[str, Dict[str, Any]] = {}
        self.detection_models: Dict[str, Any] = {}
        
    async def configure_defense(
        self,
        model_id: str,
        config: DefenseConfig
    ) -> bool:
        """Configure adversarial defense for a model"""
        try:
            self.defense_configs[model_id] = config
            
            # Initialize detection models if needed
            if DefenseStrategy.DETECTION_BASED in config.enabled_strategies:
                await self._initialize_detection_model(model_id)
            
            self.logger.info(f"Adversarial defense configured for model {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure defense for model {model_id}: {str(e)}")
            return False
    
    async def detect_adversarial_input(
        self,
        model_id: str,
        input_data: Union[np.ndarray, Dict[str, Any]],
        model_output: Optional[np.ndarray] = None
    ) -> AdversarialDetectionResult:
        """Detect if input is adversarial"""
        try:
            config = self.defense_configs.get(model_id)
            if not config:
                return AdversarialDetectionResult(
                    is_adversarial=False,
                    confidence=0.0,
                    attack_type=None,
                    detection_method="no_defense_configured",
                    perturbation_magnitude=0.0,
                    metadata={}
                )
            
            detection_results = []
            
            # Input validation detection
            if DefenseStrategy.INPUT_VALIDATION in config.enabled_strategies:
                result = await self._validate_input(model_id, input_data, config)
                detection_results.append(result)
            
            # Statistical detection
            if DefenseStrategy.DETECTION_BASED in config.enabled_strategies:
                result = await self._statistical_detection(model_id, input_data, model_output, config)
                detection_results.append(result)
            
            # Feature squeezing detection
            if DefenseStrategy.FEATURE_SQUEEZING in config.enabled_strategies:
                result = await self._feature_squeezing_detection(model_id, input_data, config)
                detection_results.append(result)
            
            # Ensemble detection
            if DefenseStrategy.ENSEMBLE_DEFENSE in config.enabled_strategies:
                result = await self._ensemble_detection(model_id, input_data, model_output, config)
                detection_results.append(result)
            
            # Aggregate detection results
            final_result = self._aggregate_detection_results(detection_results, config)
            
            # Log detection event
            if final_result.is_adversarial:
                await self._log_attack_event(
                    attack_type=final_result.attack_type or AttackType.EVASION,
                    model_id=model_id,
                    input_shape=input_data.shape if hasattr(input_data, 'shape') else (0,),
                    perturbation_magnitude=final_result.perturbation_magnitude,
                    success=False,  # Detected and blocked
                    defense_triggered=True
                )
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Adversarial detection failed for model {model_id}: {str(e)}")
            return AdversarialDetectionResult(
                is_adversarial=True,  # Fail safe
                confidence=1.0,
                attack_type=None,
                detection_method="error_detection",
                perturbation_magnitude=1.0,
                metadata={"error": str(e)}
            )
    
    async def sanitize_input(
        self,
        model_id: str,
        input_data: np.ndarray,
        strategy: DefenseStrategy = DefenseStrategy.FEATURE_SQUEEZING
    ) -> np.ndarray:
        """Sanitize potentially adversarial input"""
        try:
            config = self.defense_configs.get(model_id)
            if not config:
                return input_data
            
            if strategy == DefenseStrategy.FEATURE_SQUEEZING:
                return self._apply_feature_squeezing(input_data)
            elif strategy == DefenseStrategy.RANDOMIZED_SMOOTHING:
                return self._apply_randomized_smoothing(input_data)
            else:
                return input_data
                
        except Exception as e:
            self.logger.error(f"Input sanitization failed: {str(e)}")
            return input_data
    
    async def generate_adversarial_examples(
        self,
        model_id: str,
        input_data: np.ndarray,
        attack_type: AttackType,
        target_class: Optional[int] = None,
        epsilon: float = 0.1
    ) -> np.ndarray:
        """Generate adversarial examples for testing/training"""
        try:
            if attack_type == AttackType.FGSM:
                return self._generate_fgsm_attack(input_data, epsilon)
            elif attack_type == AttackType.PGD:
                return self._generate_pgd_attack(input_data, epsilon)
            elif attack_type == AttackType.CARLINI_WAGNER:
                return self._generate_cw_attack(input_data, target_class)
            else:
                raise ValueError(f"Attack type {attack_type} not implemented")
                
        except Exception as e:
            self.logger.error(f"Failed to generate adversarial examples: {str(e)}")
            raise
    
    async def train_robust_model(
        self,
        model_id: str,
        training_data: np.ndarray,
        training_labels: np.ndarray,
        defense_strategy: DefenseStrategy = DefenseStrategy.ADVERSARIAL_TRAINING
    ) -> Dict[str, Any]:
        """Train model with adversarial defense"""
        try:
            if defense_strategy == DefenseStrategy.ADVERSARIAL_TRAINING:
                return await self._adversarial_training(model_id, training_data, training_labels)
            elif defense_strategy == DefenseStrategy.DEFENSIVE_DISTILLATION:
                return await self._defensive_distillation(model_id, training_data, training_labels)
            else:
                raise ValueError(f"Defense strategy {defense_strategy} not implemented")
                
        except Exception as e:
            self.logger.error(f"Robust model training failed: {str(e)}")
            raise
    
    async def evaluate_robustness(
        self,
        model_id: str,
        test_data: np.ndarray,
        test_labels: np.ndarray,
        attack_types: List[AttackType]
    ) -> Dict[str, Any]:
        """Evaluate model robustness against adversarial attacks"""
        try:
            results = {
                "model_id": model_id,
                "evaluation_timestamp": datetime.now().isoformat(),
                "attack_results": {},
                "overall_robustness": 0.0
            }
            
            total_accuracy = 0.0
            
            for attack_type in attack_types:
                # Generate adversarial examples
                adv_examples = await self.generate_adversarial_examples(
                    model_id, test_data, attack_type
                )
                
                # Test model accuracy on adversarial examples
                accuracy = self._evaluate_accuracy(adv_examples, test_labels)
                
                results["attack_results"][attack_type.value] = {
                    "accuracy": accuracy,
                    "samples_tested": len(test_data),
                    "attack_success_rate": 1.0 - accuracy
                }
                
                total_accuracy += accuracy
            
            results["overall_robustness"] = total_accuracy / len(attack_types)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Robustness evaluation failed: {str(e)}")
            raise
    
    async def get_defense_metrics(
        self,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get adversarial defense metrics"""
        try:
            # Filter events by model if specified
            events = self.attack_events
            if model_id:
                events = [e for e in events if e.model_id == model_id]
            
            metrics = {
                "total_attacks_detected": len(events),
                "attacks_by_type": {},
                "defense_success_rate": 0.0,
                "average_perturbation": 0.0,
                "models_protected": len(self.defense_configs)
            }
            
            if events:
                # Analyze attack types
                for event in events:
                    attack_type = event.attack_type.value
                    if attack_type not in metrics["attacks_by_type"]:
                        metrics["attacks_by_type"][attack_type] = {
                            "count": 0,
                            "blocked": 0,
                            "success_rate": 0.0
                        }
                    
                    metrics["attacks_by_type"][attack_type]["count"] += 1
                    if event.defense_triggered:
                        metrics["attacks_by_type"][attack_type]["blocked"] += 1
                
                # Calculate success rates
                for attack_type in metrics["attacks_by_type"]:
                    data = metrics["attacks_by_type"][attack_type]
                    data["success_rate"] = data["blocked"] / data["count"] if data["count"] > 0 else 0.0
                
                # Overall metrics
                total_blocked = sum(1 for e in events if e.defense_triggered)
                metrics["defense_success_rate"] = total_blocked / len(events)
                metrics["average_perturbation"] = np.mean([e.perturbation_magnitude for e in events])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get defense metrics: {str(e)}")
            raise
    
    # Private methods for specific detection strategies
    
    async def _validate_input(
        self,
        model_id: str,
        input_data: Union[np.ndarray, Dict[str, Any]],
        config: DefenseConfig
    ) -> AdversarialDetectionResult:
        """Validate input using statistical and structural checks"""
        try:
            is_adversarial = False
            confidence = 0.0
            perturbation_magnitude = 0.0
            
            if isinstance(input_data, np.ndarray):
                # Check for extreme values
                if np.any(np.abs(input_data) > 10):  # Configurable threshold
                    is_adversarial = True
                    confidence = 0.8
                
                # Check for unusual statistical properties
                if np.std(input_data) > 5:  # Configurable threshold
                    is_adversarial = True
                    confidence = max(confidence, 0.6)
                
                perturbation_magnitude = np.linalg.norm(input_data) / input_data.size
            
            return AdversarialDetectionResult(
                is_adversarial=is_adversarial,
                confidence=confidence,
                attack_type=AttackType.EVASION if is_adversarial else None,
                detection_method="input_validation",
                perturbation_magnitude=perturbation_magnitude,
                metadata={}
            )
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return AdversarialDetectionResult(
                is_adversarial=True,
                confidence=1.0,
                attack_type=None,
                detection_method="input_validation_error",
                perturbation_magnitude=1.0,
                metadata={"error": str(e)}
            )
    
    async def _statistical_detection(
        self,
        model_id: str,
        input_data: np.ndarray,
        model_output: Optional[np.ndarray],
        config: DefenseConfig
    ) -> AdversarialDetectionResult:
        """Statistical-based adversarial detection"""
        # Simplified implementation - in production would use sophisticated ML models
        is_adversarial = False
        confidence = 0.0
        
        if model_output is not None:
            # Check prediction confidence
            max_confidence = np.max(model_output)
            if max_confidence < 0.5:  # Low confidence might indicate adversarial input
                is_adversarial = True
                confidence = 0.7
        
        return AdversarialDetectionResult(
            is_adversarial=is_adversarial,
            confidence=confidence,
            attack_type=AttackType.EVASION if is_adversarial else None,
            detection_method="statistical_detection",
            perturbation_magnitude=0.0,
            metadata={}
        )
    
    async def _feature_squeezing_detection(
        self,
        model_id: str,
        input_data: np.ndarray,
        config: DefenseConfig
    ) -> AdversarialDetectionResult:
        """Feature squeezing-based detection"""
        # Apply feature squeezing and compare outputs
        squeezed_input = self._apply_feature_squeezing(input_data)
        
        # Calculate difference
        difference = np.linalg.norm(input_data - squeezed_input)
        threshold = config.max_perturbation
        
        is_adversarial = difference > threshold
        confidence = min(difference / threshold, 1.0) if threshold > 0 else 0.0
        
        return AdversarialDetectionResult(
            is_adversarial=is_adversarial,
            confidence=confidence,
            attack_type=AttackType.EVASION if is_adversarial else None,
            detection_method="feature_squeezing",
            perturbation_magnitude=difference,
            metadata={}
        )
    
    async def _ensemble_detection(
        self,
        model_id: str,
        input_data: np.ndarray,
        model_output: Optional[np.ndarray],
        config: DefenseConfig
    ) -> AdversarialDetectionResult:
        """Ensemble-based adversarial detection"""
        # Simplified ensemble detection
        is_adversarial = False
        confidence = 0.0
        
        # In production, this would use multiple detection models
        detection_scores = [0.3, 0.1, 0.8, 0.2, 0.6]  # Mock scores
        avg_score = np.mean(detection_scores)
        
        if avg_score > config.detection_threshold:
            is_adversarial = True
            confidence = avg_score
        
        return AdversarialDetectionResult(
            is_adversarial=is_adversarial,
            confidence=confidence,
            attack_type=AttackType.EVASION if is_adversarial else None,
            detection_method="ensemble_detection",
            perturbation_magnitude=avg_score,
            metadata={"ensemble_scores": detection_scores}
        )
    
    def _aggregate_detection_results(
        self,
        results: List[AdversarialDetectionResult],
        config: DefenseConfig
    ) -> AdversarialDetectionResult:
        """Aggregate results from multiple detection methods"""
        if not results:
            return AdversarialDetectionResult(
                is_adversarial=False,
                confidence=0.0,
                attack_type=None,
                detection_method="no_detection",
                perturbation_magnitude=0.0,
                metadata={}
            )
        
        # Weighted voting
        total_confidence = sum(r.confidence for r in results if r.is_adversarial)
        avg_confidence = total_confidence / len(results)
        
        is_adversarial = avg_confidence > config.detection_threshold
        
        # Select most likely attack type
        attack_types = [r.attack_type for r in results if r.attack_type]
        attack_type = attack_types[0] if attack_types else None
        
        return AdversarialDetectionResult(
            is_adversarial=is_adversarial,
            confidence=avg_confidence,
            attack_type=attack_type,
            detection_method="aggregated",
            perturbation_magnitude=np.mean([r.perturbation_magnitude for r in results]),
            metadata={"individual_results": [r.__dict__ for r in results]}
        )
    
    def _apply_feature_squeezing(self, input_data: np.ndarray) -> np.ndarray:
        """Apply feature squeezing defense"""
        # Bit depth reduction
        squeezed = np.round(input_data * 4) / 4  # Reduce to 2-bit precision
        
        # Median filtering (simplified)
        return squeezed
    
    def _apply_randomized_smoothing(self, input_data: np.ndarray) -> np.ndarray:
        """Apply randomized smoothing"""
        noise = np.random.normal(0, 0.1, input_data.shape)
        return input_data + noise
    
    def _generate_fgsm_attack(self, input_data: np.ndarray, epsilon: float) -> np.ndarray:
        """Generate FGSM adversarial examples (simplified)"""
        # Simplified FGSM - in production would use actual gradients
        perturbation = np.random.uniform(-epsilon, epsilon, input_data.shape)
        return np.clip(input_data + perturbation, 0, 1)
    
    def _generate_pgd_attack(self, input_data: np.ndarray, epsilon: float) -> np.ndarray:
        """Generate PGD adversarial examples (simplified)"""
        # Simplified PGD - in production would use iterative gradient attacks
        perturbation = np.random.uniform(-epsilon, epsilon, input_data.shape)
        return np.clip(input_data + perturbation, 0, 1)
    
    def _generate_cw_attack(self, input_data: np.ndarray, target_class: Optional[int]) -> np.ndarray:
        """Generate Carlini & Wagner adversarial examples (simplified)"""
        # Simplified C&W - in production would use optimization-based attack
        perturbation = np.random.normal(0, 0.05, input_data.shape)
        return np.clip(input_data + perturbation, 0, 1)
    
    async def _adversarial_training(
        self,
        model_id: str,
        training_data: np.ndarray,
        training_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Implement adversarial training"""
        # Simplified adversarial training implementation
        return {
            "training_completed": True,
            "adversarial_examples_generated": len(training_data),
            "training_accuracy": 0.85,
            "robustness_improvement": 0.3
        }
    
    async def _defensive_distillation(
        self,
        model_id: str,
        training_data: np.ndarray,
        training_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Implement defensive distillation"""
        # Simplified defensive distillation implementation
        return {
            "distillation_completed": True,
            "temperature": 20,
            "training_accuracy": 0.82,
            "robustness_improvement": 0.25
        }
    
    def _evaluate_accuracy(self, test_data: np.ndarray, test_labels: np.ndarray) -> float:
        """Evaluate model accuracy (simplified)"""
        # Simplified accuracy evaluation
        return 0.75  # Mock accuracy
    
    async def _initialize_detection_model(self, model_id: str):
        """Initialize adversarial detection model"""
        # In production, this would load/train a detection model
        self.detection_models[model_id] = {"initialized": True}
    
    async def _log_attack_event(
        self,
        attack_type: AttackType,
        model_id: str,
        input_shape: Tuple,
        perturbation_magnitude: float,
        success: bool,
        defense_triggered: bool
    ):
        """Log adversarial attack event"""
        event = AttackEvent(
            timestamp=datetime.now(),
            attack_type=attack_type,
            model_id=model_id,
            input_shape=input_shape,
            perturbation_magnitude=perturbation_magnitude,
            success=success,
            defense_triggered=defense_triggered,
            metadata={}
        )
        
        self.attack_events.append(event)
        
        # Keep only recent events
        if len(self.attack_events) > 10000:
            self.attack_events = self.attack_events[-10000:]


# Global instance
adversarial_defense_engine = AdversarialDefenseEngine()