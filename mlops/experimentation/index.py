"""
Experimentation Module - Entry Point
Enterprise A/B testing and experimentation platform for MLOps

This module provides comprehensive experimentation capabilities for:
- Model A/B testing and comparison
- Statistical hypothesis validation
- Multivariate testing frameworks
- Personalization engines
- Experiment orchestration and reporting

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .experiment_orchestrator import ExperimentOrchestrator
from .a_b_testing.ab_engine import ABTestingEngine
from .hypothesis_validator import HypothesisValidator
from .statistical_engine import StatisticalEngine
from .cohort_analyzer import CohortAnalyzer

logger = logging.getLogger(__name__)

class ExperimentationManager:
    """
    Central manager for all experimentation activities
    Coordinates A/B testing, statistical validation, and experiment orchestration
    """
    
    def __init__(self):
        self.orchestrator = ExperimentOrchestrator()
        self.ab_engine = ABTestingEngine()
        self.hypothesis_validator = HypothesisValidator()
        self.statistical_engine = StatisticalEngine()
        self.cohort_analyzer = CohortAnalyzer()
        
    async def setup_model_experiment(
        self,
        model_a_id: str,
        model_b_id: str,
        traffic_split: float = 0.5,
        experiment_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Set up A/B test for model comparison
        
        Args:
            model_a_id: Control model identifier
            model_b_id: Treatment model identifier  
            traffic_split: Percentage of traffic for model B
            experiment_config: Additional configuration
            
        Returns:
            experiment_id: Unique experiment identifier
        """
        try:
            logger.info(f"Setting up model experiment: {model_a_id} vs {model_b_id}")
            
            # Create experiment configuration
            experiment_id = await self.orchestrator.create_experiment(
                name=f"model_comparison_{model_a_id}_{model_b_id}",
                model_a=model_a_id,
                model_b=model_b_id,
                traffic_split=traffic_split,
                config=experiment_config or {}
            )
            
            # Initialize A/B testing
            await self.ab_engine.initialize_ab_test(
                experiment_id=experiment_id,
                control_model=model_a_id,
                treatment_model=model_b_id,
                traffic_allocation=traffic_split
            )
            
            logger.info(f"Model experiment created: {experiment_id}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to setup model experiment: {e}")
            raise
    
    async def validate_experiment_results(
        self,
        experiment_id: str,
        minimum_sample_size: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Validate experiment results with statistical significance
        
        Args:
            experiment_id: Experiment to validate
            minimum_sample_size: Minimum samples required
            confidence_level: Statistical confidence level
            
        Returns:
            validation_results: Statistical validation summary
        """
        try:
            logger.info(f"Validating experiment results: {experiment_id}")
            
            # Get experiment metrics
            metrics = await self.ab_engine.get_experiment_metrics(experiment_id)
            
            # Check sample size adequacy
            sample_size_valid = await self.statistical_engine.validate_sample_size(
                metrics, minimum_sample_size
            )
            
            if not sample_size_valid:
                return {
                    "status": "insufficient_data",
                    "message": f"Need minimum {minimum_sample_size} samples",
                    "current_samples": metrics.get("total_samples", 0)
                }
            
            # Perform significance testing
            significance_results = await self.hypothesis_validator.test_significance(
                control_metrics=metrics["control"],
                treatment_metrics=metrics["treatment"],
                confidence_level=confidence_level
            )
            
            # Calculate effect size and practical significance
            effect_size = await self.statistical_engine.calculate_effect_size(
                metrics["control"], metrics["treatment"]
            )
            
            validation_results = {
                "experiment_id": experiment_id,
                "statistical_significance": significance_results,
                "effect_size": effect_size,
                "confidence_level": confidence_level,
                "recommendation": await self._generate_recommendation(
                    significance_results, effect_size
                ),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Experiment validation completed: {experiment_id}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate experiment: {e}")
            raise
    
    async def _generate_recommendation(
        self,
        significance_results: Dict[str, Any],
        effect_size: Dict[str, Any]
    ) -> str:
        """Generate recommendation based on statistical results"""
        
        if significance_results.get("is_significant", False):
            if effect_size.get("magnitude") == "large":
                return "DEPLOY - Strong statistical and practical significance"
            elif effect_size.get("magnitude") == "medium":
                return "DEPLOY - Statistically significant with moderate effect"
            else:
                return "CONTINUE - Significant but small effect, consider longer test"
        else:
            return "NO CHANGE - No statistical significance detected"

# Initialize global experimentation manager
experimentation_manager = ExperimentationManager()

async def main():
    """Main entry point for experimentation module"""
    logger.info("Experimentation module initialized")
    
    # Example usage
    try:
        # Setup example model experiment
        experiment_id = await experimentation_manager.setup_model_experiment(
            model_a_id="model_v1.0",
            model_b_id="model_v1.1",
            traffic_split=0.1  # 10% traffic to new model
        )
        
        logger.info(f"Created experiment: {experiment_id}")
        
    except Exception as e:
        logger.error(f"Experimentation setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())