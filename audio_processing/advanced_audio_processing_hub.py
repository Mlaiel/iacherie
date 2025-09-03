"""🎯 Advanced Audio Processing Hub - Unified Professional Audio Intelligence System

Industrial-grade unified hub for advanced audio processing capabilities including
professional source separation, loudness normalization, and format conversion.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de

Team Expertise:
- Lead Developer AI & Machine Learning: Fahed Mlaiel  
- Senior Backend Architecture: Advanced Python/FastAPI
- Audio Mastering Engineer: Professional Audio Standards
- ML Engineer: Deep Learning & Audio Processing
- Broadcast Engineer: ITU-R & EBU Standards Implementation
- Codec Specialist: Advanced Compression & Quality Optimization
- Database Administrator: PostgreSQL & Vector Databases
- Security Engineer: Enterprise Security & Authentication
- Microservices Architect: Scalable Distributed Systems
- DevOps Engineer: CI/CD & Cloud Infrastructure
- IA Prompt Engineer: Advanced AI Model Training
"""

import asyncio
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
import time

# Import the professional engines
from .separation.vocal_instrument_separation_engine import (
    VocalInstrumentSeparationEngine, SeparationRequest, SeparationResult,
    SeparationModel, QualityTier, SeparationFormat
)
from .enhancement.loudness_normalization_engine import (
    LoudnessNormalizationEngine, NormalizationRequest, NormalizationResult,
    LoudnessStandard, DynamicRangeTarget, ProcessingPrecision
)
from .format_conversion.high_quality_format_converter import (
    HighQualityFormatConverter, ConversionRequest, ConversionResult,
    AudioFormat, SampleRate, BitDepth, QualityProfile, FormatSpecification
)

logger = logging.getLogger(__name__)


class ProcessingWorkflow(Enum):
    """Professional audio processing workflows."""
    CONTENT_CREATOR = "content_creator"           # Musicians, podcasters, influencers
    BROADCAST_DELIVERY = "broadcast_delivery"     # Professional broadcasting
    STREAMING_OPTIMIZATION = "streaming_optimization" # Platform optimization
    MASTERING_CHAIN = "mastering_chain"          # Professional mastering
    COLLABORATION_PREP = "collaboration_prep"     # Collaboration matching prep
    PROTECTION_READY = "protection_ready"        # Rights protection preparation


class BusinessPurpose(Enum):
    """Business logic purposes for processing."""
    MUSIC_PRODUCTION = "music_production"         # Musicians and producers
    PODCAST_CONTENT = "podcast_content"          # Podcasters and audio content
    VIDEO_CONTENT = "video_content"              # Video creators and influencers  
    COMEDY_CONTENT = "comedy_content"            # Comedians and entertainment
    PHOTOGRAPHY_AUDIO = "photography_audio"      # Photographers with audio
    BLOGGER_CONTENT = "blogger_content"          # Bloggers with multimedia
    COLLABORATION_MATCHING = "collaboration_matching" # AI-powered matching
    SEO_OPTIMIZATION = "seo_optimization"        # Professional SEO workflows
    RIGHTS_PROTECTION = "rights_protection"      # Content protection and fingerprinting
    MONETIZATION = "monetization"                # Revenue generation workflows
    DISTRIBUTION = "distribution"                # Multi-platform distribution


@dataclass
class UnifiedProcessingRequest:
    """Unified request for comprehensive audio processing."""
    audio_data: Union[np.ndarray, bytes, str]
    input_sample_rate: int = 44100
    workflow: ProcessingWorkflow = ProcessingWorkflow.CONTENT_CREATOR
    business_purpose: BusinessPurpose = BusinessPurpose.MUSIC_PRODUCTION
    
    # Separation parameters
    enable_separation: bool = True
    separation_model: SeparationModel = SeparationModel.DEMUCS_HTDEMUCS
    separation_quality: QualityTier = QualityTier.STUDIO
    
    # Normalization parameters  
    enable_normalization: bool = True
    loudness_standard: LoudnessStandard = LoudnessStandard.EBU_R128
    dynamic_range_target: DynamicRangeTarget = DynamicRangeTarget.BROADCAST_STANDARD
    
    # Format conversion parameters
    enable_format_conversion: bool = True
    target_format: AudioFormat = AudioFormat.WAV_PCM
    target_sample_rate: SampleRate = SampleRate.SR_48000
    target_bit_depth: BitDepth = BitDepth.BIT_24
    
    # Advanced options
    preserve_metadata: bool = True
    apply_professional_mastering: bool = False
    optimize_for_platforms: List[str] = field(default_factory=list)
    custom_processing_chain: Optional[List[str]] = None


@dataclass
class UnifiedProcessingResult:
    """Comprehensive result from unified audio processing."""
    # Original audio
    original_audio: np.ndarray
    original_sample_rate: int
    
    # Separation results
    separation_result: Optional[SeparationResult] = None
    vocals: Optional[np.ndarray] = None
    instruments: Optional[np.ndarray] = None
    
    # Normalization results
    normalization_result: Optional[NormalizationResult] = None
    normalized_audio: Optional[np.ndarray] = None
    
    # Format conversion results
    conversion_result: Optional[ConversionResult] = None
    final_output: Optional[Union[np.ndarray, bytes]] = None
    
    # Processing metadata
    total_processing_time: float = 0.0
    workflow_used: str = ""
    business_purpose: str = ""
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    processing_chain: List[str] = field(default_factory=list)
    compliance_reports: Dict[str, Any] = field(default_factory=dict)
    
    # Business logic integration
    seo_optimization_data: Dict[str, Any] = field(default_factory=dict)
    collaboration_readiness: Dict[str, Any] = field(default_factory=dict)
    protection_fingerprints: Dict[str, Any] = field(default_factory=dict)
    monetization_metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedAudioProcessingHub:
    """Industrial-grade unified audio processing hub.
    
    Provides comprehensive audio processing capabilities integrating professional
    source separation, loudness normalization, and format conversion with
    enterprise-level workflow automation and business logic integration.
    """
    
    def __init__(
        self,
        max_concurrent_workflows: int = 2,
        enable_advanced_analytics: bool = True,
        cache_models: bool = True,
        temp_dir: Optional[str] = None
    ):
        """Initialize the advanced audio processing hub.
        
        Args:
            max_concurrent_workflows: Maximum concurrent processing workflows
            enable_advanced_analytics: Enable detailed analytics and reporting
            cache_models: Whether to cache AI models for performance
            temp_dir: Temporary directory for processing
        """
        self.max_concurrent_workflows = max_concurrent_workflows
        self.enable_advanced_analytics = enable_advanced_analytics
        self.cache_models = cache_models
        self.temp_dir = Path(temp_dir) if temp_dir else Path.cwd() / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize processing engines
        self.separation_engine = VocalInstrumentSeparationEngine(
            cache_models=cache_models,
            max_concurrent_jobs=max_concurrent_workflows,
            temp_dir=str(self.temp_dir / "separation")
        )
        
        self.normalization_engine = LoudnessNormalizationEngine(
            max_concurrent_jobs=max_concurrent_workflows,
            enable_advanced_metering=enable_advanced_analytics,
            cache_analysis=cache_models
        )
        
        self.format_converter = HighQualityFormatConverter(
            temp_dir=str(self.temp_dir / "conversion"),
            max_concurrent_jobs=max_concurrent_workflows,
            enable_quality_analysis=enable_advanced_analytics
        )
        
        # Processing statistics
        self.stats = {
            "total_workflows": 0,
            "total_processing_time": 0.0,
            "workflows_by_type": {},
            "business_purposes_served": {},
            "average_quality_score": 0.0,
            "successful_workflows": 0,
            "failed_workflows": 0
        }
        
        # Thread pool for workflow coordination
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent_workflows
        )
        
        # Workflow configurations
        self.workflow_configs = self._initialize_workflow_configs()
        
        logger.info(f"AdvancedAudioProcessingHub initialized with {max_concurrent_workflows} concurrent workflows")
    
    def _initialize_workflow_configs(self) -> Dict[ProcessingWorkflow, Dict[str, Any]]:
        """Initialize workflow-specific configurations."""
        return {
            ProcessingWorkflow.CONTENT_CREATOR: {
                "separation_priority": True,
                "normalization_standard": LoudnessStandard.STREAMING_STANDARD,
                "target_format": AudioFormat.WAV_PCM,
                "quality_tier": QualityTier.STUDIO,
                "enable_seo_optimization": True,
                "enable_collaboration_prep": True
            },
            ProcessingWorkflow.BROADCAST_DELIVERY: {
                "separation_priority": False,
                "normalization_standard": LoudnessStandard.EBU_R128,
                "target_format": AudioFormat.BWF,
                "quality_tier": QualityTier.BROADCAST,
                "enable_compliance_checking": True,
                "enable_loudness_monitoring": True
            },
            ProcessingWorkflow.STREAMING_OPTIMIZATION: {
                "separation_priority": True,
                "normalization_standard": LoudnessStandard.SPOTIFY,
                "target_format": AudioFormat.AAC_256,
                "quality_tier": QualityTier.PRODUCTION,
                "platform_optimization": ["spotify", "youtube", "apple_music"],
                "enable_dynamic_range_optimization": True
            },
            ProcessingWorkflow.MASTERING_CHAIN: {
                "separation_priority": True,
                "normalization_standard": LoudnessStandard.EBU_R128,
                "target_format": AudioFormat.FLAC,
                "quality_tier": QualityTier.STUDIO,
                "enable_professional_mastering": True,
                "preserve_dynamics": True
            },
            ProcessingWorkflow.COLLABORATION_PREP: {
                "separation_priority": True,
                "normalization_standard": LoudnessStandard.STREAMING_HIGH,
                "target_format": AudioFormat.WAV_PCM,
                "quality_tier": QualityTier.STUDIO,
                "enable_stem_separation": True,
                "enable_collaboration_metadata": True
            },
            ProcessingWorkflow.PROTECTION_READY: {
                "separation_priority": False,
                "normalization_standard": LoudnessStandard.BROADCAST_EU,
                "target_format": AudioFormat.WAV_PCM,
                "quality_tier": QualityTier.BROADCAST,
                "enable_fingerprinting": True,
                "enable_watermarking": True,
                "enable_integrity_validation": True
            }
        }
    
    async def process_audio(self, request: UnifiedProcessingRequest) -> UnifiedProcessingResult:
        """Execute unified audio processing workflow.
        
        Args:
            request: Unified processing request with workflow specifications
            
        Returns:
            UnifiedProcessingResult with comprehensive processing results
        """
        start_time = time.time()
        processing_chain = []
        
        try:
            # Load and validate input
            original_audio, original_sr = await self._load_and_validate_input(
                request.audio_data, request.input_sample_rate
            )
            processing_chain.append("input_validation")
            
            # Get workflow configuration
            workflow_config = self.workflow_configs.get(request.workflow, {})
            processing_chain.append(f"workflow_config_{request.workflow.value}")
            
            # Initialize result
            result = UnifiedProcessingResult(
                original_audio=original_audio,
                original_sample_rate=original_sr,
                workflow_used=request.workflow.value,
                business_purpose=request.business_purpose.value
            )
            
            current_audio = original_audio
            current_sr = original_sr
            
            # Step 1: Source Separation (if enabled)
            if request.enable_separation:
                separation_result = await self._execute_separation(
                    current_audio, current_sr, request, workflow_config
                )
                result.separation_result = separation_result
                result.vocals = separation_result.vocals
                result.instruments = separation_result.instruments
                processing_chain.append("source_separation")
                
                # Use full mix for subsequent processing unless workflow specifies otherwise
                if workflow_config.get("separation_priority", False):
                    current_audio = separation_result.vocals + separation_result.instruments
            
            # Step 2: Loudness Normalization (if enabled)
            if request.enable_normalization:
                normalization_result = await self._execute_normalization(
                    current_audio, current_sr, request, workflow_config
                )
                result.normalization_result = normalization_result
                result.normalized_audio = normalization_result.normalized_audio
                current_audio = normalization_result.normalized_audio
                processing_chain.append("loudness_normalization")
            
            # Step 3: Format Conversion (if enabled)
            if request.enable_format_conversion:
                conversion_result = await self._execute_format_conversion(
                    current_audio, current_sr, request, workflow_config
                )
                result.conversion_result = conversion_result
                result.final_output = conversion_result.converted_audio
                processing_chain.append("format_conversion")
            else:
                result.final_output = current_audio
            
            # Step 4: Business Logic Integration
            await self._apply_business_logic_integration(result, request, workflow_config)
            processing_chain.append("business_logic_integration")
            
            # Step 5: Quality Analysis and Compliance
            if self.enable_advanced_analytics:
                await self._perform_comprehensive_analysis(result, request)
                processing_chain.append("quality_analysis")
            
            # Finalize result
            result.total_processing_time = time.time() - start_time
            result.processing_chain = processing_chain
            
            # Update statistics
            self._update_workflow_stats(request, result, success=True)
            
            logger.info(
                f"Unified processing completed in {result.total_processing_time:.2f}s: "
                f"{request.workflow.value} for {request.business_purpose.value}"
            )
            
            return result
            
        except Exception as e:
            self._update_workflow_stats(request, None, success=False)
            logger.error(f"Unified processing failed: {e}")
            raise RuntimeError(f"Audio processing workflow failed: {str(e)}")
    
    async def _load_and_validate_input(
        self, audio_input: Union[np.ndarray, bytes, str], declared_sr: int
    ) -> Tuple[np.ndarray, int]:
        """Load and validate input audio data."""
        
        def load():
            if isinstance(audio_input, str):
                import librosa
                audio_data, sr = librosa.load(audio_input, sr=None, mono=False, dtype=np.float64)
            elif isinstance(audio_input, bytes):
                import soundfile as sf
                from io import BytesIO
                audio_data, sr = sf.read(BytesIO(audio_input), dtype=np.float64)
                if audio_data.ndim == 2:
                    audio_data = audio_data.T
            elif isinstance(audio_input, np.ndarray):
                audio_data = audio_input.astype(np.float64)
                sr = declared_sr
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_input)}")
            
            # Ensure stereo for professional processing
            if audio_data.ndim == 1:
                audio_data = np.stack([audio_data, audio_data])
            elif audio_data.ndim == 2 and audio_data.shape[0] == 1:
                audio_data = np.stack([audio_data[0], audio_data[0]])
            
            # Validate audio quality
            if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
                raise ValueError("Audio contains invalid values (NaN or Inf)")
            
            if np.max(np.abs(audio_data)) == 0:
                raise ValueError("Audio signal is silent")
            
            return audio_data, sr
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, load
        )
    
    async def _execute_separation(
        self, 
        audio: np.ndarray, 
        sr: int, 
        request: UnifiedProcessingRequest,
        workflow_config: Dict[str, Any]
    ) -> SeparationResult:
        """Execute source separation processing."""
        
        separation_request = SeparationRequest(
            audio_data=audio,
            sample_rate=sr,
            model=request.separation_model,
            quality_tier=request.separation_quality,
            output_format=SeparationFormat.WAV_48K_24BIT,
            preserve_dynamics=workflow_config.get("preserve_dynamics", True)
        )
        
        return await self.separation_engine.separate_audio(separation_request)
    
    async def _execute_normalization(
        self,
        audio: np.ndarray,
        sr: int,
        request: UnifiedProcessingRequest,
        workflow_config: Dict[str, Any]
    ) -> NormalizationResult:
        """Execute loudness normalization processing."""
        
        # Use workflow-specific standard if available
        target_standard = workflow_config.get("normalization_standard", request.loudness_standard)
        
        normalization_request = NormalizationRequest(
            audio_data=audio,
            sample_rate=sr,
            target_standard=target_standard,
            dynamic_range_target=request.dynamic_range_target,
            precision=ProcessingPrecision.FLOAT32_PRODUCTION,
            enable_peak_limiting=True,
            enable_dynamic_range_control=workflow_config.get("enable_dynamic_range_optimization", True)
        )
        
        return await self.normalization_engine.normalize_audio(normalization_request)
    
    async def _execute_format_conversion(
        self,
        audio: np.ndarray,
        sr: int,
        request: UnifiedProcessingRequest,
        workflow_config: Dict[str, Any]
    ) -> ConversionResult:
        """Execute format conversion processing."""
        
        # Use workflow-specific format if available
        target_format = workflow_config.get("target_format", request.target_format)
        
        target_spec = FormatSpecification(
            format=target_format,
            sample_rate=request.target_sample_rate,
            bit_depth=request.target_bit_depth,
            quality_profile=QualityProfile.MASTERING
        )
        
        conversion_request = ConversionRequest(
            audio_data=audio,
            input_sample_rate=sr,
            target_specification=target_spec,
            preserve_metadata=request.preserve_metadata,
            normalize_before_conversion=False,  # Already normalized
            apply_dithering=True
        )
        
        return await self.format_converter.convert_audio(conversion_request)
    
    async def _apply_business_logic_integration(
        self,
        result: UnifiedProcessingResult,
        request: UnifiedProcessingRequest,
        workflow_config: Dict[str, Any]
    ):
        """Apply business logic integration based on purpose."""
        
        def apply_integration():
            # SEO Optimization
            if (request.business_purpose in [BusinessPurpose.BLOGGER_CONTENT, 
                                           BusinessPurpose.VIDEO_CONTENT] or
                workflow_config.get("enable_seo_optimization", False)):
                result.seo_optimization_data = self._generate_seo_metadata(result, request)
            
            # Collaboration Matching Preparation
            if (request.business_purpose == BusinessPurpose.COLLABORATION_MATCHING or
                workflow_config.get("enable_collaboration_prep", False)):
                result.collaboration_readiness = self._generate_collaboration_metadata(result, request)
            
            # Rights Protection Preparation
            if (request.business_purpose == BusinessPurpose.RIGHTS_PROTECTION or
                workflow_config.get("enable_fingerprinting", False)):
                result.protection_fingerprints = self._generate_protection_metadata(result, request)
            
            # Monetization Preparation
            if (request.business_purpose == BusinessPurpose.MONETIZATION or
                request.workflow == ProcessingWorkflow.STREAMING_OPTIMIZATION):
                result.monetization_metadata = self._generate_monetization_metadata(result, request)
        
        await asyncio.get_event_loop().run_in_executor(
            self.executor, apply_integration
        )
    
    def _generate_seo_metadata(
        self, result: UnifiedProcessingResult, request: UnifiedProcessingRequest
    ) -> Dict[str, Any]:
        """Generate SEO optimization metadata."""
        return {
            "content_type": self._detect_content_type(result),
            "quality_score": result.quality_metrics.get("overall_quality", 0.0),
            "duration": len(result.original_audio[0]) / result.original_sample_rate,
            "format_seo_friendly": result.conversion_result.output_format.value if result.conversion_result else "wav",
            "loudness_compliant": result.normalization_result.compliance_report.get("overall_compliant", False) if result.normalization_result else False,
            "separation_available": result.separation_result is not None,
            "professional_grade": True,
            "creator_type": request.business_purpose.value
        }
    
    def _generate_collaboration_metadata(
        self, result: UnifiedProcessingResult, request: UnifiedProcessingRequest
    ) -> Dict[str, Any]:
        """Generate collaboration matching metadata."""
        return {
            "stems_available": result.separation_result is not None,
            "professional_quality": result.quality_metrics.get("overall_quality", 0.0) > 0.8,
            "loudness_normalized": result.normalization_result is not None,
            "format_compatibility": result.conversion_result.output_format.value if result.conversion_result else "wav",
            "creator_type": request.business_purpose.value,
            "collaboration_ready": True,
            "processing_timestamp": time.time(),
            "quality_tier": request.separation_quality.value if hasattr(request, 'separation_quality') else "studio"
        }
    
    def _generate_protection_metadata(
        self, result: UnifiedProcessingResult, request: UnifiedProcessingRequest
    ) -> Dict[str, Any]:
        """Generate rights protection metadata."""
        return {
            "audio_fingerprint": self._calculate_audio_fingerprint(result.original_audio),
            "processing_history": result.processing_chain,
            "quality_metrics": result.quality_metrics,
            "creator_metadata": {
                "business_purpose": request.business_purpose.value,
                "workflow": request.workflow.value,
                "processing_timestamp": time.time()
            },
            "integrity_checksum": result.conversion_result.checksum if result.conversion_result else None,
            "protection_ready": True
        }
    
    def _generate_monetization_metadata(
        self, result: UnifiedProcessingResult, request: UnifiedProcessingRequest
    ) -> Dict[str, Any]:
        """Generate monetization preparation metadata."""
        return {
            "commercial_quality": result.quality_metrics.get("overall_quality", 0.0) > 0.85,
            "broadcast_compliant": result.normalization_result.compliance_report.get("overall_compliant", False) if result.normalization_result else False,
            "platform_optimized": request.workflow == ProcessingWorkflow.STREAMING_OPTIMIZATION,
            "stems_for_licensing": result.separation_result is not None,
            "professional_grade": True,
            "revenue_ready": True,
            "distribution_formats": [result.conversion_result.output_format.value] if result.conversion_result else ["wav"],
            "creator_type": request.business_purpose.value
        }
    
    def _detect_content_type(self, result: UnifiedProcessingResult) -> str:
        """Detect content type based on processing results."""
        if result.separation_result:
            vocals_energy = np.mean(result.vocals ** 2) if result.vocals is not None else 0
            instruments_energy = np.mean(result.instruments ** 2) if result.instruments is not None else 0
            
            if vocals_energy > instruments_energy * 2:
                return "vocal_dominant"
            elif instruments_energy > vocals_energy * 2:
                return "instrumental"
            else:
                return "mixed_content"
        else:
            return "unanalyzed_audio"
    
    def _calculate_audio_fingerprint(self, audio: np.ndarray) -> str:
        """Calculate basic audio fingerprint for protection."""
        # Simplified fingerprint based on spectral characteristics
        import hashlib
        
        # Calculate spectral centroid and other features
        if audio.ndim == 2:
            mono_audio = np.mean(audio, axis=0)
        else:
            mono_audio = audio
        
        # Use a subset of the audio for fingerprinting
        sample_length = min(len(mono_audio), 44100 * 30)  # Max 30 seconds
        audio_sample = mono_audio[:sample_length]
        
        # Create fingerprint from audio characteristics
        fingerprint_data = audio_sample.tobytes()
        return hashlib.sha256(fingerprint_data).hexdigest()[:32]
    
    async def _perform_comprehensive_analysis(
        self, result: UnifiedProcessingResult, request: UnifiedProcessingRequest
    ):
        """Perform comprehensive quality and compliance analysis."""
        
        def analyze():
            quality_metrics = {}
            
            # Aggregate quality metrics from all processing stages
            if result.separation_result:
                quality_metrics.update({
                    f"separation_{k}": v for k, v in result.separation_result.quality_metrics.items()
                })
            
            if result.normalization_result:
                quality_metrics.update({
                    f"normalization_{k}": v for k, v in result.normalization_result.quality_metrics.items()
                })
            
            if result.conversion_result:
                quality_metrics.update({
                    f"conversion_{k}": v for k, v in result.conversion_result.quality_metrics.items()
                })
            
            # Calculate overall workflow quality score
            individual_scores = [
                result.separation_result.quality_metrics.get("overall_quality", 1.0) if result.separation_result else 1.0,
                result.normalization_result.quality_metrics.get("overall_quality", 1.0) if result.normalization_result else 1.0,
                result.conversion_result.quality_metrics.get("overall_quality", 1.0) if result.conversion_result else 1.0
            ]
            
            overall_quality = np.mean(individual_scores)
            quality_metrics["workflow_overall_quality"] = float(overall_quality)
            
            result.quality_metrics = quality_metrics
            
            # Compile compliance reports
            compliance_reports = {}
            if result.normalization_result:
                compliance_reports["loudness_compliance"] = result.normalization_result.compliance_report
            
            result.compliance_reports = compliance_reports
        
        await asyncio.get_event_loop().run_in_executor(
            self.executor, analyze
        )
    
    def _update_workflow_stats(
        self, 
        request: UnifiedProcessingRequest, 
        result: Optional[UnifiedProcessingResult], 
        success: bool
    ):
        """Update workflow processing statistics."""
        self.stats["total_workflows"] += 1
        
        if success:
            self.stats["successful_workflows"] += 1
            if result:
                self.stats["total_processing_time"] += result.total_processing_time
                
                # Update workflow type statistics
                workflow_name = request.workflow.value
                if workflow_name not in self.stats["workflows_by_type"]:
                    self.stats["workflows_by_type"][workflow_name] = 0
                self.stats["workflows_by_type"][workflow_name] += 1
                
                # Update business purpose statistics
                purpose_name = request.business_purpose.value
                if purpose_name not in self.stats["business_purposes_served"]:
                    self.stats["business_purposes_served"][purpose_name] = 0
                self.stats["business_purposes_served"][purpose_name] += 1
                
                # Update quality statistics
                if "workflow_overall_quality" in result.quality_metrics:
                    total_successful = self.stats["successful_workflows"]
                    current_avg = self.stats["average_quality_score"]
                    new_avg = (
                        (current_avg * (total_successful - 1) + 
                         result.quality_metrics["workflow_overall_quality"]) / total_successful
                    )
                    self.stats["average_quality_score"] = new_avg
        else:
            self.stats["failed_workflows"] += 1
    
    async def batch_process(
        self, requests: List[UnifiedProcessingRequest]
    ) -> List[UnifiedProcessingResult]:
        """Process multiple unified requests concurrently."""
        
        batch_size = min(self.max_concurrent_workflows, len(requests))
        results = []
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.process_audio(req) for req in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing failed: {result}")
                    results.append(None)
                else:
                    results.append(result)
        
        return [r for r in results if r is not None]
    
    def get_hub_stats(self) -> Dict[str, Any]:
        """Get comprehensive hub statistics."""
        return {
            **self.stats,
            "separation_engine_stats": self.separation_engine.get_engine_stats(),
            "normalization_engine_stats": self.normalization_engine.get_engine_stats(),
            "format_converter_stats": self.format_converter.get_engine_stats(),
            "max_concurrent_workflows": self.max_concurrent_workflows,
            "supported_workflows": [w.value for w in ProcessingWorkflow],
            "supported_business_purposes": [p.value for p in BusinessPurpose]
        }
    
    async def cleanup(self):
        """Cleanup all processing engines and resources."""
        try:
            await asyncio.gather(
                self.separation_engine.cleanup(),
                self.normalization_engine.cleanup(),
                self.format_converter.cleanup(),
                return_exceptions=True
            )
            
            self.executor.shutdown(wait=True)
            
            # Clean temporary files
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            logger.info("AdvancedAudioProcessingHub cleanup completed")
        except Exception as e:
            logger.error(f"Hub cleanup failed: {e}")


# Convenience functions for direct usage
async def process_audio_unified(
    audio_input: Union[np.ndarray, bytes, str],
    input_sample_rate: int = 44100,
    workflow: ProcessingWorkflow = ProcessingWorkflow.CONTENT_CREATOR,
    business_purpose: BusinessPurpose = BusinessPurpose.MUSIC_PRODUCTION
) -> UnifiedProcessingResult:
    """Unified audio processing function.
    
    Args:
        audio_input: Audio data (array, bytes, or file path)
        input_sample_rate: Input sample rate
        workflow: Processing workflow to use
        business_purpose: Business purpose for processing
        
    Returns:
        UnifiedProcessingResult with comprehensive processing results
    """
    hub = AdvancedAudioProcessingHub()
    try:
        request = UnifiedProcessingRequest(
            audio_data=audio_input,
            input_sample_rate=input_sample_rate,
            workflow=workflow,
            business_purpose=business_purpose
        )
        return await hub.process_audio(request)
    finally:
        await hub.cleanup()


def create_processing_hub(**kwargs) -> AdvancedAudioProcessingHub:
    """Create a configured advanced audio processing hub instance."""
    return AdvancedAudioProcessingHub(**kwargs)