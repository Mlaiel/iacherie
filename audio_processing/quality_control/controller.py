"""
🎯 Quality Controller - Central Quality Management System

Professional audio quality controller responsible for orchestrating all
quality control operations, managing quality workflows, and enforcing
quality standards across the audio processing pipeline.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

from .validator import AudioQualityValidator
from .monitor import QualityMonitor
from .standards import QualityStandards, QualityProfile
from .metrics import QualityMetrics, QualityReport
from .gates import QualityGate, QualityGateResult
from .optimization import QualityOptimizer
from .compliance import ComplianceChecker

logger = logging.getLogger(__name__)


class ControllerMode(Enum):
    """Quality controller operation modes"""
    STRICT = "strict"           # Maximum quality enforcement
    STANDARD = "standard"       # Standard quality requirements
    LENIENT = "lenient"        # Relaxed quality requirements
    CUSTOM = "custom"          # Custom quality configuration


class QualityAction(Enum):
    """Available quality control actions"""
    ACCEPT = "accept"          # Content passes quality checks
    REJECT = "reject"          # Content fails quality checks
    OPTIMIZE = "optimize"      # Content needs optimization
    REVIEW = "review"          # Content requires manual review
    REPROCESS = "reprocess"    # Content needs reprocessing


@dataclass
class QualityControlConfig:
    """Quality control configuration"""
    mode: ControllerMode = ControllerMode.STANDARD
    auto_optimize: bool = True
    auto_reject: bool = False
    manual_review_threshold: float = 0.7
    optimization_attempts: int = 3
    quality_gates_enabled: bool = True
    compliance_checks_enabled: bool = True
    monitoring_enabled: bool = True
    reporting_enabled: bool = True
    cache_results: bool = True
    async_processing: bool = True


@dataclass
class QualityDecision:
    """Quality control decision result"""
    action: QualityAction
    score: float
    confidence: float
    reasons: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class QualityController:
    """
    🎯 Professional Audio Quality Controller
    
    Central orchestrator for audio quality management:
    - Quality validation and assessment
    - Automated quality gates
    - Quality optimization
    - Compliance checking
    - Quality monitoring and reporting
    - Decision making and workflow management
    """
    
    def __init__(self, config: Optional[QualityControlConfig] = None):
        self.config = config or QualityControlConfig()
        
        # Initialize components
        self.validator = AudioQualityValidator()
        self.monitor = QualityMonitor() if self.config.monitoring_enabled else None
        self.standards = QualityStandards()
        self.optimizer = QualityOptimizer() if self.config.auto_optimize else None
        self.compliance_checker = ComplianceChecker() if self.config.compliance_checks_enabled else None
        
        # Quality gates
        self.quality_gates: List[QualityGate] = []
        self._setup_quality_gates()
        
        # Processing cache
        self.cache: Dict[str, QualityDecision] = {} if self.config.cache_results else None
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'accepted': 0,
            'rejected': 0,
            'optimized': 0,
            'reviews_required': 0,
            'average_score': 0.0,
            'processing_times': []
        }
        
        logger.info(f"QualityController initialized in {self.config.mode.value} mode")
    
    async def process_audio(
        self,
        audio_data: Union[np.ndarray, str, Path],
        sample_rate: Optional[int] = None,
        quality_profile: Optional[QualityProfile] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityDecision:
        """
        Process audio through complete quality control pipeline
        
        Args:
            audio_data: Audio data (array, file path, or Path object)
            sample_rate: Sample rate if audio_data is numpy array
            quality_profile: Target quality profile
            metadata: Additional metadata
            
        Returns:
            QualityDecision with action and details
        """
        start_time = datetime.now()
        
        try:
            # Generate cache key
            cache_key = None
            if self.config.cache_results:
                cache_key = self._generate_cache_key(audio_data, quality_profile)
                if cache_key in self.cache:
                    logger.info("Returning cached quality decision")
                    return self.cache[cache_key]
            
            # Load audio if needed
            if isinstance(audio_data, (str, Path)):
                import librosa
                audio_array, sr = librosa.load(str(audio_data), sr=sample_rate)
            else:
                audio_array = audio_data
                sr = sample_rate or 44100
            
            # Get quality profile
            profile = quality_profile or self.standards.get_default_profile()
            
            # Step 1: Quality validation
            validation_result = await self.validator.validate_audio(
                audio_array, sr, profile
            )
            
            # Step 2: Quality gates
            gate_results = []
            if self.config.quality_gates_enabled:
                gate_results = await self._run_quality_gates(
                    audio_array, sr, validation_result, profile
                )
            
            # Step 3: Compliance checking
            compliance_result = None
            if self.compliance_checker:
                compliance_result = await self.compliance_checker.check_compliance(
                    audio_array, sr, profile
                )
            
            # Step 4: Make quality decision
            decision = await self._make_quality_decision(
                validation_result, gate_results, compliance_result, profile
            )
            
            # Step 5: Apply optimization if needed
            if decision.action == QualityAction.OPTIMIZE and self.optimizer:
                decision = await self._handle_optimization(
                    audio_array, sr, decision, profile
                )
            
            # Step 6: Update monitoring
            if self.monitor:
                await self.monitor.record_quality_decision(decision, validation_result)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            decision.processing_time = processing_time
            
            # Update statistics
            self._update_statistics(decision)
            
            # Cache result
            if cache_key and self.config.cache_results:
                self.cache[cache_key] = decision
            
            logger.info(f"Audio quality control completed: {decision.action.value} "
                       f"(score: {decision.score:.3f}, time: {processing_time:.2f}s)")
            
            return decision
            
        except Exception as e:
            logger.error(f"Quality control processing failed: {e}")
            return QualityDecision(
                action=QualityAction.REJECT,
                score=0.0,
                confidence=0.0,
                reasons=[f"Processing error: {str(e)}"],
                recommendations=["Contact technical support"]
            )
    
    async def batch_process(
        self,
        audio_files: List[Union[str, Path, np.ndarray]],
        sample_rates: Optional[List[int]] = None,
        quality_profile: Optional[QualityProfile] = None,
        max_concurrent: int = 10
    ) -> List[QualityDecision]:
        """
        Process multiple audio files concurrently
        
        Args:
            audio_files: List of audio files or arrays
            sample_rates: Sample rates for arrays
            quality_profile: Target quality profile
            max_concurrent: Maximum concurrent processing
            
        Returns:
            List of QualityDecision results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single(audio, sr):
            async with semaphore:
                return await self.process_audio(audio, sr, quality_profile)
        
        # Prepare tasks
        tasks = []
        for i, audio in enumerate(audio_files):
            sr = sample_rates[i] if sample_rates and i < len(sample_rates) else None
            tasks.append(process_single(audio, sr))
        
        # Execute batch processing
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for item {i}: {result}")
                processed_results.append(QualityDecision(
                    action=QualityAction.REJECT,
                    score=0.0,
                    confidence=0.0,
                    reasons=[f"Batch processing error: {str(result)}"],
                    recommendations=["Contact technical support"]
                ))
            else:
                processed_results.append(result)
        
        logger.info(f"Batch processed {len(audio_files)} audio files")
        return processed_results
    
    async def _run_quality_gates(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        validation_result: QualityReport,
        profile: QualityProfile
    ) -> List[QualityGateResult]:
        """Run all configured quality gates"""
        gate_results = []
        
        for gate in self.quality_gates:
            try:
                result = await gate.evaluate(
                    audio_data, sample_rate, validation_result, profile
                )
                gate_results.append(result)
            except Exception as e:
                logger.error(f"Quality gate {gate.name} failed: {e}")
                gate_results.append(QualityGateResult(
                    gate_name=gate.name,
                    passed=False,
                    score=0.0,
                    message=f"Gate evaluation failed: {str(e)}"
                ))
        
        return gate_results
    
    async def _make_quality_decision(
        self,
        validation_result: QualityReport,
        gate_results: List[QualityGateResult],
        compliance_result: Optional[Dict[str, Any]],
        profile: QualityProfile
    ) -> QualityDecision:
        """Make final quality control decision"""
        
        # Calculate overall score
        overall_score = validation_result.overall_score
        
        # Check gate results
        gates_passed = all(gate.passed for gate in gate_results) if gate_results else True
        gate_scores = [gate.score for gate in gate_results if gate.score is not None]
        
        # Adjust score based on gates
        if gate_scores:
            gate_average = sum(gate_scores) / len(gate_scores)
            overall_score = (overall_score + gate_average) / 2
        
        # Check compliance
        compliance_passed = True
        compliance_score = 1.0
        if compliance_result:
            compliance_passed = compliance_result.get('passed', True)
            compliance_score = compliance_result.get('score', 1.0)
            overall_score = (overall_score + compliance_score) / 2
        
        # Determine action based on mode and thresholds
        if self.config.mode == ControllerMode.STRICT:
            action_threshold = 0.9
            optimization_threshold = 0.8
        elif self.config.mode == ControllerMode.LENIENT:
            action_threshold = 0.6
            optimization_threshold = 0.5
        else:  # STANDARD
            action_threshold = 0.75
            optimization_threshold = 0.65
        
        # Decision logic
        reasons = []
        recommendations = []
        
        if not gates_passed:
            action = QualityAction.REJECT
            reasons.append("Failed quality gate requirements")
            recommendations.append("Review quality gate failures and improve audio")
        elif not compliance_passed:
            action = QualityAction.REJECT
            reasons.append("Failed compliance requirements")
            recommendations.append("Ensure audio meets compliance standards")
        elif overall_score >= action_threshold:
            action = QualityAction.ACCEPT
            reasons.append(f"High quality score: {overall_score:.3f}")
        elif overall_score >= optimization_threshold:
            if self.config.auto_optimize:
                action = QualityAction.OPTIMIZE
                reasons.append(f"Score {overall_score:.3f} meets optimization threshold")
                recommendations.append("Audio will be automatically optimized")
            else:
                action = QualityAction.REVIEW
                reasons.append("Manual review required for optimization decision")
        elif overall_score >= self.config.manual_review_threshold:
            action = QualityAction.REVIEW
            reasons.append("Manual review required due to low score")
            recommendations.append("Consider audio quality improvements")
        else:
            if self.config.auto_reject:
                action = QualityAction.REJECT
                reasons.append(f"Score {overall_score:.3f} below minimum threshold")
            else:
                action = QualityAction.REVIEW
                reasons.append("Manual review required for reject decision")
        
        # Add specific recommendations from validation
        if validation_result.recommendations:
            recommendations.extend(validation_result.recommendations)
        
        # Calculate confidence
        confidence = min(1.0, overall_score + 0.1)  # Boost confidence slightly
        
        return QualityDecision(
            action=action,
            score=overall_score,
            confidence=confidence,
            reasons=reasons,
            recommendations=recommendations,
            metadata={
                'validation_result': validation_result,
                'gate_results': gate_results,
                'compliance_result': compliance_result,
                'profile_used': profile.name
            }
        )
    
    async def _handle_optimization(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        decision: QualityDecision,
        profile: QualityProfile
    ) -> QualityDecision:
        """Handle audio optimization process"""
        
        for attempt in range(self.config.optimization_attempts):
            try:
                logger.info(f"Optimization attempt {attempt + 1}/{self.config.optimization_attempts}")
                
                # Optimize audio
                optimized_audio = await self.optimizer.optimize_audio(
                    audio_data, sample_rate, profile, decision.metadata['validation_result']
                )
                
                # Re-validate optimized audio
                validation_result = await self.validator.validate_audio(
                    optimized_audio, sample_rate, profile
                )
                
                # Check if optimization improved quality
                if validation_result.overall_score > decision.score:
                    decision.score = validation_result.overall_score
                    decision.action = QualityAction.ACCEPT if validation_result.overall_score >= 0.75 else QualityAction.REVIEW
                    decision.reasons.append(f"Optimization successful (attempt {attempt + 1})")
                    decision.metadata['optimized_audio'] = optimized_audio
                    decision.metadata['optimization_attempts'] = attempt + 1
                    break
                    
            except Exception as e:
                logger.warning(f"Optimization attempt {attempt + 1} failed: {e}")
                continue
        
        else:
            # All optimization attempts failed
            decision.action = QualityAction.REJECT if self.config.auto_reject else QualityAction.REVIEW
            decision.reasons.append(f"Optimization failed after {self.config.optimization_attempts} attempts")
            decision.recommendations.append("Manual audio processing may be required")
        
        return decision
    
    def _setup_quality_gates(self):
        """Initialize standard quality gates"""
        from .gates import (
            MinimumQualityGate, NoiseGate, DistortionGate,
            DynamicRangeGate, FrequencyResponseGate
        )
        
        if self.config.quality_gates_enabled:
            self.quality_gates = [
                MinimumQualityGate("minimum_quality", threshold=0.5),
                NoiseGate("noise_gate", max_noise_level=-40),
                DistortionGate("distortion_gate", max_thd=5.0),
                DynamicRangeGate("dynamic_range_gate", min_range=20.0),
                FrequencyResponseGate("frequency_response_gate")
            ]
    
    def _generate_cache_key(
        self,
        audio_data: Union[np.ndarray, str, Path],
        profile: Optional[QualityProfile]
    ) -> str:
        """Generate cache key for audio processing"""
        import hashlib
        
        # Create hash components
        components = [
            str(type(audio_data)),
            str(profile.name if profile else "default"),
            str(self.config.mode.value)
        ]
        
        if isinstance(audio_data, np.ndarray):
            # Hash audio data
            audio_hash = hashlib.md5(audio_data.tobytes()).hexdigest()
            components.append(audio_hash)
        else:
            # Hash file path and modification time
            file_path = Path(audio_data)
            if file_path.exists():
                components.extend([
                    str(file_path),
                    str(file_path.stat().st_mtime)
                ])
        
        return hashlib.sha256('_'.join(components).encode()).hexdigest()
    
    def _update_statistics(self, decision: QualityDecision):
        """Update processing statistics"""
        self.stats['total_processed'] += 1
        
        if decision.action == QualityAction.ACCEPT:
            self.stats['accepted'] += 1
        elif decision.action == QualityAction.REJECT:
            self.stats['rejected'] += 1
        elif decision.action == QualityAction.OPTIMIZE:
            self.stats['optimized'] += 1
        elif decision.action == QualityAction.REVIEW:
            self.stats['reviews_required'] += 1
        
        # Update average score
        current_avg = self.stats['average_score']
        total = self.stats['total_processed']
        self.stats['average_score'] = (current_avg * (total - 1) + decision.score) / total
        
        # Track processing times
        self.stats['processing_times'].append(decision.processing_time)
        if len(self.stats['processing_times']) > 1000:
            self.stats['processing_times'] = self.stats['processing_times'][-1000:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get controller statistics"""
        stats = self.stats.copy()
        
        if self.stats['processing_times']:
            stats['average_processing_time'] = sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            stats['max_processing_time'] = max(self.stats['processing_times'])
            stats['min_processing_time'] = min(self.stats['processing_times'])
        
        return stats
    
    def reset_statistics(self):
        """Reset controller statistics"""
        self.stats = {
            'total_processed': 0,
            'accepted': 0,
            'rejected': 0,
            'optimized': 0,
            'reviews_required': 0,
            'average_score': 0.0,
            'processing_times': []
        }
    
    def configure_quality_gates(self, gates: List[QualityGate]):
        """Configure custom quality gates"""
        self.quality_gates = gates
        logger.info(f"Configured {len(gates)} quality gates")
    
    def add_quality_gate(self, gate: QualityGate):
        """Add a quality gate"""
        self.quality_gates.append(gate)
        logger.info(f"Added quality gate: {gate.name}")
    
    def remove_quality_gate(self, gate_name: str):
        """Remove a quality gate by name"""
        self.quality_gates = [gate for gate in self.quality_gates if gate.name != gate_name]
        logger.info(f"Removed quality gate: {gate_name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health = {
            'status': 'healthy',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check validator
            health['components']['validator'] = 'healthy' if self.validator else 'disabled'
            
            # Check monitor
            if self.monitor:
                monitor_health = await self.monitor.health_check()
                health['components']['monitor'] = 'healthy' if monitor_health else 'unhealthy'
            else:
                health['components']['monitor'] = 'disabled'
            
            # Check optimizer
            health['components']['optimizer'] = 'healthy' if self.optimizer else 'disabled'
            
            # Check compliance checker
            health['components']['compliance'] = 'healthy' if self.compliance_checker else 'disabled'
            
            # Check quality gates
            health['components']['quality_gates'] = f"{len(self.quality_gates)} gates configured"
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health['status'] = 'unhealthy'
            health['error'] = str(e)
            return health
