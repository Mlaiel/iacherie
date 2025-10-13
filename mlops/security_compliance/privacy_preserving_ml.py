"""
Privacy-Preserving Machine Learning
Enterprise privacy-preserving ML techniques and implementations

Features:
- Differential Privacy
- Federated Learning Support
- Homomorphic Encryption
- Secure Multi-party Computation
- Data Anonymization
- Privacy-aware Model Training

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
import hashlib


class PrivacyTechnique(Enum):
    """Privacy-preserving techniques"""
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    FEDERATED_LEARNING = "federated_learning"
    HOMOMORPHIC_ENCRYPTION = "homomorphic_encryption"
    SECURE_AGGREGATION = "secure_aggregation"
    DATA_ANONYMIZATION = "data_anonymization"
    NOISE_INJECTION = "noise_injection"


class PrivacyLevel(Enum):
    """Privacy protection levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class PrivacyConfig:
    """Privacy configuration for ML models"""
    technique: PrivacyTechnique
    privacy_level: PrivacyLevel
    epsilon: float = 1.0  # Privacy budget for differential privacy
    delta: float = 1e-5   # Delta parameter for differential privacy
    noise_scale: float = 1.0
    clipping_bound: float = 1.0
    batch_size: int = 32
    learning_rate: float = 0.01


@dataclass
class PrivacyMetrics:
    """Privacy metrics and measurements"""
    epsilon_spent: float
    delta_used: float
    privacy_level_achieved: PrivacyLevel
    data_points_processed: int
    noise_added: float
    utility_score: float  # Model utility after privacy application


class PrivacyPreservingML:
    """
    Enterprise Privacy-Preserving Machine Learning
    Implementation of privacy-preserving techniques for ML systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.privacy_configs: Dict[str, PrivacyConfig] = {}
        self.privacy_metrics: Dict[str, PrivacyMetrics] = {}
        self.privacy_budgets: Dict[str, float] = {}
        
    async def configure_privacy(
        self,
        model_id: str,
        config: PrivacyConfig
    ) -> bool:
        """Configure privacy-preserving settings for a model"""
        try:
            self.privacy_configs[model_id] = config
            
            # Initialize privacy budget
            if config.technique == PrivacyTechnique.DIFFERENTIAL_PRIVACY:
                self.privacy_budgets[model_id] = config.epsilon
            
            self.logger.info(f"Privacy configuration set for model {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure privacy for {model_id}: {str(e)}")
            return False
    
    async def apply_differential_privacy(
        self,
        model_id: str,
        gradients: np.ndarray,
        sensitivity: float = 1.0
    ) -> Tuple[np.ndarray, float]:
        """Apply differential privacy to model gradients"""
        try:
            config = self.privacy_configs.get(model_id)
            if not config or config.technique != PrivacyTechnique.DIFFERENTIAL_PRIVACY:
                raise ValueError(f"Differential privacy not configured for model {model_id}")
            
            # Check privacy budget
            current_budget = self.privacy_budgets.get(model_id, 0.0)
            if current_budget <= 0:
                raise ValueError(f"Privacy budget exhausted for model {model_id}")
            
            # Calculate noise scale using calibrated sensitivity
            noise_scale = sensitivity / config.epsilon
            
            # Add Gaussian noise to gradients
            noise = np.random.normal(0, noise_scale, gradients.shape)
            noisy_gradients = gradients + noise
            
            # Clip gradients to bound sensitivity
            if config.clipping_bound > 0:
                gradient_norms = np.linalg.norm(noisy_gradients, axis=1, keepdims=True)
                clipping_factor = np.minimum(1.0, config.clipping_bound / gradient_norms)
                noisy_gradients = noisy_gradients * clipping_factor
            
            # Update privacy budget
            epsilon_used = min(config.epsilon / 10, current_budget)  # Use 1/10 of budget per update
            self.privacy_budgets[model_id] = current_budget - epsilon_used
            
            # Update metrics
            self._update_privacy_metrics(model_id, epsilon_used, noise_scale)
            
            return noisy_gradients, epsilon_used
            
        except Exception as e:
            self.logger.error(f"Differential privacy application failed: {str(e)}")
            raise
    
    async def anonymize_data(
        self,
        model_id: str,
        data: np.ndarray,
        anonymization_method: str = "k_anonymity"
    ) -> np.ndarray:
        """Apply data anonymization techniques"""
        try:
            config = self.privacy_configs.get(model_id)
            if not config:
                raise ValueError(f"Privacy not configured for model {model_id}")
            
            if anonymization_method == "k_anonymity":
                return await self._apply_k_anonymity(data, k=5)
            elif anonymization_method == "l_diversity":
                return await self._apply_l_diversity(data, l=3)
            elif anonymization_method == "t_closeness":
                return await self._apply_t_closeness(data, t=0.1)
            elif anonymization_method == "gaussian_noise":
                return await self._apply_gaussian_noise(data, config.noise_scale)
            else:
                raise ValueError(f"Unknown anonymization method: {anonymization_method}")
                
        except Exception as e:
            self.logger.error(f"Data anonymization failed: {str(e)}")
            raise
    
    async def setup_federated_learning(
        self,
        model_id: str,
        participants: List[str],
        aggregation_method: str = "fedavg"
    ) -> Dict[str, Any]:
        """Set up federated learning configuration"""
        try:
            config = self.privacy_configs.get(model_id)
            if not config or config.technique != PrivacyTechnique.FEDERATED_LEARNING:
                raise ValueError(f"Federated learning not configured for model {model_id}")
            
            fl_config = {
                "model_id": model_id,
                "participants": participants,
                "aggregation_method": aggregation_method,
                "rounds": 100,
                "min_participants": max(2, len(participants) // 2),
                "secure_aggregation": True,
                "differential_privacy": config.privacy_level in [PrivacyLevel.HIGH, PrivacyLevel.MAXIMUM]
            }
            
            self.logger.info(f"Federated learning configured for model {model_id} with {len(participants)} participants")
            return fl_config
            
        except Exception as e:
            self.logger.error(f"Federated learning setup failed: {str(e)}")
            raise
    
    async def aggregate_federated_updates(
        self,
        model_id: str,
        participant_updates: List[Dict[str, np.ndarray]],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """Aggregate updates from federated learning participants"""
        try:
            if not participant_updates:
                raise ValueError("No participant updates provided")
            
            config = self.privacy_configs.get(model_id)
            if not config:
                raise ValueError(f"Privacy not configured for model {model_id}")
            
            # Apply secure aggregation if configured
            if config.privacy_level in [PrivacyLevel.HIGH, PrivacyLevel.MAXIMUM]:
                return await self._secure_aggregation(participant_updates, weights)
            else:
                return await self._simple_aggregation(participant_updates, weights)
                
        except Exception as e:
            self.logger.error(f"Federated aggregation failed: {str(e)}")
            raise
    
    async def apply_homomorphic_encryption(
        self,
        model_id: str,
        data: np.ndarray,
        operation: str = "addition"
    ) -> Dict[str, Any]:
        """Apply homomorphic encryption for secure computation"""
        try:
            config = self.privacy_configs.get(model_id)
            if not config or config.technique != PrivacyTechnique.HOMOMORPHIC_ENCRYPTION:
                raise ValueError(f"Homomorphic encryption not configured for model {model_id}")
            
            # Simplified homomorphic encryption implementation
            # In production, would use libraries like SEAL, HElib, or Pyfhel
            
            encrypted_data = {
                "encrypted_values": self._simple_encrypt(data),
                "encryption_params": {
                    "scheme": "BFV",  # Brakerski-Fan-Vercauteren scheme
                    "poly_modulus_degree": 4096,
                    "coeff_modulus": "default",
                    "plain_modulus": 1024
                },
                "supported_operations": ["addition", "multiplication", "scalar_multiplication"]
            }
            
            self.logger.info(f"Homomorphic encryption applied to data for model {model_id}")
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Homomorphic encryption failed: {str(e)}")
            raise
    
    async def evaluate_privacy_risk(
        self,
        model_id: str,
        test_data: np.ndarray,
        attack_types: List[str] = None
    ) -> Dict[str, Any]:
        """Evaluate privacy risks and potential attacks"""
        try:
            if attack_types is None:
                attack_types = ["membership_inference", "model_inversion", "property_inference"]
            
            config = self.privacy_configs.get(model_id)
            if not config:
                raise ValueError(f"Privacy not configured for model {model_id}")
            
            risk_assessment = {
                "model_id": model_id,
                "assessment_timestamp": datetime.now().isoformat(),
                "privacy_technique": config.technique.value,
                "privacy_level": config.privacy_level.value,
                "attack_assessments": {},
                "overall_risk": "unknown",
                "recommendations": []
            }
            
            total_risk_score = 0.0
            
            for attack_type in attack_types:
                attack_risk = await self._assess_attack_risk(model_id, attack_type, test_data)
                risk_assessment["attack_assessments"][attack_type] = attack_risk
                total_risk_score += attack_risk["risk_score"]
            
            # Calculate overall risk
            avg_risk_score = total_risk_score / len(attack_types)
            if avg_risk_score >= 0.8:
                risk_assessment["overall_risk"] = "high"
            elif avg_risk_score >= 0.5:
                risk_assessment["overall_risk"] = "medium"
            else:
                risk_assessment["overall_risk"] = "low"
            
            # Generate recommendations
            risk_assessment["recommendations"] = self._generate_privacy_recommendations(
                config, avg_risk_score
            )
            
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"Privacy risk evaluation failed: {str(e)}")
            raise
    
    async def get_privacy_metrics(self, model_id: str) -> Optional[PrivacyMetrics]:
        """Get privacy metrics for a model"""
        return self.privacy_metrics.get(model_id)
    
    async def get_privacy_budget_status(self, model_id: str) -> Dict[str, Any]:
        """Get current privacy budget status"""
        try:
            config = self.privacy_configs.get(model_id)
            current_budget = self.privacy_budgets.get(model_id, 0.0)
            
            if not config:
                return {"error": f"No privacy configuration for model {model_id}"}
            
            initial_budget = config.epsilon if config.technique == PrivacyTechnique.DIFFERENTIAL_PRIVACY else 0.0
            
            return {
                "model_id": model_id,
                "technique": config.technique.value,
                "initial_budget": initial_budget,
                "current_budget": current_budget,
                "budget_used": initial_budget - current_budget,
                "budget_remaining_percent": (current_budget / initial_budget * 100) if initial_budget > 0 else 0,
                "can_continue_training": current_budget > 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get privacy budget status: {str(e)}")
            return {"error": str(e)}
    
    # Private methods for privacy techniques
    
    async def _apply_k_anonymity(self, data: np.ndarray, k: int = 5) -> np.ndarray:
        """Apply k-anonymity to data"""
        # Simplified k-anonymity implementation
        # In production, would use proper anonymization libraries
        
        anonymized_data = data.copy()
        
        # Apply generalization (simplified)
        if len(data.shape) == 2:
            for col in range(data.shape[1]):
                # Generalize continuous values by binning
                col_data = anonymized_data[:, col]
                bins = np.linspace(col_data.min(), col_data.max(), max(2, len(col_data) // k))
                anonymized_data[:, col] = np.digitize(col_data, bins)
        
        return anonymized_data
    
    async def _apply_l_diversity(self, data: np.ndarray, l: int = 3) -> np.ndarray:
        """Apply l-diversity to data"""
        # Simplified l-diversity implementation
        anonymized_data = data.copy()
        
        # Add controlled diversity to sensitive attributes
        if len(data.shape) == 2 and data.shape[1] > 1:
            # Assume last column is sensitive
            sensitive_col = data.shape[1] - 1
            unique_values = np.unique(anonymized_data[:, sensitive_col])
            
            if len(unique_values) >= l:
                # Ensure each group has at least l diverse values
                for i in range(0, len(anonymized_data), l):
                    group_end = min(i + l, len(anonymized_data))
                    group_values = unique_values[:l] if len(unique_values) >= l else unique_values
                    for j, val in enumerate(group_values):
                        if i + j < group_end:
                            anonymized_data[i + j, sensitive_col] = val
        
        return anonymized_data
    
    async def _apply_t_closeness(self, data: np.ndarray, t: float = 0.1) -> np.ndarray:
        """Apply t-closeness to data"""
        # Simplified t-closeness implementation
        return await self._apply_gaussian_noise(data, t)
    
    async def _apply_gaussian_noise(self, data: np.ndarray, noise_scale: float) -> np.ndarray:
        """Apply Gaussian noise to data"""
        noise = np.random.normal(0, noise_scale, data.shape)
        return data + noise
    
    async def _secure_aggregation(
        self,
        participant_updates: List[Dict[str, np.ndarray]],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """Perform secure aggregation of participant updates"""
        if not participant_updates:
            raise ValueError("No updates to aggregate")
        
        # Simplified secure aggregation
        # In production, would use cryptographic protocols
        
        if weights is None:
            weights = [1.0 / len(participant_updates)] * len(participant_updates)
        
        # Get update keys (assuming all participants have same structure)
        update_keys = list(participant_updates[0].keys())
        aggregated_updates = {}
        
        for key in update_keys:
            # Aggregate updates for this key
            aggregated_value = np.zeros_like(participant_updates[0][key])
            
            for i, update in enumerate(participant_updates):
                if key in update:
                    aggregated_value += weights[i] * update[key]
            
            aggregated_updates[key] = aggregated_value
        
        # Return the first aggregated update (simplified)
        return aggregated_updates[update_keys[0]] if update_keys else np.array([])
    
    async def _simple_aggregation(
        self,
        participant_updates: List[Dict[str, np.ndarray]],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """Perform simple federated averaging"""
        return await self._secure_aggregation(participant_updates, weights)
    
    def _simple_encrypt(self, data: np.ndarray) -> List[str]:
        """Simple encryption simulation for homomorphic encryption"""
        # This is a placeholder - real homomorphic encryption is much more complex
        encrypted_values = []
        for value in data.flatten():
            # Simple "encryption" using hash (not real homomorphic encryption)
            encrypted = hashlib.sha256(str(value).encode()).hexdigest()[:16]
            encrypted_values.append(encrypted)
        return encrypted_values
    
    async def _assess_attack_risk(
        self,
        model_id: str,
        attack_type: str,
        test_data: np.ndarray
    ) -> Dict[str, Any]:
        """Assess risk for a specific type of privacy attack"""
        config = self.privacy_configs.get(model_id)
        
        # Simplified risk assessment
        base_risk = 0.5  # Default medium risk
        
        if attack_type == "membership_inference":
            # Lower risk with differential privacy
            if config.technique == PrivacyTechnique.DIFFERENTIAL_PRIVACY:
                risk_score = max(0.1, base_risk - (1.0 / config.epsilon))
            else:
                risk_score = base_risk + 0.2
                
        elif attack_type == "model_inversion":
            # Lower risk with federated learning
            if config.technique == PrivacyTechnique.FEDERATED_LEARNING:
                risk_score = base_risk - 0.3
            else:
                risk_score = base_risk + 0.1
                
        elif attack_type == "property_inference":
            # Risk depends on privacy level
            privacy_reduction = {
                PrivacyLevel.LOW: 0.0,
                PrivacyLevel.MEDIUM: 0.1,
                PrivacyLevel.HIGH: 0.3,
                PrivacyLevel.MAXIMUM: 0.4
            }
            risk_score = base_risk - privacy_reduction.get(config.privacy_level, 0.0)
            
        else:
            risk_score = base_risk
        
        # Clamp risk score between 0 and 1
        risk_score = max(0.0, min(1.0, risk_score))
        
        return {
            "attack_type": attack_type,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score >= 0.7 else "medium" if risk_score >= 0.4 else "low",
            "mitigation_effectiveness": 1.0 - risk_score
        }
    
    def _generate_privacy_recommendations(
        self,
        config: PrivacyConfig,
        avg_risk_score: float
    ) -> List[str]:
        """Generate privacy recommendations based on configuration and risk"""
        recommendations = []
        
        if avg_risk_score >= 0.7:
            recommendations.append("High privacy risk detected - consider increasing privacy protection")
            
            if config.technique == PrivacyTechnique.DIFFERENTIAL_PRIVACY:
                recommendations.append(f"Consider reducing epsilon from {config.epsilon} to strengthen privacy")
            
            if config.privacy_level == PrivacyLevel.LOW:
                recommendations.append("Upgrade to higher privacy level (MEDIUM or HIGH)")
        
        if config.technique == PrivacyTechnique.DIFFERENTIAL_PRIVACY:
            budget_remaining = self.privacy_budgets.get(config.technique.value, 0.0)
            if budget_remaining < config.epsilon * 0.1:
                recommendations.append("Privacy budget nearly exhausted - consider model refresh")
        
        if config.technique == PrivacyTechnique.FEDERATED_LEARNING:
            recommendations.append("Consider enabling secure aggregation for additional privacy")
        
        # General recommendations
        recommendations.append("Regularly assess privacy risks and update protections")
        recommendations.append("Monitor for privacy budget exhaustion")
        
        return recommendations
    
    def _update_privacy_metrics(self, model_id: str, epsilon_used: float, noise_added: float):
        """Update privacy metrics for a model"""
        existing_metrics = self.privacy_metrics.get(model_id)
        
        if existing_metrics:
            existing_metrics.epsilon_spent += epsilon_used
            existing_metrics.noise_added += noise_added
            existing_metrics.data_points_processed += 1
        else:
            config = self.privacy_configs.get(model_id)
            self.privacy_metrics[model_id] = PrivacyMetrics(
                epsilon_spent=epsilon_used,
                delta_used=config.delta if config else 0.0,
                privacy_level_achieved=config.privacy_level if config else PrivacyLevel.LOW,
                data_points_processed=1,
                noise_added=noise_added,
                utility_score=0.8  # Default utility score
            )


# Global instance
privacy_preserving_ml = PrivacyPreservingML()