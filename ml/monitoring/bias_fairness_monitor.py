#!/usr/bin/env python3
"""
Bias and Fairness Monitor for Ainflue ML Models
Continuous bias and fairness monitoring across creator demographics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BiasMetrics:
    """Bias metrics for fairness evaluation"""
    demographic_parity_ratio: float
    equal_opportunity_ratio: float
    predictive_parity_ratio: float
    calibration_score: float
    individual_fairness_score: float
    group_fairness_score: float
    timestamp: datetime
    creator_type: str
    demographic_group: str

@dataclass
class FairnessReport:
    """Comprehensive fairness evaluation report"""
    overall_fairness_score: float
    bias_metrics: List[BiasMetrics]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_status: str
    timestamp: datetime

class FairnessMetricCalculator(ABC):
    """Abstract base class for fairness metric calculations"""
    
    @abstractmethod
    async def calculate_metric(self, 
                              predictions: np.ndarray,
                              labels: np.ndarray,
                              protected_attributes: np.ndarray) -> float:
        """Calculate specific fairness metric"""
        pass

class DemographicParityCalculator(FairnessMetricCalculator):
    """Calculate demographic parity ratio"""
    
    async def calculate_metric(self, 
                              predictions: np.ndarray,
                              labels: np.ndarray,
                              protected_attributes: np.ndarray) -> float:
        """
        Demographic parity: P(Y=1|A=0) = P(Y=1|A=1)
        Returns ratio between groups
        """
        try:
            # Group 0 (privileged) and Group 1 (unprivileged)
            group_0_idx = protected_attributes == 0
            group_1_idx = protected_attributes == 1
            
            if not np.any(group_0_idx) or not np.any(group_1_idx):
                return 1.0  # No bias if only one group
            
            positive_rate_0 = np.mean(predictions[group_0_idx])
            positive_rate_1 = np.mean(predictions[group_1_idx])
            
            if positive_rate_0 == 0:
                return 1.0 if positive_rate_1 == 0 else 0.0
            
            return min(positive_rate_1 / positive_rate_0, positive_rate_0 / positive_rate_1)
            
        except Exception as e:
            logger.error(f"Error calculating demographic parity: {e}")
            return 0.0

class EqualOpportunityCalculator(FairnessMetricCalculator):
    """Calculate equal opportunity ratio"""
    
    async def calculate_metric(self, 
                              predictions: np.ndarray,
                              labels: np.ndarray,
                              protected_attributes: np.ndarray) -> float:
        """
        Equal opportunity: P(Y=1|A=0,D=1) = P(Y=1|A=1,D=1)
        True positive rates should be equal across groups
        """
        try:
            group_0_idx = (protected_attributes == 0) & (labels == 1)
            group_1_idx = (protected_attributes == 1) & (labels == 1)
            
            if not np.any(group_0_idx) or not np.any(group_1_idx):
                return 1.0
            
            tpr_0 = np.mean(predictions[group_0_idx])
            tpr_1 = np.mean(predictions[group_1_idx])
            
            if tpr_0 == 0:
                return 1.0 if tpr_1 == 0 else 0.0
            
            return min(tpr_1 / tpr_0, tpr_0 / tpr_1)
            
        except Exception as e:
            logger.error(f"Error calculating equal opportunity: {e}")
            return 0.0

class PredictiveParityCalculator(FairnessMetricCalculator):
    """Calculate predictive parity ratio"""
    
    async def calculate_metric(self, 
                              predictions: np.ndarray,
                              labels: np.ndarray,
                              protected_attributes: np.ndarray) -> float:
        """
        Predictive parity: P(D=1|Y=1,A=0) = P(D=1|Y=1,A=1)
        Precision should be equal across groups
        """
        try:
            group_0_pred_pos = (protected_attributes == 0) & (predictions == 1)
            group_1_pred_pos = (protected_attributes == 1) & (predictions == 1)
            
            if not np.any(group_0_pred_pos) or not np.any(group_1_pred_pos):
                return 1.0
            
            precision_0 = np.mean(labels[group_0_pred_pos])
            precision_1 = np.mean(labels[group_1_pred_pos])
            
            if precision_0 == 0:
                return 1.0 if precision_1 == 0 else 0.0
            
            return min(precision_1 / precision_0, precision_0 / precision_1)
            
        except Exception as e:
            logger.error(f"Error calculating predictive parity: {e}")
            return 0.0

class BiasFairnessMonitor:
    """
    Enterprise bias and fairness monitoring system for Ainflue ML models
    
    🎖️ EXPERT MULTI-ROLE IMPLEMENTATION:
    - Lead Dev IA: Orchestration of bias detection across all creator types
    - ML Engineer: Advanced fairness algorithms and statistical validation
    - Security: Compliance monitoring and ethical AI governance
    - DBA: Bias metrics storage and historical tracking
    - Audio Engineer: Creator-specific bias detection for musicians
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize bias fairness monitor"""
        self.config = config or {}
        self.fairness_calculators = {
            'demographic_parity': DemographicParityCalculator(),
            'equal_opportunity': EqualOpportunityCalculator(),
            'predictive_parity': PredictiveParityCalculator()
        }
        
        # Creator-specific bias thresholds
        self.creator_thresholds = {
            'musician': {'min_fairness': 0.8, 'max_bias': 0.2},
            'blogger': {'min_fairness': 0.85, 'max_bias': 0.15},
            'photographer': {'min_fairness': 0.8, 'max_bias': 0.2},
            'influencer': {'min_fairness': 0.9, 'max_bias': 0.1},
            'comedian': {'min_fairness': 0.75, 'max_bias': 0.25}
        }
        
        # Protected attributes mapping
        self.protected_attributes = [
            'gender', 'age_group', 'location', 'creator_type', 
            'experience_level', 'follower_count_tier'
        ]
        
        logger.info("✅ Bias Fairness Monitor initialized")
    
    async def monitor_model_bias(self, 
                                model_id: str,
                                predictions: np.ndarray,
                                labels: np.ndarray,
                                metadata: Dict[str, Any]) -> FairnessReport:
        """
        Monitor model for bias and fairness violations
        
        🎖️ LEAD DEV IA: Orchestration of comprehensive bias monitoring
        """
        try:
            logger.info(f"🔍 Monitoring bias for model {model_id}")
            
            # Extract creator demographics
            creator_type = metadata.get('creator_type', 'unknown')
            demographics = self._extract_demographics(metadata)
            
            # Calculate bias metrics for each protected attribute
            bias_metrics = []
            for attr_name, attr_values in demographics.items():
                if len(np.unique(attr_values)) > 1:  # Only if multiple groups exist
                    metrics = await self._calculate_bias_metrics(
                        predictions, labels, attr_values, creator_type, attr_name
                    )
                    bias_metrics.append(metrics)
            
            # Generate fairness report
            fairness_report = await self._generate_fairness_report(
                model_id, bias_metrics, creator_type
            )
            
            # Store metrics for historical tracking
            await self._store_bias_metrics(model_id, fairness_report)
            
            # Trigger alerts if violations detected
            if fairness_report.risk_level in ['HIGH', 'CRITICAL']:
                await self._trigger_bias_alert(model_id, fairness_report)
            
            logger.info(f"✅ Bias monitoring complete for {model_id}")
            return fairness_report
            
        except Exception as e:
            logger.error(f"❌ Error monitoring model bias: {e}")
            raise
    
    async def _calculate_bias_metrics(self, 
                                     predictions: np.ndarray,
                                     labels: np.ndarray,
                                     protected_attr: np.ndarray,
                                     creator_type: str,
                                     attr_name: str) -> BiasMetrics:
        """
        Calculate comprehensive bias metrics
        
        🔬 ML ENGINEER: Advanced fairness algorithms implementation
        """
        try:
            # Calculate fairness metrics
            demographic_parity = await self.fairness_calculators['demographic_parity'].calculate_metric(
                predictions, labels, protected_attr
            )
            
            equal_opportunity = await self.fairness_calculators['equal_opportunity'].calculate_metric(
                predictions, labels, protected_attr
            )
            
            predictive_parity = await self.fairness_calculators['predictive_parity'].calculate_metric(
                predictions, labels, protected_attr
            )
            
            # Calculate calibration score
            calibration_score = await self._calculate_calibration(
                predictions, labels, protected_attr
            )
            
            # Calculate individual and group fairness
            individual_fairness = await self._calculate_individual_fairness(
                predictions, protected_attr
            )
            
            group_fairness = (demographic_parity + equal_opportunity + predictive_parity) / 3
            
            return BiasMetrics(
                demographic_parity_ratio=demographic_parity,
                equal_opportunity_ratio=equal_opportunity,
                predictive_parity_ratio=predictive_parity,
                calibration_score=calibration_score,
                individual_fairness_score=individual_fairness,
                group_fairness_score=group_fairness,
                timestamp=datetime.now(),
                creator_type=creator_type,
                demographic_group=attr_name
            )
            
        except Exception as e:
            logger.error(f"Error calculating bias metrics: {e}")
            raise
    
    async def _calculate_calibration(self, 
                                   predictions: np.ndarray,
                                   labels: np.ndarray,
                                   protected_attr: np.ndarray) -> float:
        """
        Calculate calibration score across demographic groups
        
        🔬 ML ENGINEER: Statistical calibration analysis
        """
        try:
            calibration_scores = []
            
            for group in np.unique(protected_attr):
                group_idx = protected_attr == group
                if np.sum(group_idx) < 10:  # Skip small groups
                    continue
                
                group_pred = predictions[group_idx]
                group_labels = labels[group_idx]
                
                # Bin predictions and calculate calibration
                bins = np.linspace(0, 1, 11)
                bin_boundaries = list(zip(bins[:-1], bins[1:]))
                
                calibration_error = 0
                total_samples = 0
                
                for bin_lower, bin_upper in bin_boundaries:
                    in_bin = (group_pred >= bin_lower) & (group_pred < bin_upper)
                    if np.sum(in_bin) == 0:
                        continue
                    
                    bin_accuracy = np.mean(group_labels[in_bin])
                    bin_confidence = np.mean(group_pred[in_bin])
                    bin_size = np.sum(in_bin)
                    
                    calibration_error += bin_size * abs(bin_accuracy - bin_confidence)
                    total_samples += bin_size
                
                if total_samples > 0:
                    group_calibration = 1 - (calibration_error / total_samples)
                    calibration_scores.append(max(0, group_calibration))
            
            return np.mean(calibration_scores) if calibration_scores else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating calibration: {e}")
            return 0.0
    
    async def _calculate_individual_fairness(self, 
                                           predictions: np.ndarray,
                                           protected_attr: np.ndarray) -> float:
        """
        Calculate individual fairness score
        
        🔬 ML ENGINEER: Individual fairness metric implementation
        """
        try:
            # Simplified individual fairness: variance in predictions within groups
            fairness_scores = []
            
            for group in np.unique(protected_attr):
                group_idx = protected_attr == group
                group_pred = predictions[group_idx]
                
                if len(group_pred) > 1:
                    # Lower variance indicates higher individual fairness
                    variance = np.var(group_pred)
                    fairness_score = 1 / (1 + variance)  # Normalize to [0,1]
                    fairness_scores.append(fairness_score)
            
            return np.mean(fairness_scores) if fairness_scores else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating individual fairness: {e}")
            return 0.0
    
    def _extract_demographics(self, metadata: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Extract demographic information from metadata
        
        🗄️ DBA: Data extraction and demographic categorization
        """
        demographics = {}
        
        try:
            # Simulate demographic data (in production, this would come from real data)
            n_samples = metadata.get('n_samples', 1000)
            
            demographics['gender'] = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])
            demographics['age_group'] = np.random.choice([0, 1, 2], size=n_samples, p=[0.3, 0.5, 0.2])
            demographics['location'] = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
            demographics['experience_level'] = np.random.choice([0, 1], size=n_samples, p=[0.4, 0.6])
            
            # Creator-specific demographics
            creator_type = metadata.get('creator_type', 'musician')
            if creator_type == 'musician':
                demographics['genre_preference'] = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])
            elif creator_type == 'blogger':
                demographics['niche_category'] = np.random.choice([0, 1], size=n_samples, p=[0.5, 0.5])
            elif creator_type == 'photographer':
                demographics['style_preference'] = np.random.choice([0, 1], size=n_samples, p=[0.4, 0.6])
                
        except Exception as e:
            logger.error(f"Error extracting demographics: {e}")
            demographics['default'] = np.zeros(metadata.get('n_samples', 1000))
        
        return demographics
    
    async def _generate_fairness_report(self, 
                                       model_id: str,
                                       bias_metrics: List[BiasMetrics],
                                       creator_type: str) -> FairnessReport:
        """
        Generate comprehensive fairness evaluation report
        
        🔐 SECURITY: Compliance assessment and risk evaluation
        """
        try:
            thresholds = self.creator_thresholds.get(creator_type, 
                                                   self.creator_thresholds['musician'])
            
            # Calculate overall fairness score
            fairness_scores = [m.group_fairness_score for m in bias_metrics]
            overall_fairness = np.mean(fairness_scores) if fairness_scores else 1.0
            
            # Identify violations
            violations = []
            for metric in bias_metrics:
                if metric.group_fairness_score < thresholds['min_fairness']:
                    violations.append({
                        'type': 'fairness_violation',
                        'metric': 'group_fairness',
                        'value': metric.group_fairness_score,
                        'threshold': thresholds['min_fairness'],
                        'demographic_group': metric.demographic_group,
                        'severity': 'HIGH' if metric.group_fairness_score < 0.5 else 'MEDIUM'
                    })
                
                # Check individual fairness metrics
                if metric.demographic_parity_ratio < thresholds['min_fairness']:
                    violations.append({
                        'type': 'demographic_bias',
                        'metric': 'demographic_parity',
                        'value': metric.demographic_parity_ratio,
                        'threshold': thresholds['min_fairness'],
                        'demographic_group': metric.demographic_group,
                        'severity': 'HIGH'
                    })
            
            # Determine risk level
            if not violations:
                risk_level = 'LOW'
            elif len(violations) < 3:
                risk_level = 'MEDIUM'
            elif any(v['severity'] == 'HIGH' for v in violations):
                risk_level = 'HIGH'
            else:
                risk_level = 'CRITICAL'
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(violations, creator_type)
            
            # Determine compliance status
            compliance_status = 'COMPLIANT' if risk_level in ['LOW', 'MEDIUM'] else 'NON_COMPLIANT'
            
            return FairnessReport(
                overall_fairness_score=overall_fairness,
                bias_metrics=bias_metrics,
                violations=violations,
                recommendations=recommendations,
                risk_level=risk_level,
                compliance_status=compliance_status,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating fairness report: {e}")
            raise
    
    async def _generate_recommendations(self, 
                                       violations: List[Dict[str, Any]],
                                       creator_type: str) -> List[str]:
        """
        Generate actionable recommendations for bias mitigation
        
        🤖 IA PROMPT ENGINEER: AI-powered recommendation generation
        """
        recommendations = []
        
        try:
            if not violations:
                recommendations.append("✅ Model demonstrates good fairness across demographic groups")
                return recommendations
            
            # General recommendations
            if any(v['metric'] == 'demographic_parity' for v in violations):
                recommendations.append(
                    "🎯 Implement demographic parity constraints during model training"
                )
                recommendations.append(
                    "📊 Balance training data across demographic groups"
                )
            
            if any(v['metric'] == 'group_fairness' for v in violations):
                recommendations.append(
                    "⚖️ Apply fairness-aware machine learning techniques (e.g., fairness constraints)"
                )
                recommendations.append(
                    "🔄 Consider post-processing fairness corrections"
                )
            
            # Creator-specific recommendations
            if creator_type == 'musician':
                recommendations.append(
                    "🎵 Ensure audio feature extraction is unbiased across musical genres and demographics"
                )
            elif creator_type == 'blogger':
                recommendations.append(
                    "📝 Review content classification algorithms for demographic bias in writing styles"
                )
            elif creator_type == 'photographer':
                recommendations.append(
                    "📸 Audit image recognition models for bias in aesthetic preferences"
                )
            
            # Severity-based recommendations
            high_severity_violations = [v for v in violations if v['severity'] == 'HIGH']
            if high_severity_violations:
                recommendations.append(
                    "🚨 URGENT: Immediate model retraining required due to high-severity bias violations"
                )
                recommendations.append(
                    "🛡️ Implement additional fairness monitoring and alerts"
                )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("⚠️ Error generating recommendations - manual review required")
        
        return recommendations
    
    async def _store_bias_metrics(self, model_id: str, report: FairnessReport):
        """
        Store bias metrics for historical tracking
        
        🗄️ DBA: Bias metrics storage and governance
        """
        try:
            # In production, this would store to a database
            logger.info(f"📊 Storing bias metrics for model {model_id}")
            logger.info(f"   Overall fairness: {report.overall_fairness_score:.3f}")
            logger.info(f"   Risk level: {report.risk_level}")
            logger.info(f"   Violations: {len(report.violations)}")
            
        except Exception as e:
            logger.error(f"Error storing bias metrics: {e}")
    
    async def _trigger_bias_alert(self, model_id: str, report: FairnessReport):
        """
        Trigger alerts for bias violations
        
        🛡️ BACKEND SENIOR: Alert infrastructure integration
        """
        try:
            logger.warning(f"🚨 BIAS ALERT for model {model_id}")
            logger.warning(f"   Risk level: {report.risk_level}")
            logger.warning(f"   Compliance: {report.compliance_status}")
            logger.warning(f"   Violations: {len(report.violations)}")
            
            # In production, integrate with alerting systems
            
        except Exception as e:
            logger.error(f"Error triggering bias alert: {e}")
    
    async def get_historical_bias_trends(self, 
                                        model_id: str,
                                        time_range: timedelta = timedelta(days=30)) -> Dict[str, Any]:
        """
        Get historical bias trend analysis
        
        📈 ANALYTICS: Bias trend analysis and reporting
        """
        try:
            logger.info(f"📈 Analyzing bias trends for model {model_id}")
            
            # Simulate historical trend data
            end_date = datetime.now()
            start_date = end_date - time_range
            
            # Generate simulated trend data
            trend_data = {
                'model_id': model_id,
                'time_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'fairness_trend': {
                    'average_score': 0.82,
                    'trend_direction': 'improving',  # improving, declining, stable
                    'variance': 0.05
                },
                'violation_frequency': {
                    'total_violations': 3,
                    'high_severity': 1,
                    'medium_severity': 2
                },
                'demographic_insights': {
                    'most_biased_group': 'age_group',
                    'best_performing_group': 'location',
                    'recommendations': [
                        "Focus bias mitigation efforts on age group disparities",
                        "Maintain current practices for location-based fairness"
                    ]
                }
            }
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error analyzing bias trends: {e}")
            raise

# Creator-specific bias monitoring configurations
CREATOR_BIAS_CONFIGS = {
    'musician': {
        'protected_attributes': ['gender', 'genre', 'location', 'experience_level'],
        'fairness_threshold': 0.8,
        'monitoring_frequency': 'daily',
        'special_considerations': ['audio_quality_bias', 'genre_preference_bias']
    },
    'blogger': {
        'protected_attributes': ['gender', 'age_group', 'language', 'niche'],
        'fairness_threshold': 0.85,
        'monitoring_frequency': 'daily', 
        'special_considerations': ['writing_style_bias', 'topic_preference_bias']
    },
    'photographer': {
        'protected_attributes': ['gender', 'style', 'equipment_level', 'location'],
        'fairness_threshold': 0.8,
        'monitoring_frequency': 'weekly',
        'special_considerations': ['aesthetic_bias', 'equipment_bias']
    },
    'influencer': {
        'protected_attributes': ['gender', 'age_group', 'follower_count', 'platform'],
        'fairness_threshold': 0.9,
        'monitoring_frequency': 'daily',
        'special_considerations': ['engagement_bias', 'platform_algorithm_bias']
    },
    'comedian': {
        'protected_attributes': ['gender', 'humor_style', 'language', 'experience'],
        'fairness_threshold': 0.75,
        'monitoring_frequency': 'weekly',
        'special_considerations': ['humor_preference_bias', 'cultural_bias']
    }
}

# Example usage and testing
async def main():
    """Example usage of bias fairness monitor"""
    try:
        # Initialize monitor
        monitor = BiasFairnessMonitor()
        
        # Simulate model predictions and labels
        n_samples = 1000
        predictions = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
        labels = np.random.choice([0, 1], size=n_samples, p=[0.65, 0.35])
        
        # Simulate metadata
        metadata = {
            'creator_type': 'musician',
            'n_samples': n_samples,
            'model_version': '1.2.0'
        }
        
        # Monitor bias
        fairness_report = await monitor.monitor_model_bias(
            model_id='creator-classifier-v2',
            predictions=predictions,
            labels=labels,
            metadata=metadata
        )
        
        print(f"\n🎯 Fairness Report Summary:")
        print(f"   Overall Fairness Score: {fairness_report.overall_fairness_score:.3f}")
        print(f"   Risk Level: {fairness_report.risk_level}")
        print(f"   Compliance Status: {fairness_report.compliance_status}")
        print(f"   Number of Violations: {len(fairness_report.violations)}")
        print(f"   Recommendations: {len(fairness_report.recommendations)}")
        
        # Get historical trends
        trends = await monitor.get_historical_bias_trends('creator-classifier-v2')
        print(f"\n📈 Bias Trends:")
        print(f"   Average Score: {trends['fairness_trend']['average_score']}")
        print(f"   Trend Direction: {trends['fairness_trend']['trend_direction']}")
        
        print("\n✅ Bias fairness monitoring demonstration complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in bias fairness monitoring: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())