"""Quality Preservation Engine
Ensures optimal quality retention during compression processes.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Quality assessment metrics."""
    psnr: float  # Peak Signal-to-Noise Ratio
    ssim: float  # Structural Similarity Index
    vmaf: Optional[float] = None  # Video Multi-Method Assessment Fusion
    delta_e: Optional[float] = None  # Color difference
    perceptual_score: float = 0.0

class QualityPreservationEngine:
    """Advanced quality preservation and assessment engine."""
    
    def __init__(self):
        """Initialize the quality preservation engine."""
        self.quality_thresholds = self._load_quality_thresholds()
        
    def _load_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load quality thresholds for different use cases."""
        return {
            "broadcast": {
                "min_psnr": 40.0,
                "min_ssim": 0.95,
                "min_vmaf": 85.0
            },
            "streaming": {
                "min_psnr": 35.0,
                "min_ssim": 0.90,
                "min_vmaf": 75.0
            },
            "social_media": {
                "min_psnr": 30.0,
                "min_ssim": 0.85,
                "min_vmaf": 65.0
            },
            "web": {
                "min_psnr": 32.0,
                "min_ssim": 0.88,
                "min_vmaf": 70.0
            },
            "mobile": {
                "min_psnr": 28.0,
                "min_ssim": 0.80,
                "min_vmaf": 60.0
            }
        }
    
    async def assess_quality(
        self,
        original_path: Union[str, Path],
        compressed_path: Union[str, Path],
        media_type: str = "image"
    ) -> QualityMetrics:
        """
        Assess quality of compressed media compared to original.
        
        Args:
            original_path: Path to original file
            compressed_path: Path to compressed file
            media_type: Type of media (image, video, audio)
            
        Returns:
            Quality assessment metrics
        """
        try:
            if media_type == "image":
                return await self._assess_image_quality(original_path, compressed_path)
            elif media_type == "video":
                return await self._assess_video_quality(original_path, compressed_path)
            elif media_type == "audio":
                return await self._assess_audio_quality(original_path, compressed_path)
            else:
                raise ValueError(f"Unsupported media type: {media_type}")
                
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return QualityMetrics(psnr=0.0, ssim=0.0, perceptual_score=0.0)
    
    async def _assess_image_quality(
        self,
        original_path: Union[str, Path],
        compressed_path: Union[str, Path]
    ) -> QualityMetrics:
        """Assess image quality using PSNR, SSIM, and perceptual metrics."""
        # Simulate quality assessment
        await asyncio.sleep(0.1)
        
        # In real implementation, this would:
        # 1. Load both images
        # 2. Calculate PSNR
        # 3. Calculate SSIM
        # 4. Calculate perceptual metrics
        
        # Simulated results
        psnr = np.random.uniform(25, 45)  # Typical PSNR range
        ssim = np.random.uniform(0.7, 0.98)  # Typical SSIM range
        
        # Calculate perceptual score based on PSNR and SSIM
        perceptual_score = (psnr / 50.0) * 0.4 + ssim * 0.6
        perceptual_score = min(1.0, max(0.0, perceptual_score))
        
        # Calculate color difference (Delta E)
        delta_e = np.random.uniform(1.0, 8.0)
        
        return QualityMetrics(
            psnr=psnr,
            ssim=ssim,
            delta_e=delta_e,
            perceptual_score=perceptual_score
        )
    
    async def _assess_video_quality(
        self,
        original_path: Union[str, Path],
        compressed_path: Union[str, Path]
    ) -> QualityMetrics:
        """Assess video quality using PSNR, SSIM, and VMAF."""
        # Simulate video quality assessment
        await asyncio.sleep(0.5)
        
        # Simulated results
        psnr = np.random.uniform(28, 42)
        ssim = np.random.uniform(0.75, 0.95)
        vmaf = np.random.uniform(50, 90)
        
        # Calculate perceptual score
        perceptual_score = vmaf / 100.0
        
        return QualityMetrics(
            psnr=psnr,
            ssim=ssim,
            vmaf=vmaf,
            perceptual_score=perceptual_score
        )
    
    async def _assess_audio_quality(
        self,
        original_path: Union[str, Path],
        compressed_path: Union[str, Path]
    ) -> QualityMetrics:
        """Assess audio quality using specialized audio metrics."""
        # Simulate audio quality assessment
        await asyncio.sleep(0.2)
        
        # For audio, we use different metrics
        snr = np.random.uniform(40, 80)  # Signal-to-Noise Ratio
        similarity = np.random.uniform(0.85, 0.99)
        
        # Map to standard metrics
        psnr = snr
        ssim = similarity
        perceptual_score = similarity
        
        return QualityMetrics(
            psnr=psnr,
            ssim=ssim,
            perceptual_score=perceptual_score
        )
    
    def validate_quality(
        self,
        metrics: QualityMetrics,
        use_case: str = "web",
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Validate if quality meets requirements for use case.
        
        Args:
            metrics: Quality metrics to validate
            use_case: Target use case
            strict: Use strict quality requirements
            
        Returns:
            Validation result with recommendations
        """
        thresholds = self.quality_thresholds.get(use_case, self.quality_thresholds["web"])
        
        if strict:
            # Increase thresholds by 10% for strict validation
            thresholds = {k: v * 1.1 for k, v in thresholds.items()}
        
        validation_result = {
            "valid": True,
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Check PSNR
        if metrics.psnr < thresholds["min_psnr"]:
            validation_result["valid"] = False
            validation_result["issues"].append(
                f"PSNR too low: {metrics.psnr:.2f} < {thresholds['min_psnr']}"
            )
            validation_result["recommendations"].append("Increase compression quality")
        
        # Check SSIM
        if metrics.ssim < thresholds["min_ssim"]:
            validation_result["valid"] = False
            validation_result["issues"].append(
                f"SSIM too low: {metrics.ssim:.3f} < {thresholds['min_ssim']}"
            )
            validation_result["recommendations"].append("Use less aggressive compression")
        
        # Check VMAF (for video)
        if metrics.vmaf is not None and metrics.vmaf < thresholds["min_vmaf"]:
            validation_result["valid"] = False
            validation_result["issues"].append(
                f"VMAF too low: {metrics.vmaf:.1f} < {thresholds['min_vmaf']}"
            )
            validation_result["recommendations"].append("Increase bitrate or use better codec")
        
        # Calculate overall quality score
        score_components = [
            metrics.psnr / 50.0,  # Normalize PSNR
            metrics.ssim,
            metrics.perceptual_score
        ]
        
        if metrics.vmaf is not None:
            score_components.append(metrics.vmaf / 100.0)
        
        validation_result["score"] = sum(score_components) / len(score_components)
        
        return validation_result
    
    def suggest_quality_improvements(
        self,
        current_metrics: QualityMetrics,
        target_use_case: str = "web"
    ) -> List[Dict[str, Any]]:
        """Suggest improvements to achieve target quality."""
        suggestions = []
        thresholds = self.quality_thresholds.get(target_use_case, self.quality_thresholds["web"])
        
        if current_metrics.psnr < thresholds["min_psnr"]:
            deficit = thresholds["min_psnr"] - current_metrics.psnr
            suggestions.append({
                "metric": "PSNR",
                "current": current_metrics.psnr,
                "target": thresholds["min_psnr"],
                "deficit": deficit,
                "recommendation": f"Increase quality setting by {int(deficit * 2)}%"
            })
        
        if current_metrics.ssim < thresholds["min_ssim"]:
            deficit = thresholds["min_ssim"] - current_metrics.ssim
            suggestions.append({
                "metric": "SSIM",
                "current": current_metrics.ssim,
                "target": thresholds["min_ssim"],
                "deficit": deficit,
                "recommendation": "Use less lossy compression algorithm"
            })
        
        if (current_metrics.vmaf is not None and 
            current_metrics.vmaf < thresholds["min_vmaf"]):
            deficit = thresholds["min_vmaf"] - current_metrics.vmaf
            suggestions.append({
                "metric": "VMAF",
                "current": current_metrics.vmaf,
                "target": thresholds["min_vmaf"],
                "deficit": deficit,
                "recommendation": f"Increase bitrate by {int(deficit)}%"
            })
        
        return suggestions
    
    async def optimize_for_quality(
        self,
        input_path: Union[str, Path],
        target_quality: float = 0.85,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Iteratively optimize compression to achieve target quality.
        
        Args:
            input_path: Path to input file
            target_quality: Target quality score (0-1)
            max_iterations: Maximum optimization iterations
            
        Returns:
            Optimization result with final settings
        """
        optimization_history = []
        current_quality = 50  # Starting quality setting
        
        for iteration in range(max_iterations):
            # Simulate compression with current quality
            compressed_path = f"temp_compressed_{iteration}.tmp"
            
            # Simulate quality assessment
            metrics = await self.assess_quality(input_path, compressed_path, "image")
            
            optimization_history.append({
                "iteration": iteration,
                "quality_setting": current_quality,
                "metrics": metrics,
                "score": metrics.perceptual_score
            })
            
            # Check if target achieved
            if metrics.perceptual_score >= target_quality:
                return {
                    "success": True,
                    "iterations": iteration + 1,
                    "final_quality_setting": current_quality,
                    "final_metrics": metrics,
                    "optimization_history": optimization_history
                }
            
            # Adjust quality setting for next iteration
            if metrics.perceptual_score < target_quality:
                current_quality = min(95, current_quality + 10)
            else:
                current_quality = max(60, current_quality - 5)
        
        # Return best result if target not achieved
        best_result = max(optimization_history, key=lambda x: x["score"])
        
        return {
            "success": False,
            "iterations": max_iterations,
            "best_quality_setting": best_result["quality_setting"],
            "best_metrics": best_result["metrics"],
            "target_quality": target_quality,
            "achieved_quality": best_result["score"],
            "optimization_history": optimization_history
        }
    
    def get_quality_report(
        self,
        metrics: QualityMetrics,
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        return {
            "file_info": file_info,
            "quality_metrics": {
                "psnr": {
                    "value": metrics.psnr,
                    "rating": self._rate_psnr(metrics.psnr),
                    "description": "Peak Signal-to-Noise Ratio"
                },
                "ssim": {
                    "value": metrics.ssim,
                    "rating": self._rate_ssim(metrics.ssim),
                    "description": "Structural Similarity Index"
                },
                "perceptual_score": {
                    "value": metrics.perceptual_score,
                    "rating": self._rate_perceptual(metrics.perceptual_score),
                    "description": "Overall perceptual quality"
                }
            },
            "overall_rating": self._get_overall_rating(metrics),
            "recommendations": self._get_quality_recommendations(metrics)
        }
    
    def _rate_psnr(self, psnr: float) -> str:
        """Rate PSNR value."""
        if psnr >= 40:
            return "Excellent"
        elif psnr >= 35:
            return "Good"
        elif psnr >= 30:
            return "Fair"
        else:
            return "Poor"
    
    def _rate_ssim(self, ssim: float) -> str:
        """Rate SSIM value."""
        if ssim >= 0.95:
            return "Excellent"
        elif ssim >= 0.90:
            return "Good"
        elif ssim >= 0.80:
            return "Fair"
        else:
            return "Poor"
    
    def _rate_perceptual(self, score: float) -> str:
        """Rate perceptual score."""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "Good"
        elif score >= 0.7:
            return "Fair"
        else:
            return "Poor"
    
    def _get_overall_rating(self, metrics: QualityMetrics) -> str:
        """Get overall quality rating."""
        scores = [
            self._rate_psnr(metrics.psnr),
            self._rate_ssim(metrics.ssim),
            self._rate_perceptual(metrics.perceptual_score)
        ]
        
        excellent_count = scores.count("Excellent")
        good_count = scores.count("Good")
        
        if excellent_count >= 2:
            return "Excellent"
        elif excellent_count + good_count >= 2:
            return "Good"
        elif "Poor" not in scores:
            return "Fair"
        else:
            return "Poor"
    
    def _get_quality_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """Get quality improvement recommendations."""
        recommendations = []
        
        if metrics.psnr < 30:
            recommendations.append("Consider increasing compression quality to improve PSNR")
        
        if metrics.ssim < 0.85:
            recommendations.append("Use compression algorithm that better preserves structure")
        
        if metrics.perceptual_score < 0.8:
            recommendations.append("Overall quality could be improved with better compression settings")
        
        if not recommendations:
            recommendations.append("Quality is acceptable for most use cases")
        
        return recommendations