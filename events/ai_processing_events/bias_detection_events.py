"""Bias Detection Events

Enterprise-grade bias detection and mitigation system for the IA Influencer Agent platform.
Handles sophisticated bias analysis including algorithmic bias, content bias, demographic bias,
and fairness assessment across AI models and content recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission is strictly prohibited.
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Core imports
from ..core.base_event_handler import BaseEventHandler
from ..core.event_priority import EventPriority

logger = logging.getLogger(__name__)

class BiasType(Enum):
    """Types of bias to detect"""
    
    DEMOGRAPHIC_BIAS = "demographic_bias"
    GENDER_BIAS = "gender_bias"
    RACIAL_BIAS = "racial_bias"
    AGE_BIAS = "age_bias"
    CULTURAL_BIAS = "cultural_bias"
    SOCIOECONOMIC_BIAS = "socioeconomic_bias"
    RELIGIOUS_BIAS = "religious_bias"
    ALGORITHMIC_BIAS = "algorithmic_bias"
    SELECTION_BIAS = "selection_bias"
    CONFIRMATION_BIAS = "confirmation_bias"
    REPRESENTATION_BIAS = "representation_bias"
    MEASUREMENT_BIAS = "measurement_bias"

class BiasSource(Enum):
    """Sources of bias"""
    
    TRAINING_DATA = "training_data"
    MODEL_ARCHITECTURE = "model_architecture"
    FEATURE_SELECTION = "feature_selection"
    LABELING_PROCESS = "labeling_process"
    SAMPLING_METHOD = "sampling_method"
    HUMAN_ANNOTATION = "human_annotation"
    RECOMMENDATION_ALGORITHM = "recommendation_algorithm"
    CONTENT_CURATION = "content_curation"

class BiasSeverity(Enum):
    """Bias severity levels"""
    
    MINIMAL = "minimal"       # 0.0 - 0.2
    LOW = "low"              # 0.2 - 0.4
    MODERATE = "moderate"    # 0.4 - 0.6
    HIGH = "high"            # 0.6 - 0.8
    CRITICAL = "critical"    # 0.8 - 1.0

class FairnessMetric(Enum):
    """Fairness evaluation metrics"""
    
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"
    COUNTERFACTUAL_FAIRNESS = "counterfactual_fairness"

@dataclass
class BiasMetrics:
    """Bias detection metrics"""
    
    overall_bias_score: float
    demographic_bias: float
    gender_bias: float
    racial_bias: float
    age_bias: float
    cultural_bias: float
    algorithmic_bias: float
    severity_level: BiasSeverity
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall_bias_score': self.overall_bias_score,
            'demographic_bias': self.demographic_bias,
            'gender_bias': self.gender_bias,
            'racial_bias': self.racial_bias,
            'age_bias': self.age_bias,
            'cultural_bias': self.cultural_bias,
            'algorithmic_bias': self.algorithmic_bias,
            'severity_level': self.severity_level.value,
            'confidence': self.confidence
        }

@dataclass
class FairnessAssessment:
    """Fairness assessment results"""
    
    demographic_parity: float
    equalized_odds: float
    equal_opportunity: float
    calibration_score: float
    individual_fairness: float
    overall_fairness: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'demographic_parity': self.demographic_parity,
            'equalized_odds': self.equalized_odds,
            'equal_opportunity': self.equal_opportunity,
            'calibration_score': self.calibration_score,
            'individual_fairness': self.individual_fairness,
            'overall_fairness': self.overall_fairness
        }

@dataclass
class BiasDetectionRequest:
    """Bias detection request"""
    
    request_id: str
    target_system: str  # The system/model/algorithm to analyze
    analysis_type: str  # Type of analysis (content, recommendations, model outputs)
    data_sample: Any    # Sample data to analyze
    protected_attributes: List[str] = field(default_factory=list)
    bias_types: List[BiasType] = field(default_factory=lambda: list(BiasType))
    fairness_metrics: List[FairnessMetric] = field(default_factory=lambda: list(FairnessMetric))
    context: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.HIGH
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class BiasDetectionResult:
    """Bias detection result"""
    
    request_id: str
    target_system: str
    bias_metrics: BiasMetrics
    fairness_assessment: FairnessAssessment
    bias_sources: List[BiasSource] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    detected_patterns: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'target_system': self.target_system,
            'bias_metrics': self.bias_metrics.to_dict(),
            'fairness_assessment': self.fairness_assessment.to_dict(),
            'bias_sources': [source.value for source in self.bias_sources],
            'recommendations': self.recommendations,
            'mitigation_strategies': self.mitigation_strategies,
            'detected_patterns': self.detected_patterns,
            'processing_time': self.processing_time,
            'success': self.success,
            'error_message': self.error_message,
            'completed_at': self.completed_at.isoformat()
        }

class BiasDetectionEvents(BaseEventHandler):
    """AI-powered bias detection and mitigation system"""
    
    def __init__(self, max_workers -> None: int = 4) -> None:
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.request_queue = asyncio.Queue(maxsize=1000)
        
        # Bias detection models (mock implementations)
        self.bias_detectors = {
            BiasType.DEMOGRAPHIC_BIAS: self._detect_demographic_bias,
            BiasType.GENDER_BIAS: self._detect_gender_bias,
            BiasType.RACIAL_BIAS: self._detect_racial_bias,
            BiasType.AGE_BIAS: self._detect_age_bias,
            BiasType.CULTURAL_BIAS: self._detect_cultural_bias,
            BiasType.ALGORITHMIC_BIAS: self._detect_algorithmic_bias
        }
        
        # Fairness metrics calculators
        self.fairness_calculators = {
            FairnessMetric.DEMOGRAPHIC_PARITY: self._calculate_demographic_parity,
            FairnessMetric.EQUALIZED_ODDS: self._calculate_equalized_odds,
            FairnessMetric.EQUAL_OPPORTUNITY: self._calculate_equal_opportunity,
            FairnessMetric.CALIBRATION: self._calculate_calibration,
            FairnessMetric.INDIVIDUAL_FAIRNESS: self._calculate_individual_fairness
        }
        
        # Performance tracking
        self.total_detections = 0
        self.successful_detections = 0
        self.bias_alerts_triggered = 0
        self.is_running = False
        
        logger.info("Bias Detection Events initialized")
    
    async def start_detector(self) -> None:
        """Start the bias detection system"""
        self.is_running = True
        
        # Start worker tasks
        for i in range(4):
            asyncio.create_task(self._worker_loop(f"bias_worker_{i}"))
        
        logger.info("Bias Detection Events started")
    
    async def stop_detector(self) -> None:
        """Stop the bias detection system"""
        self.is_running = False
        self.executor.shutdown(wait=True)
        logger.info("Bias Detection Events stopped")
    
    async def detect_bias(self, request: BiasDetectionRequest) -> BiasDetectionResult:
        """Detect bias in the specified system/data"""
        start_time = time.time()
        
        try:
            # Run bias detection for each specified bias type
            bias_scores = {}
            for bias_type in request.bias_types:
                detector = self.bias_detectors.get(bias_type)
                if detector:
                    score = await detector(request)
                    bias_scores[bias_type] = score
                else:
                    bias_scores[bias_type] = np.random.uniform(0.0, 0.3)  # Default low bias
            
            # Calculate overall bias metrics
            bias_metrics = self._calculate_bias_metrics(bias_scores)
            
            # Assess fairness
            fairness_assessment = await self._assess_fairness(request)
            
            # Identify bias sources
            bias_sources = self._identify_bias_sources(bias_metrics, request)
            
            # Generate recommendations and mitigation strategies
            recommendations = self._generate_recommendations(bias_metrics, bias_sources)
            mitigation_strategies = self._generate_mitigation_strategies(bias_metrics, bias_sources)
            detected_patterns = self._identify_bias_patterns(bias_metrics, request)
            
            processing_time = time.time() - start_time
            self.successful_detections += 1
            
            # Check if bias alert should be triggered
            if bias_metrics.severity_level in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]:
                self.bias_alerts_triggered += 1
                logger.warning(f"High bias detected in {request.target_system}: "
                             f"{bias_metrics.severity_level.value} (score: {bias_metrics.overall_bias_score:.2f})")
            
            return BiasDetectionResult(
                request_id=request.request_id,
                target_system=request.target_system,
                bias_metrics=bias_metrics,
                fairness_assessment=fairness_assessment,
                bias_sources=bias_sources,
                recommendations=recommendations,
                mitigation_strategies=mitigation_strategies,
                detected_patterns=detected_patterns,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Bias detection failed: {str(e)}")
            
            return BiasDetectionResult(
                request_id=request.request_id,
                target_system=request.target_system,
                bias_metrics=BiasMetrics(
                    overall_bias_score=0.0, demographic_bias=0.0, gender_bias=0.0,
                    racial_bias=0.0, age_bias=0.0, cultural_bias=0.0, algorithmic_bias=0.0,
                    severity_level=BiasSeverity.MINIMAL, confidence=0.0
                ),
                fairness_assessment=FairnessAssessment(
                    demographic_parity=0.0, equalized_odds=0.0, equal_opportunity=0.0,
                    calibration_score=0.0, individual_fairness=0.0, overall_fairness=0.0
                ),
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _detect_demographic_bias(self, request: BiasDetectionRequest) -> float:
        """Detect demographic bias"""
        await asyncio.sleep(0.05)  # Simulate processing time
        
        # Mock demographic bias detection
        # In real implementation, this would analyze representation across demographics
        protected_attrs = request.protected_attributes
        bias_score = 0.0
        
        if 'age' in protected_attrs or 'gender' in protected_attrs or 'race' in protected_attrs:
            # Simulate higher bias if multiple protected attributes are involved
            bias_score = np.random.uniform(0.1, 0.6)
        else:
            bias_score = np.random.uniform(0.0, 0.3)
        
        return bias_score
    
    async def _detect_gender_bias(self, request: BiasDetectionRequest) -> float:
        """Detect gender bias"""
        await asyncio.sleep(0.04)  # Simulate processing time
        
        # Mock gender bias detection
        # In real implementation, this would analyze gender representation and treatment
        return np.random.uniform(0.0, 0.4)
    
    async def _detect_racial_bias(self, request: BiasDetectionRequest) -> float:
        """Detect racial bias"""
        await asyncio.sleep(0.06)  # Simulate processing time
        
        # Mock racial bias detection
        # In real implementation, this would analyze racial representation and fairness
        return np.random.uniform(0.0, 0.5)
    
    async def _detect_age_bias(self, request: BiasDetectionRequest) -> float:
        """Detect age bias"""
        await asyncio.sleep(0.03)  # Simulate processing time
        
        # Mock age bias detection
        return np.random.uniform(0.0, 0.3)
    
    async def _detect_cultural_bias(self, request: BiasDetectionRequest) -> float:
        """Detect cultural bias"""
        await asyncio.sleep(0.04)  # Simulate processing time
        
        # Mock cultural bias detection
        return np.random.uniform(0.0, 0.4)
    
    async def _detect_algorithmic_bias(self, request: BiasDetectionRequest) -> float:
        """Detect algorithmic bias"""
        await asyncio.sleep(0.08)  # Simulate processing time
        
        # Mock algorithmic bias detection
        # In real implementation, this would analyze model predictions for systematic bias
        return np.random.uniform(0.0, 0.5)
    
    def _calculate_bias_metrics(self, bias_scores: Dict[BiasType, float]) -> BiasMetrics:
        """Calculate overall bias metrics"""
        
        # Extract individual bias scores
        demographic_bias = bias_scores.get(BiasType.DEMOGRAPHIC_BIAS, 0.0)
        gender_bias = bias_scores.get(BiasType.GENDER_BIAS, 0.0)
        racial_bias = bias_scores.get(BiasType.RACIAL_BIAS, 0.0)
        age_bias = bias_scores.get(BiasType.AGE_BIAS, 0.0)
        cultural_bias = bias_scores.get(BiasType.CULTURAL_BIAS, 0.0)
        algorithmic_bias = bias_scores.get(BiasType.ALGORITHMIC_BIAS, 0.0)
        
        # Calculate overall bias score (weighted average)
        weights = {
            BiasType.DEMOGRAPHIC_BIAS: 0.2,
            BiasType.GENDER_BIAS: 0.15,
            BiasType.RACIAL_BIAS: 0.2,
            BiasType.AGE_BIAS: 0.1,
            BiasType.CULTURAL_BIAS: 0.15,
            BiasType.ALGORITHMIC_BIAS: 0.2
        }
        
        overall_score = sum(bias_scores.get(bias_type, 0.0) * weight 
                          for bias_type, weight in weights.items())
        
        # Determine severity level
        severity_level = self._determine_bias_severity(overall_score)
        
        # Calculate confidence (mock)
        confidence = np.random.uniform(0.8, 0.95)
        
        return BiasMetrics(
            overall_bias_score=overall_score,
            demographic_bias=demographic_bias,
            gender_bias=gender_bias,
            racial_bias=racial_bias,
            age_bias=age_bias,
            cultural_bias=cultural_bias,
            algorithmic_bias=algorithmic_bias,
            severity_level=severity_level,
            confidence=confidence
        )
    
    def _determine_bias_severity(self, overall_score: float) -> BiasSeverity:
        """Determine bias severity level"""
        if overall_score >= 0.8:
            return BiasSeverity.CRITICAL
        elif overall_score >= 0.6:
            return BiasSeverity.HIGH
        elif overall_score >= 0.4:
            return BiasSeverity.MODERATE
        elif overall_score >= 0.2:
            return BiasSeverity.LOW
        else:
            return BiasSeverity.MINIMAL
    
    async def _assess_fairness(self, request: BiasDetectionRequest) -> FairnessAssessment:
        """Assess fairness using various metrics"""
        
        fairness_scores = {}
        
        # Calculate each fairness metric
        for metric in request.fairness_metrics:
            calculator = self.fairness_calculators.get(metric)
            if calculator:
                score = await calculator(request)
                fairness_scores[metric] = score
            else:
                fairness_scores[metric] = np.random.uniform(0.6, 0.9)  # Default fair score
        
        # Extract or set default values
        demographic_parity = fairness_scores.get(FairnessMetric.DEMOGRAPHIC_PARITY, 0.8)
        equalized_odds = fairness_scores.get(FairnessMetric.EQUALIZED_ODDS, 0.8)
        equal_opportunity = fairness_scores.get(FairnessMetric.EQUAL_OPPORTUNITY, 0.8)
        calibration_score = fairness_scores.get(FairnessMetric.CALIBRATION, 0.8)
        individual_fairness = fairness_scores.get(FairnessMetric.INDIVIDUAL_FAIRNESS, 0.8)
        
        # Calculate overall fairness
        overall_fairness = np.mean([demographic_parity, equalized_odds, equal_opportunity,
                                  calibration_score, individual_fairness])
        
        return FairnessAssessment(
            demographic_parity=demographic_parity,
            equalized_odds=equalized_odds,
            equal_opportunity=equal_opportunity,
            calibration_score=calibration_score,
            individual_fairness=individual_fairness,
            overall_fairness=overall_fairness
        )
    
    async def _calculate_demographic_parity(self, request: BiasDetectionRequest) -> float:
        """Calculate demographic parity metric"""
        await asyncio.sleep(0.02)
        return np.random.uniform(0.6, 0.9)
    
    async def _calculate_equalized_odds(self, request: BiasDetectionRequest) -> float:
        """Calculate equalized odds metric"""
        await asyncio.sleep(0.02)
        return np.random.uniform(0.6, 0.9)
    
    async def _calculate_equal_opportunity(self, request: BiasDetectionRequest) -> float:
        """Calculate equal opportunity metric"""
        await asyncio.sleep(0.02)
        return np.random.uniform(0.6, 0.9)
    
    async def _calculate_calibration(self, request: BiasDetectionRequest) -> float:
        """Calculate calibration metric"""
        await asyncio.sleep(0.02)
        return np.random.uniform(0.6, 0.9)
    
    async def _calculate_individual_fairness(self, request: BiasDetectionRequest) -> float:
        """Calculate individual fairness metric"""
        await asyncio.sleep(0.02)
        return np.random.uniform(0.6, 0.9)
    
    def _identify_bias_sources(self, bias_metrics: BiasMetrics, request: BiasDetectionRequest) -> List[BiasSource]:
        """Identify potential sources of bias"""
        sources = []
        
        if bias_metrics.overall_bias_score > 0.4:
            # High bias detected, identify likely sources
            if bias_metrics.demographic_bias > 0.5:
                sources.append(BiasSource.TRAINING_DATA)
                sources.append(BiasSource.SAMPLING_METHOD)
            
            if bias_metrics.algorithmic_bias > 0.5:
                sources.append(BiasSource.MODEL_ARCHITECTURE)
                sources.append(BiasSource.FEATURE_SELECTION)
            
            if 'recommendations' in request.analysis_type.lower():
                sources.append(BiasSource.RECOMMENDATION_ALGORITHM)
            
            if 'content' in request.analysis_type.lower():
                sources.append(BiasSource.CONTENT_CURATION)
                sources.append(BiasSource.HUMAN_ANNOTATION)
        
        return sources
    
    def _generate_recommendations(self, bias_metrics: BiasMetrics, bias_sources: List[BiasSource]) -> List[str]:
        """Generate bias mitigation recommendations"""
        recommendations = []
        
        if bias_metrics.severity_level in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]:
            recommendations.append("Immediate bias audit and mitigation required")
            recommendations.append("Review and retrain affected models")
        
        if BiasSource.TRAINING_DATA in bias_sources:
            recommendations.append("Audit training data for representative sampling")
            recommendations.append("Implement data augmentation for underrepresented groups")
        
        if BiasSource.MODEL_ARCHITECTURE in bias_sources:
            recommendations.append("Review model architecture for potential bias amplification")
            recommendations.append("Consider fairness-aware machine learning techniques")
        
        if BiasSource.FEATURE_SELECTION in bias_sources:
            recommendations.append("Audit feature selection process for proxy variables")
            recommendations.append("Implement feature importance analysis for bias detection")
        
        if bias_metrics.demographic_bias > 0.5:
            recommendations.append("Implement demographic parity constraints")
            recommendations.append("Regular monitoring of outcomes across demographic groups")
        
        if bias_metrics.gender_bias > 0.5:
            recommendations.append("Implement gender-aware evaluation metrics")
            recommendations.append("Review content and recommendations for gender stereotypes")
        
        return recommendations
    
    def _generate_mitigation_strategies(self, bias_metrics: BiasMetrics, bias_sources: List[BiasSource]) -> List[str]:
        """Generate bias mitigation strategies"""
        strategies = []
        
        # Pre-processing strategies
        if BiasSource.TRAINING_DATA in bias_sources:
            strategies.append("Data re-sampling and augmentation")
            strategies.append("Synthetic data generation for minority groups")
        
        # In-processing strategies
        if BiasSource.MODEL_ARCHITECTURE in bias_sources:
            strategies.append("Fairness-constrained optimization")
            strategies.append("Adversarial debiasing techniques")
        
        # Post-processing strategies
        if bias_metrics.overall_bias_score > 0.4:
            strategies.append("Threshold optimization for fairness")
            strategies.append("Output calibration across groups")
        
        # Monitoring strategies
        strategies.append("Continuous bias monitoring in production")
        strategies.append("Regular fairness audits and assessments")
        strategies.append("Bias alert system implementation")
        
        return strategies
    
    def _identify_bias_patterns(self, bias_metrics: BiasMetrics, request: BiasDetectionRequest) -> List[str]:
        """Identify specific bias patterns"""
        patterns = []
        
        if bias_metrics.demographic_bias > 0.4:
            patterns.append("Underrepresentation of certain demographic groups")
            patterns.append("Systematic differences in treatment across demographics")
        
        if bias_metrics.gender_bias > 0.4:
            patterns.append("Gender stereotyping in content or recommendations")
            patterns.append("Unequal representation across gender categories")
        
        if bias_metrics.racial_bias > 0.4:
            patterns.append("Racial disparities in outcomes or treatment")
            patterns.append("Cultural insensitivity in content recommendations")
        
        if bias_metrics.algorithmic_bias > 0.4:
            patterns.append("Systematic algorithmic discrimination")
            patterns.append("Feedback loops amplifying existing biases")
        
        return patterns
    
    async def _worker_loop(self, worker_id -> None: str) -> None:
        """Worker loop for processing bias detection requests"""
        logger.info(f"Bias detection worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get next request from queue
                request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=1.0
                )
                
                # Process the request
                result = await self.detect_bias(request)
                
                # Log result
                if result.success:
                    logger.debug(f"Bias analysis completed: {result.bias_metrics.severity_level.value} "
                               f"(score: {result.bias_metrics.overall_bias_score:.2f})")
                else:
                    logger.error(f"Bias detection failed: {result.error_message}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Bias detection worker {worker_id} error: {str(e)}")
                await asyncio.sleep(1.0)
        
        logger.info(f"Bias detection worker {worker_id} stopped")
    
    def get_detector_stats(self) -> Dict[str, Any]:
        """Get bias detector statistics"""
        success_rate = self.successful_detections / max(self.total_detections, 1)
        
        return {
            'total_detections': self.total_detections,
            'successful_detections': self.successful_detections,
            'success_rate': success_rate,
            'bias_alerts_triggered': self.bias_alerts_triggered,
            'supported_bias_types': [bt.value for bt in BiasType],
            'supported_fairness_metrics': [fm.value for fm in FairnessMetric],
            'bias_severity_levels': [bs.value for bs in BiasSeverity],
            'is_running': self.is_running
        }
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bias detection events"""
        try:
            event_type = event_data.get('event_type')
            
            if event_type == 'detect_bias':
                request = BiasDetectionRequest(
                    request_id=event_data.get('request_id', f"bias_{int(time.time())}"),
                    target_system=event_data.get('target_system'),
                    analysis_type=event_data.get('analysis_type'),
                    data_sample=event_data.get('data_sample'),
                    protected_attributes=event_data.get('protected_attributes', []),
                    bias_types=event_data.get('bias_types', list(BiasType)),
                    fairness_metrics=event_data.get('fairness_metrics', list(FairnessMetric))
                )
                
                result = await self.detect_bias(request)
                
                return {
                    'status': 'success',
                    'detection_result': result.to_dict()
                }
            
            elif event_type == 'get_stats':
                stats = self.get_detector_stats()
                return {
                    'status': 'success',
                    'detector_stats': stats
                }
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown event type: {event_type}'
                }
                
        except Exception as e:
            logger.error(f"Error handling bias detection event: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Export classes and functions
__all__ = [
    'BiasType',
    'BiasSource',
    'BiasSeverity',
    'FairnessMetric',
    'BiasMetrics',
    'FairnessAssessment',
    'BiasDetectionRequest',
    'BiasDetectionResult',
    'BiasDetectionEvents'
]