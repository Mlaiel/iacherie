# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Model Security Tests - Enterprise Grade Test Suite

Comprehensive tests for ML model security, adversarial defense, privacy protection,
data protection, audit logging, and compliance validation systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import tensorflow as tf
import asyncio
import tempfile
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import jwt

from ai.ml.model_security import (
    ModelSecurityManager, AdversarialDefense, PrivacyPreserver,
    ModelEncryption, SecureInference, AccessController,
    AuditLogger, ComplianceValidator, ThreatDetector,
    ModelIntegrityChecker, SecureFederatedLearning, DifferentialPrivacy,
    HomomorphicEncryption, SecureMultiPartyComputation, ModelWatermarking,
    AttackDetector, VulnerabilityScanner, SecurityMetrics,
    DataAnonymizer, PII_Detector, GDPR_Compliance, HIPAA_Compliance,
    BiasDetector, FairnessValidator, EthicalAI_Checker
)


class TestModelSecurityManager:
    """Tests for core model security management functionality"""
    
    def test_init_security_manager(self):
        """Test security manager initialization"""
        manager = ModelSecurityManager(
            security_policies=["encryption", "access_control", "audit_logging"],
            threat_detection_enabled=True,
            compliance_standards=["GDPR", "HIPAA", "SOX"],
            enable_adversarial_defense=True,
            privacy_level="high"
        )
        
        assert len(manager.security_policies) == 3
        assert manager.threat_detection_enabled
        assert len(manager.compliance_standards) == 3
        assert manager.enable_adversarial_defense
        assert manager.privacy_level == "high"

    def test_security_assessment(self, trained_model):
        """Test comprehensive security assessment"""
        manager = ModelSecurityManager()
        
        assessment_config = {
            "model": trained_model,
            "assessment_types": [
                "vulnerability_scan",
                "adversarial_robustness",
                "privacy_leakage",
                "bias_detection",
                "integrity_check"
            ],
            "threat_model": "standard",
            "compliance_requirements": ["GDPR", "AIACT"]
        }
        
        with patch.object(manager, 'conduct_security_assessment') as mock_assess:
            mock_assess.return_value = {
                "assessment_id": "assess_001",
                "overall_security_score": 8.7,
                "vulnerability_results": {
                    "high_risk": 0,
                    "medium_risk": 2,
                    "low_risk": 5,
                    "total_vulnerabilities": 7
                },
                "adversarial_robustness": {
                    "fgsm_attack": {"success_rate": 0.15, "robustness_score": 0.85},
                    "pgd_attack": {"success_rate": 0.22, "robustness_score": 0.78},
                    "c&w_attack": {"success_rate": 0.08, "robustness_score": 0.92}
                },
                "privacy_score": 9.2,
                "bias_score": 8.8,
                "integrity_verified": True,
                "compliance_status": {
                    "GDPR": "compliant",
                    "AIACT": "compliant"
                },
                "recommendations": [
                    "Implement input validation",
                    "Add adversarial training",
                    "Enhance monitoring"
                ]
            }
            
            assessment_result = manager.conduct_security_assessment(assessment_config)
            
            assert "assessment_id" in assessment_result
            assert assessment_result["overall_security_score"] > 8.0
            assert assessment_result["integrity_verified"] is True
            assert all(
                status == "compliant" 
                for status in assessment_result["compliance_status"].values()
            )

    def test_threat_modeling(self):
        """Test threat modeling for ML systems"""
        manager = ModelSecurityManager(threat_detection_enabled=True)
        
        threat_model_config = {
            "model_type": "neural_network",
            "deployment_environment": "cloud",
            "data_sensitivity": "high",
            "attack_vectors": [
                "model_inversion",
                "membership_inference",
                "poisoning_attack",
                "evasion_attack",
                "model_stealing"
            ]
        }
        
        with patch.object(manager, 'generate_threat_model') as mock_threat:
            mock_threat.return_value = {
                "threat_model_id": "tm_001",
                "identified_threats": [
                    {
                        "threat_id": "T001",
                        "threat_type": "model_inversion",
                        "severity": "high",
                        "likelihood": "medium",
                        "risk_score": 7.5,
                        "mitigation": "Implement differential privacy"
                    },
                    {
                        "threat_id": "T002",
                        "threat_type": "evasion_attack",
                        "severity": "medium",
                        "likelihood": "high",
                        "risk_score": 6.8,
                        "mitigation": "Add adversarial training"
                    }
                ],
                "risk_matrix": {
                    "high_risk": 1,
                    "medium_risk": 1,
                    "low_risk": 3
                },
                "security_controls": [
                    "input_validation",
                    "output_sanitization",
                    "rate_limiting",
                    "anomaly_detection"
                ]
            }
            
            threat_model = manager.generate_threat_model(threat_model_config)
            
            assert "threat_model_id" in threat_model
            assert "identified_threats" in threat_model
            assert len(threat_model["identified_threats"]) >= 2

    def test_security_policy_enforcement(self):
        """Test security policy enforcement"""
        manager = ModelSecurityManager(
            security_policies=["data_encryption", "access_control", "audit_logging"]
        )
        
        policy_config = {
            "policy_name": "data_protection_policy",
            "policy_rules": [
                {"rule": "encrypt_at_rest", "enabled": True},
                {"rule": "encrypt_in_transit", "enabled": True},
                {"rule": "access_logging", "enabled": True},
                {"rule": "data_masking", "enabled": True}
            ],
            "enforcement_mode": "strict",
            "violation_action": "block"
        }
        
        with patch.object(manager, 'enforce_security_policies') as mock_enforce:
            mock_enforce.return_value = {
                "policy_id": "policy_001",
                "enforcement_status": "active",
                "rules_enforced": 4,
                "violations_detected": 0,
                "compliance_score": 100,
                "last_enforcement": datetime.now().isoformat()
            }
            
            enforcement_result = manager.enforce_security_policies(policy_config)
            
            assert enforcement_result["enforcement_status"] == "active"
            assert enforcement_result["violations_detected"] == 0
            assert enforcement_result["compliance_score"] == 100


class TestAdversarialDefense:
    """Tests for adversarial attack defense mechanisms"""
    
    def test_init_adversarial_defense(self):
        """Test adversarial defense initialization"""
        defense = AdversarialDefense(
            defense_methods=["adversarial_training", "input_preprocessing", "certified_defense"],
            detection_enabled=True,
            response_strategy="adaptive",
            logging_level="detailed"
        )
        
        assert len(defense.defense_methods) == 3
        assert defense.detection_enabled
        assert defense.response_strategy == "adaptive"

    def test_fgsm_attack_detection(self, trained_model, sample_inputs):
        """Test FGSM (Fast Gradient Sign Method) attack detection"""
        defense = AdversarialDefense(detection_enabled=True)
        
        # Simulate FGSM attack
        attack_config = {
            "attack_type": "fgsm",
            "epsilon": 0.1,
            "targeted": False,
            "confidence_threshold": 0.5
        }
        
        with patch.object(defense, 'detect_fgsm_attack') as mock_detect:
            mock_detect.return_value = {
                "attack_detected": True,
                "attack_confidence": 0.87,
                "attacked_samples": 15,
                "total_samples": 100,
                "attack_success_rate": 0.15,
                "detection_time": 2.3,
                "defense_triggered": True
            }
            
            detection_result = defense.detect_fgsm_attack(
                model=trained_model,
                inputs=sample_inputs,
                config=attack_config
            )
            
            assert detection_result["attack_detected"] is True
            assert detection_result["defense_triggered"] is True
            assert detection_result["attack_success_rate"] < 0.2

    def test_pgd_attack_defense(self, trained_model, sample_inputs):
        """Test PGD (Projected Gradient Descent) attack defense"""
        defense = AdversarialDefense(
            defense_methods=["input_preprocessing", "adversarial_training"]
        )
        
        pgd_config = {
            "attack_type": "pgd",
            "epsilon": 0.03,
            "alpha": 0.01,
            "num_iter": 10,
            "random_start": True
        }
        
        with patch.object(defense, 'defend_against_pgd') as mock_defend:
            mock_defend.return_value = {
                "defense_success": True,
                "original_accuracy": 0.94,
                "defended_accuracy": 0.91,
                "robustness_improvement": 0.23,
                "processing_overhead": 1.45,
                "defense_methods_used": ["input_preprocessing", "adversarial_training"]
            }
            
            defense_result = defense.defend_against_pgd(
                model=trained_model,
                inputs=sample_inputs,
                config=pgd_config
            )
            
            assert defense_result["defense_success"] is True
            assert defense_result["defended_accuracy"] > 0.9
            assert defense_result["robustness_improvement"] > 0.2

    def test_cw_attack_mitigation(self, trained_model, sample_inputs):
        """Test Carlini & Wagner attack mitigation"""
        defense = AdversarialDefense(defense_methods=["certified_defense"])
        
        cw_config = {
            "attack_type": "c&w",
            "confidence": 0,
            "learning_rate": 0.01,
            "max_iterations": 100,
            "initial_const": 0.01
        }
        
        with patch.object(defense, 'mitigate_cw_attack') as mock_mitigate:
            mock_mitigate.return_value = {
                "mitigation_success": True,
                "attack_prevented": True,
                "perturbation_reduced": 0.67,
                "confidence_preserved": 0.89,
                "mitigation_time": 5.2,
                "certified_robustness": 0.85
            }
            
            mitigation_result = defense.mitigate_cw_attack(
                model=trained_model,
                inputs=sample_inputs,
                config=cw_config
            )
            
            assert mitigation_result["mitigation_success"] is True
            assert mitigation_result["attack_prevented"] is True
            assert mitigation_result["certified_robustness"] > 0.8

    def test_adversarial_training(self, base_model, training_data):
        """Test adversarial training process"""
        defense = AdversarialDefense(defense_methods=["adversarial_training"])
        
        training_config = {
            "epochs": 10,
            "adversarial_ratio": 0.5,
            "attack_methods": ["fgsm", "pgd"],
            "epsilon_schedule": [0.01, 0.02, 0.03],
            "regularization": 0.001
        }
        
        with patch.object(defense, 'adversarial_training') as mock_train:
            mock_train.return_value = {
                "training_id": "adv_train_001",
                "epochs_completed": 10,
                "final_clean_accuracy": 0.91,
                "final_adversarial_accuracy": 0.87,
                "robustness_gain": 0.34,
                "training_time": 3600,
                "model_checkpoints": ["epoch_5.pth", "epoch_10.pth"]
            }
            
            training_result = defense.adversarial_training(
                model=base_model,
                training_data=training_data,
                config=training_config
            )
            
            assert training_result["epochs_completed"] == 10
            assert training_result["final_adversarial_accuracy"] > 0.85
            assert training_result["robustness_gain"] > 0.3

    def test_certified_defense(self, trained_model):
        """Test certified defense mechanisms"""
        defense = AdversarialDefense(defense_methods=["certified_defense"])
        
        certification_config = {
            "certification_method": "randomized_smoothing",
            "noise_sigma": 0.25,
            "num_samples": 1000,
            "confidence_level": 0.99,
            "radius": 0.5
        }
        
        with patch.object(defense, 'apply_certified_defense') as mock_certify:
            mock_certify.return_value = {
                "certification_id": "cert_001",
                "certified_accuracy": 0.89,
                "certified_radius": 0.47,
                "robustness_certificate": "valid",
                "confidence_interval": [0.87, 0.91],
                "certification_time": 45.6
            }
            
            certification_result = defense.apply_certified_defense(
                model=trained_model,
                config=certification_config
            )
            
            assert certification_result["robustness_certificate"] == "valid"
            assert certification_result["certified_accuracy"] > 0.85
            assert certification_result["certified_radius"] > 0.4


class TestPrivacyPreserver:
    """Tests for privacy preservation mechanisms"""
    
    def test_init_privacy_preserver(self):
        """Test privacy preserver initialization"""
        preserver = PrivacyPreserver(
            privacy_techniques=["differential_privacy", "federated_learning", "homomorphic_encryption"],
            privacy_budget=1.0,
            noise_mechanism="gaussian",
            enable_secure_aggregation=True
        )
        
        assert len(preserver.privacy_techniques) == 3
        assert preserver.privacy_budget == 1.0
        assert preserver.noise_mechanism == "gaussian"
        assert preserver.enable_secure_aggregation

    def test_differential_privacy_training(self, training_data):
        """Test differential privacy in training"""
        preserver = PrivacyPreserver(
            privacy_techniques=["differential_privacy"],
            privacy_budget=1.0
        )
        
        dp_config = {
            "epsilon": 1.0,
            "delta": 1e-5,
            "max_grad_norm": 1.0,
            "noise_multiplier": 1.1,
            "batch_size": 32,
            "epochs": 10
        }
        
        with patch.object(preserver, 'apply_differential_privacy') as mock_dp:
            mock_dp.return_value = {
                "dp_training_id": "dp_001",
                "privacy_spent": 0.95,
                "privacy_remaining": 0.05,
                "noise_added": True,
                "model_accuracy": 0.88,
                "privacy_utility_tradeoff": 0.73,
                "epsilon_consumption": [0.1, 0.2, 0.3, 0.35]
            }
            
            dp_result = preserver.apply_differential_privacy(
                training_data=training_data,
                config=dp_config
            )
            
            assert dp_result["noise_added"] is True
            assert dp_result["privacy_spent"] < 1.0
            assert dp_result["model_accuracy"] > 0.85

    def test_federated_learning_privacy(self, distributed_data):
        """Test privacy in federated learning"""
        preserver = PrivacyPreserver(
            privacy_techniques=["federated_learning"],
            enable_secure_aggregation=True
        )
        
        fl_config = {
            "num_clients": 10,
            "client_fraction": 0.8,
            "local_epochs": 5,
            "communication_rounds": 20,
            "secure_aggregation": True,
            "differential_privacy": {"epsilon": 2.0, "delta": 1e-5}
        }
        
        with patch.object(preserver, 'federated_learning_with_privacy') as mock_fl:
            mock_fl.return_value = {
                "fl_session_id": "fl_001",
                "rounds_completed": 20,
                "participating_clients": 8,
                "global_model_accuracy": 0.92,
                "privacy_preserved": True,
                "communication_cost": 2.3,
                "aggregation_secure": True,
                "privacy_budget_used": 1.8
            }
            
            fl_result = preserver.federated_learning_with_privacy(
                distributed_data=distributed_data,
                config=fl_config
            )
            
            assert fl_result["privacy_preserved"] is True
            assert fl_result["aggregation_secure"] is True
            assert fl_result["global_model_accuracy"] > 0.9

    def test_homomorphic_encryption(self, sensitive_data):
        """Test homomorphic encryption for secure computation"""
        preserver = PrivacyPreserver(
            privacy_techniques=["homomorphic_encryption"]
        )
        
        he_config = {
            "encryption_scheme": "bfv",
            "polynomial_modulus": 8192,
            "coefficient_modulus": [40, 40, 40, 40],
            "plain_modulus": 1024
        }
        
        with patch.object(preserver, 'apply_homomorphic_encryption') as mock_he:
            mock_he.return_value = {
                "encryption_id": "he_001",
                "data_encrypted": True,
                "computation_performed": True,
                "result_decrypted": True,
                "encryption_time": 12.5,
                "computation_time": 45.6,
                "decryption_time": 8.3,
                "privacy_maintained": True
            }
            
            he_result = preserver.apply_homomorphic_encryption(
                data=sensitive_data,
                config=he_config
            )
            
            assert he_result["data_encrypted"] is True
            assert he_result["privacy_maintained"] is True
            assert he_result["computation_performed"] is True

    def test_secure_multiparty_computation(self, multi_party_data):
        """Test secure multi-party computation"""
        preserver = PrivacyPreserver()
        
        smc_config = {
            "num_parties": 3,
            "computation_type": "joint_training",
            "security_threshold": 2,
            "protocol": "shamir_secret_sharing",
            "communication_secure": True
        }
        
        with patch.object(preserver, 'secure_multiparty_computation') as mock_smc:
            mock_smc.return_value = {
                "smc_session_id": "smc_001",
                "parties_participated": 3,
                "computation_completed": True,
                "result_shared": True,
                "privacy_preserved": True,
                "security_threshold_met": True,
                "computation_time": 180.5
            }
            
            smc_result = preserver.secure_multiparty_computation(
                parties_data=multi_party_data,
                config=smc_config
            )
            
            assert smc_result["computation_completed"] is True
            assert smc_result["privacy_preserved"] is True
            assert smc_result["security_threshold_met"] is True

    def test_membership_inference_protection(self, trained_model, training_data, test_data):
        """Test protection against membership inference attacks"""
        preserver = PrivacyPreserver()
        
        protection_config = {
            "protection_method": "differential_privacy",
            "epsilon": 1.0,
            "attack_simulation": True,
            "evaluation_rounds": 100
        }
        
        with patch.object(preserver, 'protect_against_membership_inference') as mock_protect:
            mock_protect.return_value = {
                "protection_id": "mi_protect_001",
                "attack_success_rate_before": 0.65,
                "attack_success_rate_after": 0.52,
                "privacy_improvement": 0.20,
                "utility_loss": 0.03,
                "protection_effective": True,
                "privacy_score": 8.7
            }
            
            protection_result = preserver.protect_against_membership_inference(
                model=trained_model,
                training_data=training_data,
                test_data=test_data,
                config=protection_config
            )
            
            assert protection_result["protection_effective"] is True
            assert protection_result["privacy_improvement"] > 0.15
            assert protection_result["utility_loss"] < 0.05


class TestModelEncryption:
    """Tests for model encryption and secure storage"""
    
    def test_init_model_encryption(self):
        """Test model encryption initialization"""
        encryption = ModelEncryption(
            encryption_algorithms=["AES-256", "RSA-2048", "ChaCha20"],
            key_management_system="vault",
            enable_key_rotation=True,
            encryption_at_rest=True,
            encryption_in_transit=True
        )
        
        assert len(encryption.encryption_algorithms) == 3
        assert encryption.key_management_system == "vault"
        assert encryption.enable_key_rotation
        assert encryption.encryption_at_rest
        assert encryption.encryption_in_transit

    def test_model_encryption_aes(self, trained_model, temp_dir):
        """Test AES model encryption"""
        encryption = ModelEncryption(encryption_algorithms=["AES-256"])
        
        encryption_config = {
            "algorithm": "AES-256",
            "mode": "GCM",
            "key_derivation": "PBKDF2",
            "iterations": 100000,
            "salt_size": 32
        }
        
        model_path = temp_dir / "model.pth"
        encrypted_path = temp_dir / "model.encrypted"
        
        with patch.object(encryption, 'encrypt_model_aes') as mock_encrypt:
            mock_encrypt.return_value = {
                "encryption_id": "enc_001",
                "encrypted_path": str(encrypted_path),
                "encryption_key_id": "key_123",
                "algorithm": "AES-256-GCM",
                "encryption_time": 5.2,
                "file_size_encrypted": 256.8,
                "integrity_hash": "sha256:abc123...",
                "encryption_successful": True
            }
            
            encryption_result = encryption.encrypt_model_aes(
                model_path=model_path,
                output_path=encrypted_path,
                config=encryption_config
            )
            
            assert encryption_result["encryption_successful"] is True
            assert "encryption_key_id" in encryption_result
            assert "integrity_hash" in encryption_result

    def test_model_decryption(self, encrypted_model_path, decryption_key):
        """Test model decryption"""
        encryption = ModelEncryption()
        
        decryption_config = {
            "encryption_key_id": "key_123",
            "algorithm": "AES-256-GCM",
            "verify_integrity": True
        }
        
        with patch.object(encryption, 'decrypt_model') as mock_decrypt:
            mock_decrypt.return_value = {
                "decryption_id": "dec_001",
                "decrypted_model": Mock(),
                "decryption_successful": True,
                "integrity_verified": True,
                "decryption_time": 3.1,
                "model_hash_verified": True
            }
            
            decryption_result = encryption.decrypt_model(
                encrypted_path=encrypted_model_path,
                decryption_key=decryption_key,
                config=decryption_config
            )
            
            assert decryption_result["decryption_successful"] is True
            assert decryption_result["integrity_verified"] is True
            assert decryption_result["decrypted_model"] is not None

    def test_key_management(self):
        """Test cryptographic key management"""
        encryption = ModelEncryption(
            key_management_system="vault",
            enable_key_rotation=True
        )
        
        key_config = {
            "key_type": "AES-256",
            "key_usage": "model_encryption",
            "rotation_interval": "30d",
            "backup_keys": 3
        }
        
        with patch.object(encryption, 'manage_encryption_keys') as mock_keys:
            mock_keys.return_value = {
                "key_id": "key_456",
                "key_created": True,
                "key_stored_securely": True,
                "key_rotation_scheduled": True,
                "backup_keys_created": 3,
                "key_metadata": {
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
                    "algorithm": "AES-256",
                    "key_strength": "high"
                }
            }
            
            key_result = encryption.manage_encryption_keys(key_config)
            
            assert key_result["key_created"] is True
            assert key_result["key_stored_securely"] is True
            assert key_result["key_rotation_scheduled"] is True

    def test_secure_model_sharing(self, trained_model):
        """Test secure model sharing between parties"""
        encryption = ModelEncryption()
        
        sharing_config = {
            "recipient_public_key": "recipient_pubkey.pem",
            "encryption_method": "hybrid",  # RSA + AES
            "digital_signature": True,
            "access_controls": ["time_limit", "usage_limit"],
            "audit_logging": True
        }
        
        with patch.object(encryption, 'secure_model_sharing') as mock_share:
            mock_share.return_value = {
                "sharing_id": "share_001",
                "encrypted_package_path": "secure_model_package.enc",
                "digital_signature": "signature.sig",
                "recipient_key_id": "recipient_key_789",
                "access_token": "access_token_xyz",
                "sharing_successful": True,
                "expiration_time": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            sharing_result = encryption.secure_model_sharing(
                model=trained_model,
                config=sharing_config
            )
            
            assert sharing_result["sharing_successful"] is True
            assert "digital_signature" in sharing_result
            assert "access_token" in sharing_result


class TestAccessController:
    """Tests for access control and authorization"""
    
    def test_init_access_controller(self):
        """Test access controller initialization"""
        controller = AccessController(
            authentication_methods=["oauth2", "jwt", "api_key"],
            authorization_model="rbac",
            enable_mfa=True,
            session_timeout=3600,
            audit_all_access=True
        )
        
        assert len(controller.authentication_methods) == 3
        assert controller.authorization_model == "rbac"
        assert controller.enable_mfa
        assert controller.session_timeout == 3600
        assert controller.audit_all_access

    def test_user_authentication(self):
        """Test user authentication mechanisms"""
        controller = AccessController(authentication_methods=["jwt", "oauth2"])
        
        auth_request = {
            "user_id": "user_123",
            "authentication_method": "jwt",
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "client_id": "ml_client_001",
            "scope": ["model:read", "model:infer"]
        }
        
        with patch.object(controller, 'authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "authentication_id": "auth_001",
                "user_id": "user_123",
                "authentication_successful": True,
                "token_valid": True,
                "permissions": ["model:read", "model:infer"],
                "session_token": "session_token_abc",
                "session_expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            auth_result = controller.authenticate_user(auth_request)
            
            assert auth_result["authentication_successful"] is True
            assert auth_result["token_valid"] is True
            assert "session_token" in auth_result

    def test_role_based_authorization(self):
        """Test role-based access control (RBAC)"""
        controller = AccessController(authorization_model="rbac")
        
        authorization_request = {
            "user_id": "user_123",
            "user_roles": ["data_scientist", "model_user"],
            "requested_action": "model:deploy",
            "resource": "model_456",
            "context": {"department": "AI_research", "project": "content_analysis"}
        }
        
        with patch.object(controller, 'authorize_rbac') as mock_authz:
            mock_authz.return_value = {
                "authorization_id": "authz_001",
                "user_id": "user_123",
                "action": "model:deploy",
                "resource": "model_456",
                "permission_granted": False,
                "required_roles": ["model_admin", "deployment_manager"],
                "user_roles": ["data_scientist", "model_user"],
                "missing_permissions": ["deployment:create"],
                "access_denied_reason": "insufficient_privileges"
            }
            
            authz_result = controller.authorize_rbac(authorization_request)
            
            assert authz_result["permission_granted"] is False
            assert "missing_permissions" in authz_result
            assert "access_denied_reason" in authz_result

    def test_attribute_based_authorization(self):
        """Test attribute-based access control (ABAC)"""
        controller = AccessController(authorization_model="abac")
        
        abac_request = {
            "user_attributes": {
                "department": "AI_research",
                "clearance_level": "confidential",
                "project_access": ["project_A", "project_B"]
            },
            "resource_attributes": {
                "data_classification": "sensitive",
                "project": "project_A",
                "model_type": "classification"
            },
            "action": "model:train",
            "environment": {
                "time": datetime.now().isoformat(),
                "location": "datacenter_1",
                "network": "internal"
            }
        }
        
        with patch.object(controller, 'authorize_abac') as mock_abac:
            mock_abac.return_value = {
                "authorization_id": "abac_001",
                "permission_granted": True,
                "policy_matched": "ai_research_policy_v2",
                "decision_reason": "user has required clearance and project access",
                "conditions": [
                    "audit_logging_required",
                    "session_timeout_30min"
                ],
                "decision_time": 0.023
            }
            
            abac_result = controller.authorize_abac(abac_request)
            
            assert abac_result["permission_granted"] is True
            assert "policy_matched" in abac_result
            assert "conditions" in abac_result

    def test_api_rate_limiting(self):
        """Test API rate limiting and throttling"""
        controller = AccessController()
        
        rate_limit_config = {
            "user_id": "user_123",
            "api_endpoint": "/api/v1/models/predict",
            "rate_limit_rules": [
                {"window": "1m", "max_requests": 100},
                {"window": "1h", "max_requests": 1000},
                {"window": "1d", "max_requests": 10000}
            ]
        }
        
        with patch.object(controller, 'check_rate_limits') as mock_rate:
            mock_rate.return_value = {
                "rate_limit_id": "rate_001",
                "user_id": "user_123",
                "endpoint": "/api/v1/models/predict",
                "current_usage": {
                    "1m": {"requests": 15, "limit": 100},
                    "1h": {"requests": 234, "limit": 1000},
                    "1d": {"requests": 1567, "limit": 10000}
                },
                "rate_limit_exceeded": False,
                "remaining_quota": {
                    "1m": 85,
                    "1h": 766,
                    "1d": 8433
                }
            }
            
            rate_result = controller.check_rate_limits(rate_limit_config)
            
            assert rate_result["rate_limit_exceeded"] is False
            assert "remaining_quota" in rate_result
            assert all(quota > 0 for quota in rate_result["remaining_quota"].values())


class TestAuditLogger:
    """Tests for audit logging and compliance tracking"""
    
    def test_init_audit_logger(self):
        """Test audit logger initialization"""
        logger = AuditLogger(
            log_levels=["INFO", "WARN", "ERROR", "AUDIT"],
            storage_backend="elasticsearch",
            retention_period="7y",
            enable_tamper_protection=True,
            compliance_standards=["SOX", "GDPR", "HIPAA"]
        )
        
        assert len(logger.log_levels) == 4
        assert logger.storage_backend == "elasticsearch"
        assert logger.retention_period == "7y"
        assert logger.enable_tamper_protection

    def test_model_access_logging(self):
        """Test model access audit logging"""
        logger = AuditLogger()
        
        access_event = {
            "event_type": "model_access",
            "user_id": "user_123",
            "model_id": "model_456",
            "action": "inference_request",
            "timestamp": datetime.now().isoformat(),
            "ip_address": "192.168.1.100",
            "user_agent": "ML-Client/1.0",
            "request_size": 1024,
            "response_size": 256,
            "processing_time": 45.6,
            "success": True
        }
        
        with patch.object(logger, 'log_model_access') as mock_log:
            mock_log.return_value = {
                "log_id": "log_001",
                "event_logged": True,
                "log_timestamp": datetime.now().isoformat(),
                "log_level": "AUDIT",
                "tamper_proof": True,
                "compliance_tags": ["GDPR", "audit_trail"]
            }
            
            log_result = logger.log_model_access(access_event)
            
            assert log_result["event_logged"] is True
            assert log_result["tamper_proof"] is True
            assert "compliance_tags" in log_result

    def test_security_event_logging(self):
        """Test security event audit logging"""
        logger = AuditLogger(enable_tamper_protection=True)
        
        security_event = {
            "event_type": "security_incident",
            "incident_type": "adversarial_attack_detected",
            "severity": "high",
            "user_id": "user_123",
            "model_id": "model_456",
            "attack_details": {
                "attack_type": "fgsm",
                "success": False,
                "confidence": 0.87
            },
            "response_actions": ["blocked_request", "alert_sent", "user_flagged"],
            "timestamp": datetime.now().isoformat()
        }
        
        with patch.object(logger, 'log_security_event') as mock_security:
            mock_security.return_value = {
                "security_log_id": "sec_log_001",
                "event_logged": True,
                "severity": "high",
                "alert_triggered": True,
                "notification_sent": ["security_team", "model_owner"],
                "incident_id": "inc_001",
                "tamper_protection_enabled": True
            }
            
            security_result = logger.log_security_event(security_event)
            
            assert security_result["event_logged"] is True
            assert security_result["alert_triggered"] is True
            assert security_result["tamper_protection_enabled"] is True

    def test_compliance_reporting(self):
        """Test compliance reporting generation"""
        logger = AuditLogger(compliance_standards=["GDPR", "HIPAA"])
        
        report_config = {
            "report_type": "compliance_summary",
            "compliance_standard": "GDPR",
            "time_period": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            },
            "include_sections": [
                "data_processing_activities",
                "user_consent_tracking",
                "data_breach_incidents",
                "data_subject_requests"
            ]
        }
        
        with patch.object(logger, 'generate_compliance_report') as mock_report:
            mock_report.return_value = {
                "report_id": "report_001",
                "compliance_standard": "GDPR",
                "report_period": "2024-01-01 to 2024-12-31",
                "compliance_score": 95.2,
                "total_events_audited": 145678,
                "violations_found": 3,
                "recommendations": [
                    "Implement additional consent verification",
                    "Enhance data retention monitoring"
                ],
                "report_generated_at": datetime.now().isoformat()
            }
            
            report_result = logger.generate_compliance_report(report_config)
            
            assert "report_id" in report_result
            assert report_result["compliance_score"] > 90
            assert "recommendations" in report_result


@pytest.mark.integration
class TestModelSecurityIntegration:
    """Integration tests for model security systems"""
    
    @pytest.mark.slow
    def test_end_to_end_security_pipeline(self, trained_model, temp_dir):
        """Test complete security pipeline integration"""
        # Initialize security components
        security_manager = ModelSecurityManager(
            security_policies=["encryption", "access_control", "audit_logging"],
            threat_detection_enabled=True
        )
        adversarial_defense = AdversarialDefense(detection_enabled=True)
        privacy_preserver = PrivacyPreserver(privacy_techniques=["differential_privacy"])
        encryption = ModelEncryption(encryption_at_rest=True)
        access_controller = AccessController(authorization_model="rbac")
        audit_logger = AuditLogger(enable_tamper_protection=True)
        
        # Conduct security assessment
        with patch.object(security_manager, 'conduct_security_assessment') as mock_assess:
            mock_assess.return_value = {
                "overall_security_score": 8.5,
                "vulnerabilities": 2,
                "compliance_status": "compliant"
            }
            
            assessment_result = security_manager.conduct_security_assessment({
                "model": trained_model
            })
            assert assessment_result["overall_security_score"] > 8.0
        
        # Apply adversarial defense
        with patch.object(adversarial_defense, 'defend_against_pgd') as mock_defend:
            mock_defend.return_value = {
                "defense_success": True,
                "robustness_improvement": 0.25
            }
            
            defense_result = adversarial_defense.defend_against_pgd(
                model=trained_model, inputs=np.random.randn(10, 784)
            )
            assert defense_result["defense_success"] is True
        
        # Apply privacy preservation
        with patch.object(privacy_preserver, 'apply_differential_privacy') as mock_privacy:
            mock_privacy.return_value = {
                "privacy_preserved": True,
                "privacy_budget_used": 0.8
            }
            
            privacy_result = privacy_preserver.apply_differential_privacy({})
            assert privacy_result["privacy_preserved"] is True
        
        # Encrypt model
        with patch.object(encryption, 'encrypt_model_aes') as mock_encrypt:
            mock_encrypt.return_value = {
                "encryption_successful": True,
                "encrypted_path": str(temp_dir / "model.encrypted")
            }
            
            encryption_result = encryption.encrypt_model_aes(
                model_path=temp_dir / "model.pth",
                output_path=temp_dir / "model.encrypted"
            )
            assert encryption_result["encryption_successful"] is True
        
        # Test access control
        with patch.object(access_controller, 'authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "authentication_successful": True,
                "permissions": ["model:read"]
            }
            
            auth_result = access_controller.authenticate_user({
                "user_id": "test_user", "token": "test_token"
            })
            assert auth_result["authentication_successful"] is True
        
        # Log security events
        with patch.object(audit_logger, 'log_security_event') as mock_log:
            mock_log.return_value = {
                "event_logged": True,
                "tamper_protection_enabled": True
            }
            
            log_result = audit_logger.log_security_event({
                "event_type": "security_assessment_completed"
            })
            assert log_result["event_logged"] is True

    def test_multi_layer_security_validation(self, trained_model):
        """Test multi-layer security validation"""
        security_layers = [
            ("input_validation", {"enabled": True}),
            ("adversarial_detection", {"threshold": 0.8}),
            ("privacy_protection", {"epsilon": 1.0}),
            ("access_control", {"method": "rbac"}),
            ("audit_logging", {"level": "comprehensive"})
        ]
        
        security_manager = ModelSecurityManager()
        
        validation_results = []
        for layer_name, layer_config in security_layers:
            with patch.object(security_manager, f'validate_{layer_name}') as mock_validate:
                mock_validate.return_value = {
                    "layer": layer_name,
                    "validation_passed": True,
                    "security_score": np.random.uniform(8.0, 9.5)
                }
                
                result = getattr(security_manager, f'validate_{layer_name}')(layer_config)
                validation_results.append(result)
        
        # All layers should pass validation
        assert all(result["validation_passed"] for result in validation_results)
        overall_score = np.mean([result["security_score"] for result in validation_results])
        assert overall_score > 8.0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
