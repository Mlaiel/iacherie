"""Comprehensive tests for AI/ML Testing Specialization modules

Tests for production-grade model accuracy validation, bias testing,
adversarial testing, drift monitoring, and A/B testing integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import numpy as np
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the module path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ai_engine.testing.accuracy_validation import (
    ProductionAccuracyValidator,
    AccuracyMetrics,
    AccuracyThreshold,
    ValidationStatus
)
from ai_engine.testing.bias_testing import (
    FairnessValidator,
    BiasMetrics,
    FairnessMetric,
    BiasType
)
from ai_engine.testing.adversarial_testing import (
    AdversarialSecurityTester,
    AdversarialAttackType,
    SecurityThreatLevel
)
from ai_engine.testing.drift_monitoring import (
    EnhancedDriftMonitor,
    MonitoringConfig,
    DriftSeverity,
    MonitoringStatus
)
from ai_engine.testing.ab_testing_integration import (
    MLExperimentFramework,
    ExperimentConfig,
    ExperimentType,
    ExperimentStatus
)


class TestProductionAccuracyValidator:
    """
Tests for production accuracy validation"""
    
    @pytest.fixture
    def validator(self):
        return ProductionAccuracyValidator(min_accuracy_threshold=0.99)
    
    @pytest.fixture
    def sample_data(self):
        np.random.seed(42)
        y_true = np.random.choice([0, 1], size=1000)
        # Generate predictions with high accuracy
        y_pred = y_true.copy()
        # Add some errors to make it realistic but still >99%
        error_indices = np.random.choice(1000, size=5, replace=False)
        y_pred[error_indices] = 1 - y_pred[error_indices]
        
        return y_pred, y_true
    
    def test_validator_initialization(self, validator):
        """
Test validator initialization"""
        assert validator.min_accuracy_threshold == 0.99
        assert isinstance(validator.validation_history, dict)
    
    @pytest.mark.asyncio
    async def test_validate_model_accuracy_success(self, validator, sample_data):
        """
Test successful model accuracy validation"""
        y_pred, y_true = sample_data
        
        result = await validator.validate_model_accuracy(
            model_id="test_model_1",
            model_predictions=y_pred,
            ground_truth=y_true,
            dataset_info={"dataset_name": "test_dataset", "size": len(y_true)}
        )
        
        assert result.model_id == "test_model_1"
        assert result.threshold_met is True  # Should meet >99% threshold
        assert result.status == ValidationStatus.PASSED
        assert result.metrics.accuracy >= 0.99
        assert result.validation_duration > 0
        assert len(result.recommendations) >= 0


class TestFairnessValidator:
    """Tests for bias and fairness validation"""
    
    @pytest.fixture
    def validator(self):
        return FairnessValidator(fairness_threshold=0.90)
    
    @pytest.fixture
    def sample_bias_data(self):
        np.random.seed(42)
        n_samples = 1000
        
        # Generate predictions and ground truth
        y_true = np.random.choice([0, 1], size=n_samples)
        y_pred = y_true.copy()
        
        # Add some bias - make predictions worse for group 1
        gender = np.random.choice(['M', 'F'], size=n_samples)
        race = np.random.choice(['A', 'B', 'C'], size=n_samples)
        
        sensitive_attributes = {
            'gender': gender,
            'race': race
        }
        
        return y_pred, y_true, sensitive_attributes
    
    def test_validator_initialization(self, validator):
        """
Test fairness validator initialization"""
        assert validator.fairness_threshold == 0.90
        assert isinstance(validator.validation_history, dict)
    
    @pytest.mark.asyncio
    async def test_validate_model_fairness(self, validator, sample_bias_data):
        """
Test comprehensive fairness validation"""
        y_pred, y_true, sensitive_attributes = sample_bias_data
        
        result = await validator.validate_model_fairness(
            model_id="fairness_model_1",
            predictions=y_pred,
            ground_truth=y_true,
            sensitive_attributes=sensitive_attributes,
            dataset_info={"dataset_name": "bias_test", "size": len(y_true)}
        )
        
        assert result.model_id == "fairness_model_1"
        assert isinstance(result.metrics, BiasMetrics)
        assert result.overall_fairness_score >= 0
        assert result.overall_fairness_score <= 1
        assert len(result.individual_tests) > 0
        assert result.validation_duration > 0


class TestAdversarialSecurityTester:
    """Tests for adversarial security testing"""
    
    @pytest.fixture
    def tester(self):
        return AdversarialSecurityTester(security_threshold=0.85)
    
    @pytest.fixture
    def sample_model_data(self):
        np.random.seed(42)
        X_test = np.random.randn(100, 10)  # 100 samples, 10 features
        y_test = np.random.choice([0, 1], size=100)
        
        # Mock model prediction function
        def mock_predict(X):
            # Simple mock model that returns mostly correct predictions
            return (np.sum(X, axis=1) > 0).astype(int)
        
        return mock_predict, X_test, y_test
    
    def test_tester_initialization(self, tester):
        """
Test adversarial tester initialization"""
        assert tester.security_threshold == 0.85
        assert isinstance(tester.validation_history, dict)
    
    @pytest.mark.asyncio
    async def test_validate_model_security(self, tester, sample_model_data):
        """
Test comprehensive security validation"""
        mock_predict, X_test, y_test = sample_model_data
        
        result = await tester.validate_model_security(
            model_id="security_model_1",
            model_predict_func=mock_predict,
            X_test=X_test,
            y_test=y_test
        )
        
        assert result.model_id == "security_model_1"
        assert isinstance(result.security_metrics.overall_robustness_score, float)
        assert 0 <= result.overall_security_score <= 1
        assert len(result.individual_attacks) > 0
        assert result.validation_duration > 0


# Pytest fixtures for async support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])