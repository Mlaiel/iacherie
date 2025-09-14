"""Enhancement Pipeline
Automated enhancement pipeline with multiple processing stages and AI orchestration.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Union, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import time

# Import enhancement modules
from .color_enhancement import ColorEnhancementEngine, ColorEnhancementConfig
from .noise_reduction import NoiseReductionEngine, NoiseReductionConfig
from .sharpness_enhancement import SharpnessEnhancementEngine, SharpnessConfig
from .contrast_optimization import ContrastOptimizationEngine, ContrastConfig
from .ai_filter_engine import AIFilterEngine, FilterConfig

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """Available processing stages in the pipeline."""
    NOISE_REDUCTION = "noise_reduction"
    CONTRAST_OPTIMIZATION = "contrast_optimization"
    COLOR_ENHANCEMENT = "color_enhancement"
    SHARPNESS_ENHANCEMENT = "sharpness_enhancement"
    AI_FILTERING = "ai_filtering"
    CUSTOM = "custom"

@dataclass
class StageConfig:
    """Configuration for a single processing stage."""
    stage: ProcessingStage
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1 = highest, 10 = lowest
    parallel_safe: bool = True  # Can be run in parallel with other stages
    
@dataclass
class PipelineConfig:
    """Configuration for the entire enhancement pipeline."""
    stages: List[StageConfig] = field(default_factory=list)
    auto_optimize: bool = True  # Automatically optimize stage order and parameters
    quality_target: str = "balanced"  # "speed", "balanced", "quality"
    parallel_processing: bool = True
    intermediate_files: bool = False  # Save intermediate results
    progress_callback: Optional[Callable] = None
    
    # Quality thresholds
    min_quality_improvement: float = 0.05  # Minimum improvement to apply stage
    max_processing_time: float = 300.0  # Maximum processing time in seconds
    
    # Adaptive processing
    content_aware: bool = True  # Adapt pipeline based on content analysis
    real_time_mode: bool = False  # Optimize for real-time processing

class ContentAnalyzer:
    """Analyze content to optimize pipeline configuration."""
    
    @staticmethod
    async def analyze_content(file_path: Path) -> Dict[str, Any]:
        """Analyze content characteristics to guide pipeline optimization."""
        try:
            import cv2
            
            file_ext = file_path.suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                return await ContentAnalyzer._analyze_image(file_path)
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                return await ContentAnalyzer._analyze_video(file_path)
            elif file_ext in ['.wav', '.mp3', '.flac', '.m4a', '.aac']:
                return await ContentAnalyzer._analyze_audio(file_path)
            else:
                return {"content_type": "unknown", "characteristics": {}}
                
        except Exception as e:
            logger.warning(f"Content analysis failed: {e}")
            return {"content_type": "unknown", "characteristics": {}, "error": str(e)}
    
    @staticmethod
    async def _analyze_image(file_path: Path) -> Dict[str, Any]:
        """Analyze image content characteristics."""
        import cv2
        
        image = cv2.imread(str(file_path))
        if image is None:
            return {"content_type": "image", "characteristics": {}, "error": "Could not load image"}
        
        # Basic characteristics
        height, width = image.shape[:2]
        total_pixels = height * width
        
        # Color analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Noise estimation
        noise_level = np.std(cv2.Laplacian(gray, cv2.CV_64F))
        
        # Contrast analysis
        contrast = np.std(gray)
        
        # Blur estimation
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness analysis
        brightness = np.mean(gray)
        
        # Color saturation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv[:, :, 1])
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / total_pixels
        
        characteristics = {
            "resolution": f"{width}x{height}",
            "megapixels": total_pixels / 1e6,
            "noise_level": float(noise_level),
            "contrast_level": float(contrast),
            "blur_score": float(blur_score),
            "brightness": float(brightness),
            "saturation": float(saturation),
            "edge_density": float(edge_density),
            "is_low_light": brightness < 80,
            "is_noisy": noise_level > 20,
            "is_blurry": blur_score < 100,
            "is_low_contrast": contrast < 40,
            "is_oversaturated": saturation > 150,
            "is_high_detail": edge_density > 0.1
        }
        
        return {
            "content_type": "image",
            "characteristics": characteristics,
            "recommended_stages": ContentAnalyzer._recommend_image_stages(characteristics)
        }
    
    @staticmethod
    async def _analyze_video(file_path: Path) -> Dict[str, Any]:
        """Analyze video content characteristics."""
        import cv2
        
        cap = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            return {"content_type": "video", "characteristics": {}, "error": "Could not open video"}
        
        # Video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames for analysis
        sample_frames = []
        for i in range(0, min(frame_count, 30), frame_count // 10 if frame_count > 10 else 1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                sample_frames.append(frame)
        
        cap.release()
        
        if not sample_frames:
            return {"content_type": "video", "characteristics": {}, "error": "Could not read frames"}
        
        # Analyze sample frames
        noise_levels = []
        contrast_levels = []
        brightness_levels = []
        
        for frame in sample_frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            noise_levels.append(np.std(cv2.Laplacian(gray, cv2.CV_64F)))
            contrast_levels.append(np.std(gray))
            brightness_levels.append(np.mean(gray))
        
        characteristics = {
            "resolution": f"{width}x{height}",
            "fps": float(fps),
            "duration": frame_count / fps if fps > 0 else 0,
            "frame_count": frame_count,
            "avg_noise_level": float(np.mean(noise_levels)),
            "avg_contrast": float(np.mean(contrast_levels)),
            "avg_brightness": float(np.mean(brightness_levels)),
            "is_hd": width >= 1280 and height >= 720,
            "is_4k": width >= 3840 and height >= 2160,
            "is_high_fps": fps > 30,
            "is_long_duration": (frame_count / fps if fps > 0 else 0) > 300  # 5 minutes
        }
        
        return {
            "content_type": "video",
            "characteristics": characteristics,
            "recommended_stages": ContentAnalyzer._recommend_video_stages(characteristics)
        }
    
    @staticmethod
    async def _analyze_audio(file_path: Path) -> Dict[str, Any]:
        """Analyze audio content characteristics."""
        try:
            import librosa
            
            # Load audio
            audio, sr = librosa.load(str(file_path), sr=None, duration=30)  # Sample first 30 seconds
            
            # Audio characteristics
            duration = len(audio) / sr
            rms_energy = np.sqrt(np.mean(audio**2))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio)[0])
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)[0])
            
            # Estimate noise level
            noise_level = np.std(audio[:int(0.5 * sr)])  # First 0.5 seconds as noise estimate
            
            characteristics = {
                "sample_rate": sr,
                "duration": duration,
                "rms_energy": float(rms_energy),
                "zero_crossing_rate": float(zero_crossing_rate),
                "spectral_centroid": float(spectral_centroid),
                "estimated_noise_level": float(noise_level),
                "is_speech": zero_crossing_rate > 0.1 and spectral_centroid < 3000,
                "is_music": spectral_centroid > 1000 and rms_energy > 0.01,
                "is_noisy": noise_level > 0.02,
                "is_low_quality": sr < 44100
            }
            
            return {
                "content_type": "audio",
                "characteristics": characteristics,
                "recommended_stages": ContentAnalyzer._recommend_audio_stages(characteristics)
            }
            
        except ImportError:
            logger.warning("Librosa not available for audio analysis")
            return {"content_type": "audio", "characteristics": {}, "error": "Librosa not available"}
        except Exception as e:
            return {"content_type": "audio", "characteristics": {}, "error": str(e)}
    
    @staticmethod
    def _recommend_image_stages(characteristics: Dict) -> List[ProcessingStage]:
        """Recommend processing stages for image based on characteristics."""
        stages = []
        
        if characteristics.get("is_noisy", False):
            stages.append(ProcessingStage.NOISE_REDUCTION)
        
        if characteristics.get("is_low_contrast", False):
            stages.append(ProcessingStage.CONTRAST_OPTIMIZATION)
        
        if characteristics.get("brightness", 128) < 100 or characteristics.get("saturation", 128) < 100:
            stages.append(ProcessingStage.COLOR_ENHANCEMENT)
        
        if characteristics.get("is_blurry", False):
            stages.append(ProcessingStage.SHARPNESS_ENHANCEMENT)
        
        # Always include AI filtering for creative enhancement
        stages.append(ProcessingStage.AI_FILTERING)
        
        return stages
    
    @staticmethod
    def _recommend_video_stages(characteristics: Dict) -> List[ProcessingStage]:
        """Recommend processing stages for video based on characteristics."""
        stages = []
        
        if characteristics.get("avg_noise_level", 0) > 15:
            stages.append(ProcessingStage.NOISE_REDUCTION)
        
        if characteristics.get("avg_contrast", 50) < 40:
            stages.append(ProcessingStage.CONTRAST_OPTIMIZATION)
        
        if characteristics.get("avg_brightness", 128) < 100:
            stages.append(ProcessingStage.COLOR_ENHANCEMENT)
        
        # For video, be more conservative with processing
        if not characteristics.get("is_long_duration", False):
            stages.append(ProcessingStage.AI_FILTERING)
        
        return stages
    
    @staticmethod
    def _recommend_audio_stages(characteristics: Dict) -> List[ProcessingStage]:
        """Recommend processing stages for audio based on characteristics."""
        stages = []
        
        if characteristics.get("is_noisy", False):
            stages.append(ProcessingStage.NOISE_REDUCTION)
        
        return stages

class EnhancementPipeline:
    """Enterprise enhancement pipeline orchestrator with AI-powered optimization."""
    
    def __init__(self) -> None:
        self.config = PipelineConfig()
        self.engines = self._initialize_engines()
        self.processing_stats = {}
        
    def _initialize_engines(self) -> Dict[ProcessingStage, Any]:
        """Initialize all enhancement engines."""
        return {
            ProcessingStage.NOISE_REDUCTION: NoiseReductionEngine(),
            ProcessingStage.CONTRAST_OPTIMIZATION: ContrastOptimizationEngine(),
            ProcessingStage.COLOR_ENHANCEMENT: ColorEnhancementEngine(),
            ProcessingStage.SHARPNESS_ENHANCEMENT: SharpnessEnhancementEngine(),
            ProcessingStage.AI_FILTERING: AIFilterEngine()
        }
    
    async def process_pipeline(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        pipeline_config: Dict[str, any] = None
    ) -> Dict[str, any]:
        """Process multimedia through enhancement pipeline."""
        try:
            start_time = time.time()
            
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Update configuration if provided
            if pipeline_config:
                await self._update_config_from_dict(pipeline_config)
            
            # Analyze content if content-aware processing is enabled
            content_analysis = {}
            if self.config.content_aware:
                content_analysis = await ContentAnalyzer.analyze_content(input_path)
                await self._optimize_pipeline_for_content(content_analysis)
            
            # Execute pipeline
            pipeline_result = await self._execute_pipeline(input_path, output_path, content_analysis)
            
            total_time = time.time() - start_time
            
            return {
                "success": True,
                "pipeline_completed": True,
                "total_improvements": pipeline_result.get("total_improvement", 0.0),
                "processing_time": total_time,
                "stages_executed": pipeline_result.get("stages_executed", []),
                "content_analysis": content_analysis,
                "output_path": str(output_path),
                "pipeline_stats": pipeline_result.get("pipeline_stats", {}),
                "quality_metrics": pipeline_result.get("quality_metrics", {})
            }
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _update_config_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update pipeline configuration from dictionary."""
        if "auto_optimize" in config_dict:
            self.config.auto_optimize = config_dict["auto_optimize"]
        
        if "quality_target" in config_dict:
            self.config.quality_target = config_dict["quality_target"]
        
        if "parallel_processing" in config_dict:
            self.config.parallel_processing = config_dict["parallel_processing"]
        
        if "stages" in config_dict:
            self.config.stages = []
            for stage_dict in config_dict["stages"]:
                stage_config = StageConfig(
                    stage=ProcessingStage(stage_dict["stage"]),
                    enabled=stage_dict.get("enabled", True),
                    parameters=stage_dict.get("parameters", {}),
                    priority=stage_dict.get("priority", 1)
                )
                self.config.stages.append(stage_config)
    
    async def _optimize_pipeline_for_content(self, content_analysis: Dict) -> None:
        """Optimize pipeline configuration based on content analysis."""
        if not content_analysis.get("characteristics"):
            return
        
        characteristics = content_analysis["characteristics"]
        recommended_stages = content_analysis.get("recommended_stages", [])
        
        # If no stages configured, use recommended stages
        if not self.config.stages and recommended_stages:
            self.config.stages = []
            for i, stage in enumerate(recommended_stages):
                stage_config = StageConfig(
                    stage=stage,
                    enabled=True,
                    priority=i + 1,
                    parameters=self._get_optimal_parameters_for_stage(stage, characteristics)
                )
                self.config.stages.append(stage_config)
        
        # Optimize existing stages based on content
        for stage_config in self.config.stages:
            if stage_config.enabled:
                optimal_params = self._get_optimal_parameters_for_stage(
                    stage_config.stage, characteristics
                )
                stage_config.parameters.update(optimal_params)
    
    def _get_optimal_parameters_for_stage(
        self, 
        stage: ProcessingStage, 
        characteristics: Dict
    ) -> Dict[str, Any]:
        """Get optimal parameters for a stage based on content characteristics."""
        params = {}
        
        if stage == ProcessingStage.NOISE_REDUCTION:
            if characteristics.get("is_noisy", False):
                params["noise_level"] = 0.8
            else:
                params["noise_level"] = 0.3
        
        elif stage == ProcessingStage.CONTRAST_OPTIMIZATION:
            if characteristics.get("is_low_contrast", False):
                params["contrast_level"] = 0.8
            else:
                params["contrast_level"] = 0.4
        
        elif stage == ProcessingStage.COLOR_ENHANCEMENT:
            if characteristics.get("brightness", 128) < 80:
                params["enhancement_type"] = "underexposed"
            elif characteristics.get("saturation", 128) < 80:
                params["enhancement_type"] = "low_saturation"
            else:
                params["enhancement_type"] = "auto"
        
        elif stage == ProcessingStage.SHARPNESS_ENHANCEMENT:
            if characteristics.get("is_blurry", False):
                params["sharpness_level"] = 0.8
            else:
                params["sharpness_level"] = 0.4
        
        elif stage == ProcessingStage.AI_FILTERING:
            if characteristics.get("is_high_detail", False):
                params["filter_type"] = "artistic_oil"
            else:
                params["filter_type"] = "auto_enhance"
        
        return params
    
    async def _execute_pipeline(
        self, 
        input_path: Path, 
        output_path: Path, 
        content_analysis: Dict
    ) -> Dict[str, Any]:
        """Execute the enhancement pipeline."""
        # Sort stages by priority
        enabled_stages = [s for s in self.config.stages if s.enabled]
        enabled_stages.sort(key=lambda x: x.priority)
        
        current_input = input_path
        intermediate_outputs = []
        stages_executed = []
        total_improvement = 0.0
        pipeline_stats = {}
        
        # Create intermediate directory if needed
        if self.config.intermediate_files:
            intermediate_dir = output_path.parent / f"{output_path.stem}_intermediate"
            intermediate_dir.mkdir(exist_ok=True)
        
        # Execute stages
        for i, stage_config in enumerate(enabled_stages):
            stage_start = time.time()
            
            # Determine output path for this stage
            if i == len(enabled_stages) - 1:
                # Last stage outputs to final path
                stage_output = output_path
            else:
                # Intermediate output
                if self.config.intermediate_files:
                    stage_output = intermediate_dir / f"stage_{i+1}_{stage_config.stage.value}{input_path.suffix}"
                else:
                    stage_output = output_path.parent / f"temp_{stage_config.stage.value}{input_path.suffix}"
                intermediate_outputs.append(stage_output)
            
            # Execute stage
            stage_result = await self._execute_stage(
                stage_config, current_input, stage_output
            )
            
            stage_time = time.time() - stage_start
            
            # Update statistics
            if stage_result.get("success", False):
                stages_executed.append({
                    "stage": stage_config.stage.value,
                    "processing_time": stage_time,
                    "improvement": stage_result.get("improvement_score", 0.0),
                    "parameters": stage_config.parameters
                })
                
                improvement = stage_result.get("improvement_score", 0.0)
                if isinstance(improvement, (int, float)):
                    total_improvement += improvement
                
                pipeline_stats[stage_config.stage.value] = {
                    "processing_time": stage_time,
                    "success": True,
                    "details": stage_result
                }
                
                # Update input for next stage
                current_input = stage_output
                
                # Progress callback
                if self.config.progress_callback:
                    progress = (i + 1) / len(enabled_stages)
                    self.config.progress_callback(progress, stage_config.stage.value)
            else:
                pipeline_stats[stage_config.stage.value] = {
                    "processing_time": stage_time,
                    "success": False,
                    "error": stage_result.get("error", "Unknown error")
                }
                logger.warning(f"Stage {stage_config.stage.value} failed: {stage_result.get('error')}")
        
        # Clean up intermediate files if not saved
        if not self.config.intermediate_files:
            for intermediate_file in intermediate_outputs:
                if intermediate_file.exists() and intermediate_file != output_path:
                    try:
                        intermediate_file.unlink()
                    except Exception as e:
                        logger.warning(f"Could not delete intermediate file {intermediate_file}: {e}")
        
        # Calculate average improvement
        avg_improvement = total_improvement / len(stages_executed) if stages_executed else 0.0
        
        return {
            "stages_executed": stages_executed,
            "total_improvement": avg_improvement,
            "pipeline_stats": pipeline_stats,
            "quality_metrics": await self._calculate_quality_metrics(input_path, output_path)
        }
    
    async def _execute_stage(
        self, 
        stage_config: StageConfig, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, Any]:
        """Execute a single pipeline stage."""
        try:
            engine = self.engines[stage_config.stage]
            parameters = stage_config.parameters
            
            if stage_config.stage == ProcessingStage.NOISE_REDUCTION:
                result = await engine.reduce_noise(
                    input_path, output_path, 
                    parameters.get("noise_level", 0.5)
                )
                
            elif stage_config.stage == ProcessingStage.CONTRAST_OPTIMIZATION:
                result = await engine.optimize_contrast(
                    input_path, output_path,
                    parameters.get("contrast_level", 0.5)
                )
                
            elif stage_config.stage == ProcessingStage.COLOR_ENHANCEMENT:
                result = await engine.enhance_colors(
                    input_path, output_path,
                    parameters.get("enhancement_type", "auto")
                )
                
            elif stage_config.stage == ProcessingStage.SHARPNESS_ENHANCEMENT:
                result = await engine.enhance_sharpness(
                    input_path, output_path,
                    parameters.get("sharpness_level", 0.5)
                )
                
            elif stage_config.stage == ProcessingStage.AI_FILTERING:
                result = await engine.apply_ai_filter(
                    input_path, output_path,
                    parameters.get("filter_type", "auto_enhance")
                )
            else:
                result = {"success": False, "error": f"Unknown stage: {stage_config.stage}"}
            
            # Extract improvement score from result
            improvement_score = 0.0
            if result.get("success", False):
                # Try to extract improvement metrics from different result formats
                if "color_improvement" in result:
                    improvement_score = result["color_improvement"]
                elif "noise_reduction" in result:
                    improvement_score = result["noise_reduction"]
                elif "contrast_improvement" in result:
                    improvement_score = result["contrast_improvement"]
                elif "sharpness_improvement" in result:
                    improvement_score = result["sharpness_improvement"]
                elif "effectiveness_score" in result:
                    improvement_score = result["effectiveness_score"]
                else:
                    improvement_score = 0.5  # Default improvement score
            
            result["improvement_score"] = improvement_score
            return result
            
        except Exception as e:
            logger.error(f"Stage {stage_config.stage.value} execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_quality_metrics(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, float]:
        """Calculate overall quality metrics for the pipeline."""
        try:
            import cv2
            
            # Only calculate for images (video would be too expensive)
            if input_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                return {"note": "Quality metrics only available for images"}
            
            if not output_path.exists():
                return {"error": "Output file not found"}
            
            original = cv2.imread(str(input_path))
            processed = cv2.imread(str(output_path))
            
            if original is None or processed is None:
                return {"error": "Could not load images for quality analysis"}
            
            # Ensure same size
            if original.shape != processed.shape:
                processed = cv2.resize(processed, (original.shape[1], original.shape[0]))
            
            # Calculate PSNR
            psnr = cv2.PSNR(original, processed)
            
            # Calculate simple SSIM
            ssim = self._calculate_simple_ssim(original, processed)
            
            return {
                "psnr": float(psnr),
                "ssim": float(ssim),
                "overall_quality": float((psnr / 50.0 + ssim) / 2)  # Normalized score
            }
            
        except Exception as e:
            logger.warning(f"Quality metrics calculation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_simple_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate a simplified SSIM metric."""
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) if len(img1.shape) == 3 else img1
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) if len(img2.shape) == 3 else img2
        
        # Calculate means
        mu1 = np.mean(gray1)
        mu2 = np.mean(gray2)
        
        # Calculate variances and covariance
        var1 = np.var(gray1)
        var2 = np.var(gray2)
        cov = np.mean((gray1 - mu1) * (gray2 - mu2))
        
        # SSIM constants
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        
        # SSIM calculation
        numerator = (2 * mu1 * mu2 + c1) * (2 * cov + c2)
        denominator = (mu1**2 + mu2**2 + c1) * (var1 + var2 + c2)
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def create_preset_config(self, preset_name: str) -> PipelineConfig:
        """Create a preset pipeline configuration."""
        config = PipelineConfig()
        
        if preset_name == "photo_enhancement":
            config.stages = [
                StageConfig(ProcessingStage.NOISE_REDUCTION, True, {"noise_level": 0.4}, 1),
                StageConfig(ProcessingStage.COLOR_ENHANCEMENT, True, {"enhancement_type": "auto"}, 2),
                StageConfig(ProcessingStage.CONTRAST_OPTIMIZATION, True, {"contrast_level": 0.6}, 3),
                StageConfig(ProcessingStage.SHARPNESS_ENHANCEMENT, True, {"sharpness_level": 0.5}, 4),
            ]
            config.quality_target = "quality"
            
        elif preset_name == "social_media":
            config.stages = [
                StageConfig(ProcessingStage.COLOR_ENHANCEMENT, True, {"enhancement_type": "vibrant_boost"}, 1),
                StageConfig(ProcessingStage.AI_FILTERING, True, {"filter_type": "instagram_vsco"}, 2),
                StageConfig(ProcessingStage.SHARPNESS_ENHANCEMENT, True, {"sharpness_level": 0.3}, 3),
            ]
            config.quality_target = "speed"
            
        elif preset_name == "professional":
            config.stages = [
                StageConfig(ProcessingStage.NOISE_REDUCTION, True, {"noise_level": 0.7}, 1),
                StageConfig(ProcessingStage.CONTRAST_OPTIMIZATION, True, {"contrast_level": 0.8}, 2),
                StageConfig(ProcessingStage.COLOR_ENHANCEMENT, True, {"enhancement_type": "auto"}, 3),
                StageConfig(ProcessingStage.SHARPNESS_ENHANCEMENT, True, {"sharpness_level": 0.7}, 4),
                StageConfig(ProcessingStage.AI_FILTERING, True, {"filter_type": "auto_enhance"}, 5),
            ]
            config.quality_target = "quality"
            config.content_aware = True
            
        elif preset_name == "video_fast":
            config.stages = [
                StageConfig(ProcessingStage.COLOR_ENHANCEMENT, True, {"enhancement_type": "auto"}, 1),
                StageConfig(ProcessingStage.CONTRAST_OPTIMIZATION, True, {"contrast_level": 0.4}, 2),
            ]
            config.quality_target = "speed"
            config.parallel_processing = True
            
        return config
    
    async def batch_process_pipeline(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        pipeline_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process multiple files through the enhancement pipeline."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            return {"success": False, "error": "Input directory not found"}
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        supported_formats = {
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp',  # Images
            '.mp4', '.avi', '.mov', '.mkv',  # Videos
            '.wav', '.mp3', '.flac', '.m4a', '.aac'  # Audio
        }
        
        files_to_process = [
            f for f in input_dir.iterdir() 
            if f.suffix.lower() in supported_formats
        ]
        
        for i, file_path in enumerate(files_to_process):
            output_path = output_dir / file_path.name
            
            # Progress callback for batch processing
            if self.config.progress_callback:
                self.config.progress_callback(i / len(files_to_process), f"Processing {file_path.name}")
            
            result = await self.process_pipeline(file_path, output_path, pipeline_config)
            
            results.append({
                "input": str(file_path),
                "output": str(output_path),
                "result": result
            })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        if successful > 0:
            avg_improvement = np.mean([
                r["result"].get("total_improvements", 0)
                for r in results if r["result"]["success"]
            ])
        else:
            avg_improvement = 0
        
        return {
            "success": True,
            "total_processed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "average_improvement": float(avg_improvement),
            "results": results
        }