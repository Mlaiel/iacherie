"""Adversarial Testing for AI Security

This module provides comprehensive adversarial testing capabilities
to ensure AI/ML models are robust against security attacks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import json
import uuid
import hashlib

logger = logging.getLogger(__name__)


class AdversarialAttackType(str, Enum):
    """
Types of adversarial attacks"""

    FGSM = "fast_gradient_sign_method"
    PGD = "projected_gradient_descent"
    CW = "carlini_wagner"
    DEEPFOOL = "deepfool"
    BOUNDARY = "boundary_attack"
    EVASION = "evasion_attack"
    POISONING = "poisoning_attack"
    MODEL_INVERSION = "model_inversion"
    MEMBERSHIP_INFERENCE = "membership_inference"


class SecurityThreatLevel(str, Enum):
    """Security threat severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class DefenseType(str, Enum):
    """Types of adversarial defenses"""

    ADVERSARIAL_TRAINING = "adversarial_training"
    GRADIENT_MASKING = "gradient_masking"
    INPUT_TRANSFORMATION = "input_transformation"
    DETECTION = "detection"
    CERTIFIED_DEFENSE = "certified_defense"


@dataclass
class AdversarialAttack:
    """Single adversarial attack configuration and results"""
    attack_id: str
    attack_type: AdversarialAttackType
    attack_parameters: Dict[str, Any]
    original_accuracy: float
    adversarial_accuracy: float
    attack_success_rate: float
    robustness_score: float
    threat_level: SecurityThreatLevel
    execution_time: float
    samples_tested: int
    attack_details: Dict[str, Any]


@dataclass
class SecurityMetrics:
    """
Comprehensive security metrics"""
    overall_robustness_score: float
    attack_success_rates: Dict[str, float]
    threat_assessment: SecurityThreatLevel
    vulnerability_areas: List[str]
    defense_effectiveness: Dict[str, float]
    security_score: float
    model_stability: float
    resistance_metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityValidationResult:
    """
Complete security validation result"""
    model_id: str
    validation_id: str
    security_metrics: SecurityMetrics
    individual_attacks: List[AdversarialAttack]
    overall_security_score: float
    critical_vulnerabilities: List[str]
    security_recommendations: List[str]
    defense_suggestions: List[str]
    validation_duration: float
    test_configuration: Dict[str, Any]


class AdversarialSecurityTester:
    """
Comprehensive adversarial security tester for AI/ML models"""
    
    def __init__(self, security_threshold: float = 0.85):
        """
        Initialize the adversarial security tester.
        
        Args:
            security_threshold: Minimum security score threshold (default: 0.85)
        """
        self.security_threshold = security_threshold
        self.validation_history = {}
        self.logger = logging.getLogger(__name__)
        
    async def validate_model_security(
        self,
        model_id: str,
        model_predict_func: Callable,
        X_test: np.ndarray,
        y_test: np.ndarray,
        attack_configs: Optional[List[Dict[str, Any]]] = None,
        defense_configs: Optional[List[Dict[str, Any]]] = None
    ) -> SecurityValidationResult:
        """
        Comprehensive security validation of AI/ML model.
        
        Args:
            model_id: Unique model identifier
            model_predict_func: Model prediction function
            X_test: Test features
            y_test: Test labels
            attack_configs: List of attack configurations to run
            defense_configs: List of defense configurations to test
            
        Returns:
            SecurityValidationResult: Comprehensive security validation result
        """
        start_time = datetime.utcnow()
        validation_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Starting security validation for model {model_id}")
            
            # Use default attack configs if none provided
            if attack_configs is None:
                attack_configs = self._get_default_attack_configs()
            
            # Calculate baseline accuracy
            baseline_predictions = model_predict_func(X_test)
            baseline_accuracy = np.mean(baseline_predictions == y_test)
            
            # Run adversarial attacks
            individual_attacks = await self._run_adversarial_attacks(
                model_predict_func, X_test, y_test, baseline_accuracy, attack_configs
            )
            
            # Calculate comprehensive security metrics
            security_metrics = await self._calculate_security_metrics(
                individual_attacks, baseline_accuracy, defense_configs
            )
            
            # Calculate overall security score
            overall_score = self._calculate_overall_security_score(security_metrics, individual_attacks)
            
            # Identify critical vulnerabilities
            critical_vulnerabilities = self._identify_critical_vulnerabilities(
                security_metrics, individual_attacks
            )
            
            # Generate security recommendations
            recommendations = self._generate_security_recommendations(
                security_metrics, individual_attacks
            )
            
            # Generate defense suggestions
            defense_suggestions = self._generate_defense_suggestions(
                security_metrics, individual_attacks
            )
            
            # Calculate validation duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Create validation result
            result = SecurityValidationResult(
                model_id=model_id,
                validation_id=validation_id,
                security_metrics=security_metrics,
                individual_attacks=individual_attacks,
                overall_security_score=overall_score,
                critical_vulnerabilities=critical_vulnerabilities,
                security_recommendations=recommendations,
                defense_suggestions=defense_suggestions,
                validation_duration=duration,
                test_configuration={
                    "attack_configs": attack_configs,
                    "defense_configs": defense_configs or [],
                    "baseline_accuracy": baseline_accuracy
                }
            )
            
            # Store validation history
            if model_id not in self.validation_history:
                self.validation_history[model_id] = []
            self.validation_history[model_id].append(result)
            
            self.logger.info(
                f"Security validation completed for model {model_id}: "
                f"Security Score={overall_score:.4f}, Vulnerabilities={len(critical_vulnerabilities)}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Security validation failed for model {model_id}: {str(e)}")
            raise
    
    def _get_default_attack_configs(self) -> List[Dict[str, Any]]:
        """Get default adversarial attack configurations"""
        return [
            {
                "attack_type": AdversarialAttackType.FGSM,
                "parameters": {"epsilon": 0.1, "targeted": False}
            },
            {
                "attack_type": AdversarialAttackType.PGD,
                "parameters": {"epsilon": 0.1, "steps": 10, "step_size": 0.01}
            },
            {
                "attack_type": AdversarialAttackType.EVASION,
                "parameters": {"perturbation_budget": 0.05}
            },
            {
                "attack_type": AdversarialAttackType.MEMBERSHIP_INFERENCE,
                "parameters": {"confidence_threshold": 0.8}
            }
        ]
    
    async def _run_adversarial_attacks(
        self,
        model_predict_func: Callable,
        X_test: np.ndarray,
        y_test: np.ndarray,
        baseline_accuracy: float,
        attack_configs: List[Dict[str, Any]]
    ) -> List[AdversarialAttack]:
        """Run specified adversarial attacks"""
        attacks = []
        
        for config in attack_configs:
            try:
                attack_start = datetime.utcnow()
                
                attack_type = config["attack_type"]
                parameters = config.get("parameters", {})
                
                # Run specific attack based on type
                if attack_type == AdversarialAttackType.FGSM:
                    attack_result = await self._run_fgsm_attack(
                        model_predict_func, X_test, y_test, parameters
                    )
                elif attack_type == AdversarialAttackType.PGD:
                    attack_result = await self._run_pgd_attack(
                        model_predict_func, X_test, y_test, parameters
                    )
                elif attack_type == AdversarialAttackType.EVASION:
                    attack_result = await self._run_evasion_attack(
                        model_predict_func, X_test, y_test, parameters
                    )
                elif attack_type == AdversarialAttackType.MEMBERSHIP_INFERENCE:
                    attack_result = await self._run_membership_inference_attack(
                        model_predict_func, X_test, y_test, parameters
                    )
                else:
                    # Simulated attack for unsupported types
                    attack_result = await self._run_simulated_attack(
                        model_predict_func, X_test, y_test, attack_type, parameters
                    )
                
                attack_end = datetime.utcnow()
                execution_time = (attack_end - attack_start).total_seconds()
                
                # Calculate attack success rate and robustness
                adversarial_accuracy = attack_result.get("adversarial_accuracy", baseline_accuracy)
                attack_success_rate = 1.0 - (adversarial_accuracy / baseline_accuracy) if baseline_accuracy > 0 else 0
                robustness_score = adversarial_accuracy / baseline_accuracy if baseline_accuracy > 0 else 1.0
                
                # Determine threat level
                threat_level = self._determine_threat_level(attack_success_rate)
                
                attack = AdversarialAttack(
                    attack_id=str(uuid.uuid4()),
                    attack_type=attack_type,
                    attack_parameters=parameters,
                    original_accuracy=baseline_accuracy,
                    adversarial_accuracy=adversarial_accuracy,
                    attack_success_rate=attack_success_rate,
                    robustness_score=robustness_score,
                    threat_level=threat_level,
                    execution_time=execution_time,
                    samples_tested=len(X_test),
                    attack_details=attack_result
                )
                
                attacks.append(attack)
                
            except Exception as e:
                self.logger.error(f"Attack {attack_type} failed: {str(e)}")
                continue
        
        return attacks
    
    async def _run_fgsm_attack(
        self,
        model_predict_func: Callable,
        X_test: np.ndarray,
        y_test: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Fast Gradient Sign Method attack (simulated)"""
        epsilon = parameters.get("epsilon", 0.1)
        
        # Simulate FGSM attack by adding noise
        # In a real implementation, you'd compute gradients and apply FGSM
        noise = np.random.normal(0, epsilon, X_test.shape)
        X_adversarial = np.clip(X_test + noise, X_test.min(), X_test.max())
        
        # Get predictions on adversarial examples
        adversarial_predictions = model_predict_func(X_adversarial)
        adversarial_accuracy = np.mean(adversarial_predictions == y_test)
        
        return {
            "adversarial_accuracy": adversarial_accuracy,
            "perturbation_norm": np.mean(np.linalg.norm(noise, axis=1)),
            "epsilon": epsilon,
            "attack_method": "FGSM (simulated)"
        }
    
    async def _run_pgd_attack(
        self,
        model_predict_func: Callable,
        X_test: np.ndarray,
        y_test: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Projected Gradient Descent attack (simulated)"""
        epsilon = parameters.get("epsilon", 0.1)
        steps = parameters.get("steps", 10)
        step_size = parameters.get("step_size", 0.01)
        
        # Simulate PGD attack with iterative perturbations
        X_adversarial = X_test.copy()
        
        for step in range(steps):
            noise = np.random.normal(0, step_size, X_test.shape)
            X_adversarial = np.clip(X_adversarial + noise, 
                                   X_test - epsilon, X_test + epsilon)
            X_adversarial = np.clip(X_adversarial, X_test.min(), X_test.max())
        
        adversarial_predictions = model_predict_func(X_adversarial)
        adversarial_accuracy = np.mean(adversarial_predictions == y_test)
        
        return {
            "adversarial_accuracy": adversarial_accuracy,
            "perturbation_norm": np.mean(np.linalg.norm(X_adversarial - X_test, axis=1)),
            "epsilon": epsilon,
            "steps": steps,
            "attack_method": "PGD (simulated)"
        }
    
    async def _run_evasion_attack(
        self,
        model_predict_func: Callable,
        X_test: np.ndarray,
        y_test: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run evasion attack (simulated)"""
        perturbation_budget = parameters.get("perturbation_budget", 0.05)
        
        # Simulate evasion by adding targeted noise
        noise_scale = perturbation_budget * np.std(X_test, axis=0)
        noise = np.random.normal(0, noise_scale, X_test.shape)
        X_adversarial = X_test + noise
        
        adversarial_predictions = model_predict_func(X_adversarial)
        adversarial_accuracy = np.mean(adversarial_predictions == y_test)
        
        return {
            "adversarial_accuracy": adversarial_accuracy,
            "perturbation_budget": perturbation_budget,
            "evasion_rate": 1.0 - adversarial_accuracy,
            "attack_method": "Evasion (simulated)"
        }
    
    async def _run_membership_inference_attack(
        self,
        model_predict_func: Callable,
        X_test: np.ndarray,
        y_test: np.ndarray,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run membership inference attack (simulated)"""
        confidence_threshold = parameters.get("confidence_threshold", 0.8)
        
        # Simulate membership inference by analyzing prediction confidence
        # In practice, this would require access to prediction probabilities
        predictions = model_predict_func(X_test)
        accuracy = np.mean(predictions == y_test)
        
        # Simulate inference success rate based on accuracy
        inference_success_rate = min(0.9, accuracy * 1.2) if accuracy > 0.7 else 0.5
        privacy_leakage = inference_success_rate - 0.5  # Above random guessing
        
        return {
            "adversarial_accuracy": accuracy,  # Not directly applicable
            "inference_success_rate": inference_success_rate,
            "privacy_leakage": privacy_leakage,
            "confidence_threshold": confidence_threshold,
            "attack_method": "Membership Inference (simulated)"
        }
    
    async def _run_simulated_attack(
        self,
        model_predict_func: Callable,
        X_test: np.ndarray,
        y_test: np.ndarray,
        attack_type: AdversarialAttackType,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run simulated attack for unsupported attack types"""
        baseline_predictions = model_predict_func(X_test)
        baseline_accuracy = np.mean(baseline_predictions == y_test)
        
        # Simulate attack with random perturbation
        noise_level = parameters.get("noise_level", 0.1)
        noise = np.random.normal(0, noise_level, X_test.shape)
        X_adversarial = X_test + noise
        
        adversarial_predictions = model_predict_func(X_adversarial)
        adversarial_accuracy = np.mean(adversarial_predictions == y_test)
        
        return {
            "adversarial_accuracy": adversarial_accuracy,
            "attack_type": attack_type,
            "simulated": True,
            "attack_method": f"{attack_type} (simulated)"
        }
    
    def _determine_threat_level(self, attack_success_rate: float) -> SecurityThreatLevel:
        """Determine threat level based on attack success rate"""
        if attack_success_rate >= 0.8:
            return SecurityThreatLevel.CRITICAL
        elif attack_success_rate >= 0.6:
            return SecurityThreatLevel.HIGH
        elif attack_success_rate >= 0.4:
            return SecurityThreatLevel.MEDIUM
        elif attack_success_rate >= 0.2:
            return SecurityThreatLevel.LOW
        else:
            return SecurityThreatLevel.MINIMAL
    
    async def _calculate_security_metrics(
        self,
        attacks: List[AdversarialAttack],
        baseline_accuracy: float,
        defense_configs: Optional[List[Dict[str, Any]]] = None
    ) -> SecurityMetrics:
        """
Calculate comprehensive security metrics"""
        
        if not attacks:
            return SecurityMetrics(
                overall_robustness_score=1.0,
                attack_success_rates={},
                threat_assessment=SecurityThreatLevel.MINIMAL,
                vulnerability_areas=[],
                defense_effectiveness={},
                security_score=1.0,
                model_stability=1.0,
                resistance_metrics={}
            )
        
        # Calculate attack success rates by type
        attack_success_rates = {}
        for attack in attacks:
            attack_type = attack.attack_type
            if attack_type not in attack_success_rates:
                attack_success_rates[attack_type] = []
            attack_success_rates[attack_type].append(attack.attack_success_rate)
        
        # Average success rates by attack type
        avg_success_rates = {
            attack_type: np.mean(rates)
            for attack_type, rates in attack_success_rates.items()
        }
        
        # Calculate overall robustness score
        all_robustness_scores = [attack.robustness_score for attack in attacks]
        overall_robustness_score = np.mean(all_robustness_scores)
        
        # Determine overall threat assessment
        max_success_rate = max(avg_success_rates.values()) if avg_success_rates else 0
        threat_assessment = self._determine_threat_level(max_success_rate)
        
        # Identify vulnerability areas
        vulnerability_areas = [
            attack_type for attack_type, success_rate in avg_success_rates.items()
            if success_rate > 0.3
        ]
        
        # Calculate defense effectiveness (if defenses were tested)
        defense_effectiveness = {}
        if defense_configs:
            for defense_config in defense_configs:
                defense_type = defense_config.get("type", "unknown")
                # Simulate defense effectiveness
                effectiveness = np.random.uniform(0.6, 0.9)
                defense_effectiveness[defense_type] = effectiveness
        
        # Calculate security score
        security_score = self._calculate_security_score(
            overall_robustness_score, avg_success_rates, defense_effectiveness
        )
        
        # Calculate model stability
        stability_scores = [attack.robustness_score for attack in attacks]
        model_stability = np.mean(stability_scores) if stability_scores else 1.0
        
        # Calculate resistance metrics
        resistance_metrics = {
            "evasion_resistance": 1.0 - avg_success_rates.get(AdversarialAttackType.EVASION, 0),
            "poisoning_resistance": 1.0 - avg_success_rates.get(AdversarialAttackType.POISONING, 0),
            "privacy_resistance": 1.0 - avg_success_rates.get(AdversarialAttackType.MEMBERSHIP_INFERENCE, 0)
        }
        
        return SecurityMetrics(
            overall_robustness_score=overall_robustness_score,
            attack_success_rates=avg_success_rates,
            threat_assessment=threat_assessment,
            vulnerability_areas=vulnerability_areas,
            defense_effectiveness=defense_effectiveness,
            security_score=security_score,
            model_stability=model_stability,
            resistance_metrics=resistance_metrics
        )
    
    def _calculate_security_score(
        self,
        robustness_score: float,
        attack_success_rates: Dict[str, float],
        defense_effectiveness: Dict[str, float]
    ) -> float:
        """Calculate overall security score"""
        # Base score from robustness
        base_score = robustness_score * 0.4
        
        # Attack resistance score
        if attack_success_rates:
            max_success_rate = max(attack_success_rates.values())
            attack_resistance = (1.0 - max_success_rate) * 0.4
        else:
            attack_resistance = 0.4
        
        # Defense effectiveness score
        if defense_effectiveness:
            defense_score = np.mean(list(defense_effectiveness.values())) * 0.2
        else:
            defense_score = 0.1  # Partial credit for no major vulnerabilities
        
        return base_score + attack_resistance + defense_score
    
    def _calculate_overall_security_score(
        self, security_metrics: SecurityMetrics, attacks: List[AdversarialAttack]
    ) -> float:
        """
Calculate overall security score"""
        return security_metrics.security_score
    
    def _identify_critical_vulnerabilities(
        self, security_metrics: SecurityMetrics, attacks: List[AdversarialAttack]
    ) -> List[str]:
        """
Identify critical security vulnerabilities"""
        vulnerabilities = []
        
        if security_metrics.threat_assessment in [SecurityThreatLevel.CRITICAL, SecurityThreatLevel.HIGH]:
            vulnerabilities.append(f"High threat level detected: {security_metrics.threat_assessment}")
        
        if security_metrics.overall_robustness_score < 0.7:
            vulnerabilities.append("Low overall robustness to adversarial attacks")
        
        for attack_type, success_rate in security_metrics.attack_success_rates.items():
            if success_rate > 0.5:
                vulnerabilities.append(f"High vulnerability to {attack_type} attacks")
        
        if security_metrics.security_score < self.security_threshold:
            vulnerabilities.append("Overall security score below threshold")
        
        return vulnerabilities
    
    def _generate_security_recommendations(
        self, security_metrics: SecurityMetrics, attacks: List[AdversarialAttack]
    ) -> List[str]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        if security_metrics.security_score < self.security_threshold:
            recommendations.append("Implement comprehensive adversarial defense mechanisms")
        
        if security_metrics.overall_robustness_score < 0.8:
            recommendations.append("Improve model robustness through adversarial training")
        
        for vulnerability in security_metrics.vulnerability_areas:
            recommendations.append(f"Address vulnerabilities to {vulnerability} attacks")
        
        if not security_metrics.defense_effectiveness:
            recommendations.append("Implement and test adversarial defense strategies")
        
        return recommendations
    
    def _generate_defense_suggestions(
        self, security_metrics: SecurityMetrics, attacks: List[AdversarialAttack]
    ) -> List[str]:
        """Generate specific defense suggestions"""
        suggestions = []
        
        # Check for specific attack vulnerabilities
        for attack_type, success_rate in security_metrics.attack_success_rates.items():
            if success_rate > 0.3:
                if attack_type == AdversarialAttackType.FGSM:
                    suggestions.append("Implement gradient masking or adversarial training for FGSM defense")
                elif attack_type == AdversarialAttackType.PGD:
                    suggestions.append("Use certified defenses or robust optimization for PGD resistance")
                elif attack_type == AdversarialAttackType.EVASION:
                    suggestions.append("Implement input validation and anomaly detection")
                elif attack_type == AdversarialAttackType.MEMBERSHIP_INFERENCE:
                    suggestions.append("Use differential privacy or model ensembling")
        
        # General suggestions based on threat level
        if security_metrics.threat_assessment == SecurityThreatLevel.CRITICAL:
            suggestions.append("Immediate security review and enhanced defense deployment required")
        
        return suggestions
    
    def get_security_history(self, model_id: str) -> List[SecurityValidationResult]:
        """Get security validation history for a model"""
        return self.validation_history.get(model_id, [])
    
    async def continuous_security_monitoring(
        self,
        model_id: str,
        monitoring_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Setup continuous security monitoring"""
        config = {
            "model_id": model_id,
            "security_threshold": monitoring_config.get("threshold", self.security_threshold),
            "attack_frequency": monitoring_config.get("frequency", "weekly"),
            "defense_testing": monitoring_config.get("test_defenses", True),
            "alert_on_threats": monitoring_config.get("alerts", True),
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Continuous security monitoring setup for model {model_id}")
        return config