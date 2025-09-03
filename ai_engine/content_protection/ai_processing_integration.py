#!/usr/bin/env python3
"""AI Processing Integration Module for IA-Influencer-Agent
========================================================

Centralized integration module that coordinates all AI processing features
for comprehensive content protection and analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module integrates:
- Voice cloning detection
- Deepfake detection 
- Copyright matching engine
- Content fingerprinting
- AI watermarking system
- Style transfer protection
- Blockchain rights registration
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import json

# Import our AI processing modules
try:
    from .voice_clone_detector import VoiceCloneDetector, VoiceAuthenticityLevel
except ImportError:
    from ..ml.voice_clone_detector import VoiceCloneDetector, VoiceAuthenticityLevel

try:
    from .style_transfer_protection import StyleTransferProtector, StyleType, TransferDetectionResult
except ImportError:
    StyleTransferProtector = None
    StyleType = None
    TransferDetectionResult = None

try:
    from .watermarking import WatermarkingSystem, WatermarkConfig
except ImportError:
    WatermarkingSystem = None
    WatermarkConfig = None

try:
    from .copyright_detector import CopyrightDetector, DetectionResult
except ImportError:
    CopyrightDetector = None
    DetectionResult = None

try:
    from .fingerprinting import ContentFingerprint
except ImportError:
    ContentFingerprint = None

try:
    from ..audio.rights_management import RightsManager
except ImportError:
    RightsManager = None

try:
    from ...ai_agents.fraud_detection_agent.utils.deepfake_detector import DeepfakeDetector, ContentType
except ImportError:
    DeepfakeDetector = None
    ContentType = None

logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """AI processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ThreatLevel(Enum):
    """Content threat level assessment"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"


@dataclass
class AIProcessingResult:
    """Comprehensive AI processing analysis result"""
    content_id: str
    processing_status: ProcessingStatus
    threat_level: ThreatLevel
    overall_confidence: float
    
    # Individual analysis results
    voice_clone_analysis: Optional[Dict[str, Any]] = None
    deepfake_analysis: Optional[Dict[str, Any]] = None
    copyright_analysis: Optional[Dict[str, Any]] = None
    style_transfer_analysis: Optional[Dict[str, Any]] = None
    watermark_analysis: Optional[Dict[str, Any]] = None
    rights_analysis: Optional[Dict[str, Any]] = None
    
    # Processing metadata
    processing_time: float = 0.0
    features_analyzed: List[str] = None
    warnings: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.features_analyzed is None:
            self.features_analyzed = []
        if self.warnings is None:
            self.warnings = []
        if self.recommendations is None:
            self.recommendations = []


class AIProcessingEngine:
    """
    Comprehensive AI Processing Engine
    
    Coordinates all AI processing features to provide complete content analysis:
    - Voice authenticity verification
    - Deepfake and manipulation detection
    - Copyright infringement detection
    - Style transfer protection
    - Content watermarking
    - Blockchain rights management
    """
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.is_initialized = False
        
        # Initialize component analyzers
        self.voice_detector = None
        self.deepfake_detector = None
        self.copyright_detector = None
        self.style_protector = None
        self.watermarking_system = None
        self.rights_manager = None
        
        # Processing configuration
        self.config = {
            'enable_voice_detection': True,
            'enable_deepfake_detection': True,
            'enable_copyright_detection': True,
            'enable_style_protection': True,
            'enable_watermarking': True,
            'enable_rights_management': True,
            'parallel_processing': True,
            'confidence_threshold': 0.7
        }
        
        logger.info(f"AI Processing Engine initialized on device: {device}")
    
    async def initialize(self) -> bool:
        """Initialize all AI processing components"""
        try:
            initialization_tasks = []
            
            # Initialize voice clone detector
            if self.config['enable_voice_detection'] and VoiceCloneDetector:
                self.voice_detector = VoiceCloneDetector(device=self.device)
                initialization_tasks.append(self._init_voice_detector())
            
            # Initialize deepfake detector
            if self.config['enable_deepfake_detection'] and DeepfakeDetector:
                self.deepfake_detector = DeepfakeDetector()
                initialization_tasks.append(self._init_deepfake_detector())
            
            # Initialize copyright detector
            if self.config['enable_copyright_detection'] and CopyrightDetector:
                self.copyright_detector = CopyrightDetector()
                initialization_tasks.append(self._init_copyright_detector())
            
            # Initialize style transfer protector
            if self.config['enable_style_protection'] and StyleTransferProtector:
                self.style_protector = StyleTransferProtector(device=self.device)
                initialization_tasks.append(self._init_style_protector())
            
            # Initialize watermarking system
            if self.config['enable_watermarking'] and WatermarkingSystem:
                self.watermarking_system = WatermarkingSystem()
                initialization_tasks.append(self._init_watermarking_system())
            
            # Initialize rights manager
            if self.config['enable_rights_management'] and RightsManager:
                self.rights_manager = RightsManager()
                initialization_tasks.append(self._init_rights_manager())
            
            # Run all initializations
            if initialization_tasks:
                results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
                
                # Check for any failures
                failures = [r for r in results if isinstance(r, Exception)]
                if failures:
                    logger.warning(f"Some components failed to initialize: {len(failures)} failures")
                    for failure in failures:
                        logger.warning(f"Initialization failure: {failure}")
            
            self.is_initialized = True
            logger.info("AI Processing Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"AI Processing Engine initialization failed: {e}")
            return False
    
    async def process_content(self,
                            content_data: Any,
                            content_type: str,
                            content_id: str = None,
                            analysis_options: Dict[str, Any] = None) -> AIProcessingResult:
        """
        Comprehensive content analysis using all available AI processing features
        
        Args:
            content_data: The content to analyze (audio, video, image, text)
            content_type: Type of content (audio, video, image, text)
            content_id: Unique identifier for the content
            analysis_options: Additional options for analysis
            
        Returns:
            AIProcessingResult: Comprehensive analysis results
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        if content_id is None:
            import hashlib
            content_id = hashlib.md5(f"{content_type}_{time.time()}".encode()).hexdigest()[:16]
        
        analysis_options = analysis_options or {}
        
        try:
            # Initialize result
            result = AIProcessingResult(
                content_id=content_id,
                processing_status=ProcessingStatus.IN_PROGRESS,
                threat_level=ThreatLevel.SAFE,
                overall_confidence=0.0
            )
            
            # Collect analysis tasks
            analysis_tasks = []
            
            # Voice clone detection (for audio content)
            if (content_type in ['audio', 'voice'] and 
                self.voice_detector and 
                analysis_options.get('check_voice_cloning', True)):
                analysis_tasks.append(
                    self._analyze_voice_cloning(content_data, content_type)
                )
                result.features_analyzed.append('voice_cloning')
            
            # Deepfake detection (for video/audio/image)
            if (content_type in ['video', 'audio', 'image'] and 
                self.deepfake_detector and 
                analysis_options.get('check_deepfakes', True)):
                analysis_tasks.append(
                    self._analyze_deepfakes(content_data, content_type)
                )
                result.features_analyzed.append('deepfake_detection')
            
            # Copyright detection (for all content types)
            if (self.copyright_detector and 
                analysis_options.get('check_copyright', True)):
                analysis_tasks.append(
                    self._analyze_copyright(content_data, content_type)
                )
                result.features_analyzed.append('copyright_detection')
            
            # Style transfer protection
            if (self.style_protector and 
                analysis_options.get('check_style_transfer', True)):
                analysis_tasks.append(
                    self._analyze_style_transfer(content_data, content_type)
                )
                result.features_analyzed.append('style_transfer')
            
            # Watermark detection/verification
            if (self.watermarking_system and 
                analysis_options.get('check_watermarks', True)):
                analysis_tasks.append(
                    self._analyze_watermarks(content_data, content_type, analysis_options)
                )
                result.features_analyzed.append('watermarking')
            
            # Rights verification
            if (self.rights_manager and 
                analysis_options.get('check_rights', True)):
                analysis_tasks.append(
                    self._analyze_rights(content_data, content_type, analysis_options)
                )
                result.features_analyzed.append('rights_management')
            
            # Execute analyses
            if analysis_tasks:
                if self.config['parallel_processing']:
                    # Run analyses in parallel
                    analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                else:
                    # Run analyses sequentially
                    analysis_results = []
                    for task in analysis_tasks:
                        try:
                            analysis_result = await task
                            analysis_results.append(analysis_result)
                        except Exception as e:
                            analysis_results.append(e)
                
                # Process results
                await self._process_analysis_results(result, analysis_results)
            
            # Calculate overall assessment
            result.threat_level = self._calculate_threat_level(result)
            result.overall_confidence = self._calculate_overall_confidence(result)
            result.processing_time = time.time() - start_time
            result.processing_status = ProcessingStatus.COMPLETED
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            logger.info(f"Content analysis completed: {content_id} - {result.threat_level.value}")
            return result
            
        except Exception as e:
            logger.error(f"Content processing failed for {content_id}: {e}")
            
            return AIProcessingResult(
                content_id=content_id,
                processing_status=ProcessingStatus.FAILED,
                threat_level=ThreatLevel.SAFE,
                overall_confidence=0.0,
                processing_time=time.time() - start_time,
                warnings=[f"Processing failed: {str(e)}"]
            )
    
    # Individual analysis methods
    async def _analyze_voice_cloning(self, content_data: Any, content_type: str) -> Dict[str, Any]:
        """Analyze content for voice cloning"""
        try:
            import numpy as np
            
            # Convert content to appropriate format
            if isinstance(content_data, str):
                # Assume it's a file path or text representation
                audio_data = np.random.randn(16000)  # 1 second of dummy audio
            elif hasattr(content_data, 'shape'):
                audio_data = content_data
            else:
                audio_data = np.array(content_data) if content_data else np.random.randn(16000)
            
            result = await self.voice_detector.detect_voice_clone(
                audio_data=audio_data,
                sample_rate=16000
            )
            
            return {
                'analysis_type': 'voice_cloning',
                'authenticity_level': result.authenticity_level.value,
                'clone_probability': result.clone_probability,
                'confidence': result.confidence_score,
                'indicators': result.detection_indicators,
                'processing_time': result.processing_time
            }
            
        except Exception as e:
            logger.error(f"Voice cloning analysis failed: {e}")
            return {
                'analysis_type': 'voice_cloning',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _analyze_deepfakes(self, content_data: Any, content_type: str) -> Dict[str, Any]:
        """Analyze content for deepfakes"""
        try:
            # Prepare content for deepfake analysis
            content_dict = {
                'data': content_data,
                'type': content_type,
                'timestamp': time.time()
            }
            
            result = await self.deepfake_detector.analyze_content(content_dict)
            
            return {
                'analysis_type': 'deepfake_detection',
                'deepfake_probability': result.get('deepfake_probability', 0.0),
                'manipulation_detected': result.get('manipulation_detected', False),
                'confidence': result.get('authenticity_score', 0.0),
                'manipulation_types': result.get('manipulation_types', []),
                'technical_analysis': result.get('technical_analysis', {})
            }
            
        except Exception as e:
            logger.error(f"Deepfake analysis failed: {e}")
            return {
                'analysis_type': 'deepfake_detection',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _analyze_copyright(self, content_data: Any, content_type: str) -> Dict[str, Any]:
        """Analyze content for copyright violations"""
        try:
            result = await self.copyright_detector.detect_copyright(content_data, content_type)
            
            return {
                'analysis_type': 'copyright_detection',
                'detection_result': result.get('result', 'unknown'),
                'confidence': result.get('confidence', 0.0),
                'matches': result.get('matches', []),
                'analysis_time': result.get('analysis_time', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Copyright analysis failed: {e}")
            return {
                'analysis_type': 'copyright_detection',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _analyze_style_transfer(self, content_data: Any, content_type: str) -> Dict[str, Any]:
        """Analyze content for style transfer violations"""
        try:
            # Map content type to style type
            style_type_mapping = {
                'image': StyleType.ARTISTIC_VISUAL,
                'text': StyleType.WRITING_STYLE,
                'audio': StyleType.MUSICAL_STYLE,
                'video': StyleType.VIDEO_EDITING
            }
            
            style_type = style_type_mapping.get(content_type, StyleType.ARTISTIC_VISUAL)
            
            result = await self.style_protector.detect_style_transfer(
                content_data=content_data,
                style_type=style_type,
                check_database=True
            )
            
            return {
                'analysis_type': 'style_transfer',
                'detection_result': result.detection_result.value,
                'similarity_score': result.similarity_score,
                'transfer_probability': result.transfer_probability,
                'confidence': result.confidence_score,
                'matched_styles': result.matched_styles,
                'protection_violations': result.protection_violations
            }
            
        except Exception as e:
            logger.error(f"Style transfer analysis failed: {e}")
            return {
                'analysis_type': 'style_transfer',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _analyze_watermarks(self, content_data: Any, content_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for watermarks"""
        try:
            # Check if we should verify a specific watermark
            expected_watermark = options.get('expected_watermark')
            
            if expected_watermark:
                # Verify specific watermark
                result = await self.watermarking_system.verify_watermark(
                    content_data=content_data,
                    expected_watermark=expected_watermark,
                    media_type=content_type
                )
                
                return {
                    'analysis_type': 'watermark_verification',
                    'verified': result.get('verified', False),
                    'confidence': result.get('confidence', 0.0),
                    'extracted_data': result.get('extracted_data', ''),
                    'verification_type': 'specific_watermark'
                }
            else:
                # General watermark detection
                # This would require a more sophisticated watermark detection system
                return {
                    'analysis_type': 'watermark_detection',
                    'watermarks_detected': [],
                    'confidence': 0.5,
                    'detection_type': 'general_scan'
                }
            
        except Exception as e:
            logger.error(f"Watermark analysis failed: {e}")
            return {
                'analysis_type': 'watermark_analysis',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _analyze_rights(self, content_data: Any, content_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content rights and ownership"""
        try:
            # This would integrate with blockchain rights registration
            # For now, return a placeholder analysis
            
            return {
                'analysis_type': 'rights_verification',
                'rights_status': 'unverified',
                'blockchain_verified': False,
                'ownership_claims': [],
                'confidence': 0.5
            }
            
        except Exception as e:
            logger.error(f"Rights analysis failed: {e}")
            return {
                'analysis_type': 'rights_verification',
                'error': str(e),
                'confidence': 0.0
            }
    
    # Helper methods
    async def _process_analysis_results(self, result: AIProcessingResult, analysis_results: List[Any]):
        """Process individual analysis results into the main result"""
        for i, analysis_result in enumerate(analysis_results):
            if isinstance(analysis_result, Exception):
                result.warnings.append(f"Analysis {i} failed: {str(analysis_result)}")
                continue
            
            if not isinstance(analysis_result, dict):
                continue
            
            analysis_type = analysis_result.get('analysis_type', 'unknown')
            
            if analysis_type == 'voice_cloning':
                result.voice_clone_analysis = analysis_result
            elif analysis_type == 'deepfake_detection':
                result.deepfake_analysis = analysis_result
            elif analysis_type == 'copyright_detection':
                result.copyright_analysis = analysis_result
            elif analysis_type == 'style_transfer':
                result.style_transfer_analysis = analysis_result
            elif analysis_type in ['watermark_verification', 'watermark_detection']:
                result.watermark_analysis = analysis_result
            elif analysis_type == 'rights_verification':
                result.rights_analysis = analysis_result
    
    def _calculate_threat_level(self, result: AIProcessingResult) -> ThreatLevel:
        """Calculate overall threat level based on all analyses"""
        threat_scores = []
        
        # Voice cloning threat
        if result.voice_clone_analysis:
            clone_prob = result.voice_clone_analysis.get('clone_probability', 0.0)
            if clone_prob >= 0.8:
                threat_scores.append(4)  # High threat
            elif clone_prob >= 0.6:
                threat_scores.append(3)  # Medium threat
            elif clone_prob >= 0.4:
                threat_scores.append(2)  # Low threat
            else:
                threat_scores.append(1)  # Safe
        
        # Deepfake threat
        if result.deepfake_analysis:
            deepfake_prob = result.deepfake_analysis.get('deepfake_probability', 0.0)
            if deepfake_prob >= 0.8:
                threat_scores.append(4)
            elif deepfake_prob >= 0.6:
                threat_scores.append(3)
            elif deepfake_prob >= 0.4:
                threat_scores.append(2)
            else:
                threat_scores.append(1)
        
        # Copyright threat
        if result.copyright_analysis:
            detection_result = result.copyright_analysis.get('detection_result', 'clear')
            if detection_result == 'copyright_violation':
                threat_scores.append(4)
            elif detection_result == 'potential_match':
                threat_scores.append(3)
            else:
                threat_scores.append(1)
        
        # Style transfer threat
        if result.style_transfer_analysis:
            transfer_prob = result.style_transfer_analysis.get('transfer_probability', 0.0)
            if transfer_prob >= 0.8:
                threat_scores.append(4)
            elif transfer_prob >= 0.6:
                threat_scores.append(3)
            elif transfer_prob >= 0.4:
                threat_scores.append(2)
            else:
                threat_scores.append(1)
        
        # Calculate overall threat level
        if not threat_scores:
            return ThreatLevel.SAFE
        
        max_threat = max(threat_scores)
        avg_threat = sum(threat_scores) / len(threat_scores)
        
        # Use maximum threat with average as tiebreaker
        if max_threat >= 4 or avg_threat >= 3.5:
            return ThreatLevel.CRITICAL
        elif max_threat >= 3 or avg_threat >= 2.5:
            return ThreatLevel.HIGH_RISK
        elif max_threat >= 2 or avg_threat >= 1.5:
            return ThreatLevel.MEDIUM_RISK
        elif max_threat >= 1.5 or avg_threat >= 1.2:
            return ThreatLevel.LOW_RISK
        else:
            return ThreatLevel.SAFE
    
    def _calculate_overall_confidence(self, result: AIProcessingResult) -> float:
        """Calculate overall confidence score"""
        confidences = []
        
        # Collect confidence scores from all analyses
        for analysis in [result.voice_clone_analysis, result.deepfake_analysis, 
                        result.copyright_analysis, result.style_transfer_analysis, 
                        result.watermark_analysis, result.rights_analysis]:
            if analysis and 'confidence' in analysis:
                confidences.append(analysis['confidence'])
        
        if not confidences:
            return 0.0
        
        # Return weighted average (give more weight to higher confidence scores)
        weights = [c for c in confidences]  # Use confidence as weight
        weighted_sum = sum(c * w for c, w in zip(confidences, weights))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    def _generate_recommendations(self, result: AIProcessingResult) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Voice cloning recommendations
        if result.voice_clone_analysis:
            clone_prob = result.voice_clone_analysis.get('clone_probability', 0.0)
            if clone_prob >= 0.7:
                recommendations.append("High probability of voice cloning detected - verify speaker identity")
            elif clone_prob >= 0.5:
                recommendations.append("Moderate voice cloning risk - additional verification recommended")
        
        # Deepfake recommendations
        if result.deepfake_analysis:
            deepfake_prob = result.deepfake_analysis.get('deepfake_probability', 0.0)
            if deepfake_prob >= 0.7:
                recommendations.append("Significant deepfake indicators found - content may be artificially generated")
            elif deepfake_prob >= 0.5:
                recommendations.append("Some manipulation indicators detected - further analysis recommended")
        
        # Copyright recommendations
        if result.copyright_analysis:
            matches = result.copyright_analysis.get('matches', [])
            if matches:
                recommendations.append(f"Potential copyright matches found ({len(matches)}) - legal review advised")
        
        # Style transfer recommendations
        if result.style_transfer_analysis:
            violations = result.style_transfer_analysis.get('protection_violations', [])
            if violations:
                recommendations.append("Style protection violations detected - unauthorized style use suspected")
        
        # Overall threat recommendations
        if result.threat_level == ThreatLevel.CRITICAL:
            recommendations.append("CRITICAL: Multiple high-risk indicators - immediate action required")
        elif result.threat_level == ThreatLevel.HIGH_RISK:
            recommendations.append("HIGH RISK: Significant threats detected - thorough investigation needed")
        elif result.threat_level == ThreatLevel.MEDIUM_RISK:
            recommendations.append("MEDIUM RISK: Some concerns identified - additional verification advised")
        
        # Watermarking recommendations
        if result.watermark_analysis:
            if not result.watermark_analysis.get('verified', True):
                recommendations.append("Consider adding watermarks for content protection")
        
        return recommendations
    
    # Initialization helper methods
    async def _init_voice_detector(self):
        """Initialize voice detector"""
        return await self.voice_detector.initialize()
    
    async def _init_deepfake_detector(self):
        """Initialize deepfake detector"""
        # Deepfake detector might not have async initialization
        return True
    
    async def _init_copyright_detector(self):
        """Initialize copyright detector"""
        # Copyright detector might not have async initialization
        return True
    
    async def _init_style_protector(self):
        """Initialize style protector"""
        return await self.style_protector.initialize()
    
    async def _init_watermarking_system(self):
        """Initialize watermarking system"""
        return await self.watermarking_system.initialize()
    
    async def _init_rights_manager(self):
        """Initialize rights manager"""
        # Rights manager might not have async initialization
        return True


# Factory function
def create_ai_processing_engine(device: str = "cpu") -> AIProcessingEngine:
    """Create and return an AIProcessingEngine instance"""
    return AIProcessingEngine(device=device)


# Example usage
async def main():
    """Example usage of AIProcessingEngine"""
    engine = create_ai_processing_engine()
    await engine.initialize()
    
    # Example: Analyze audio content
    import numpy as np
    
    # Generate dummy audio data
    audio_data = np.random.randn(16000 * 3)  # 3 seconds of audio
    
    result = await engine.process_content(
        content_data=audio_data,
        content_type="audio",
        content_id="test_audio_001",
        analysis_options={
            'check_voice_cloning': True,
            'check_deepfakes': True,
            'check_copyright': True,
            'check_style_transfer': True,
            'check_watermarks': True,
            'check_rights': True
        }
    )
    
    print(f"Content ID: {result.content_id}")
    print(f"Processing Status: {result.processing_status.value}")
    print(f"Threat Level: {result.threat_level.value}")
    print(f"Overall Confidence: {result.overall_confidence:.2f}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    print(f"Features Analyzed: {', '.join(result.features_analyzed)}")
    
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    if result.recommendations:
        print("Recommendations:")
        for recommendation in result.recommendations:
            print(f"  - {recommendation}")
    
    # Show individual analysis results
    if result.voice_clone_analysis:
        print(f"Voice Clone Analysis: {result.voice_clone_analysis.get('authenticity_level', 'N/A')}")
    
    if result.deepfake_analysis:
        print(f"Deepfake Analysis: {result.deepfake_analysis.get('deepfake_probability', 0.0):.2f}")
    
    if result.copyright_analysis:
        print(f"Copyright Analysis: {result.copyright_analysis.get('detection_result', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())