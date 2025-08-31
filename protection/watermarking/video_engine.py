"""Professional Video Watermarking Engine
Advanced digital watermarking for video content with temporal and spatial techniques

Developed by: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Senior Backend + ML Engineer + DBA + Security Expert + 
               Microservices Architect + Audio Engineer + DevOps + AI Prompt Engineer

⚠️ INTELLECTUAL PROPERTY WARNING:
This video watermarking engine, concept, and all associated code are the exclusive intellectual 
property of Fahed Mlaiel. Any unauthorized use, copying, modification, or distribution 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly 
prohibited and will result in legal action.
"""
import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import hashlib
import base64
from pathlib import Path
import tempfile
import io
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    import cv2
    from PIL import Image
    import imageio
    from scipy.fft import dct, idct
    from scipy import ndimage
    import pywt
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False

logger = logging.getLogger(__name__)


class VideoWatermarkTechnique(Enum):
    """Video watermarking techniques"""    FRAME_DCT = "frame_dct"
    FRAME_DWT = "frame_dwt"
    FRAME_LSB = "frame_lsb"
    TEMPORAL_CORRELATION = "temporal_correlation"
    MOTION_VECTOR = "motion_vector"
    COMPRESSED_DOMAIN = "compressed_domain"
    SCENE_CHANGE = "scene_change"
    SPATIAL_TEMPORAL = "spatial_temporal"


class VideoFrameSelection(Enum):
    """Frame selection strategies"""    UNIFORM = "uniform"          # Every N frames
    KEYFRAMES_ONLY = "keyframes" # Only keyframes
    SCENE_CHANGES = "scenes"     # At scene changes
    HIGH_MOTION = "motion"       # High motion frames
    LOW_MOTION = "static"        # Low motion frames
    ADAPTIVE = "adaptive"        # Adaptive selection


class VideoQualityLevel(Enum):
    """Video quality preservation levels"""    BROADCAST = "broadcast"      # Broadcast quality
    STREAMING = "streaming"      # Streaming quality
    COMPRESSED = "compressed"    # Heavily compressed
    PREVIEW = "preview"          # Preview quality


@dataclass
class VideoWatermarkConfig:
    """Configuration for video watermarking"""    technique: VideoWatermarkTechnique = VideoWatermarkTechnique.FRAME_DCT
    frame_selection: VideoFrameSelection = VideoFrameSelection.UNIFORM
    quality_level: VideoQualityLevel = VideoQualityLevel.STREAMING
    frame_interval: int = 10
    max_frames: int = 1000
    temporal_window: int = 5
    spatial_block_size: int = 8
    embedding_strength: float = 0.1
    motion_threshold: float = 0.5
    preserve_keyframes: bool = True
    codec_compatibility: bool = True


@dataclass
class FrameMetadata:
    """Metadata for individual frame processing"""    frame_number: int
    timestamp_ms: float
    is_keyframe: bool
    motion_level: float
    complexity_score: float
    watermark_applied: bool
    embedding_strength: float
    bits_embedded: int


class MotionAnalyzer:
    """Motion analysis for adaptive watermarking"""    
    def __init__(self):
        self.prev_frame_gray = None
        self.motion_threshold = 0.5
    
    async def analyze_motion(self, frame: np.ndarray) -> float:
        """Analyze motion in frame compared to previous"""        try:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.prev_frame_gray is None:
                self.prev_frame_gray = frame_gray
                return 0.0
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                self.prev_frame_gray, frame_gray, None, None
            )
            
            # Calculate motion magnitude
            if flow[0] is not None:
                motion_magnitude = np.mean(np.sqrt(
                    np.sum(flow[0] ** 2, axis=2)
                ))
            else:
                motion_magnitude = 0.0
            
            self.prev_frame_gray = frame_gray
            return float(motion_magnitude)
            
        except Exception as e:
            logger.error(f"Error analyzing motion: {e}")
            return 0.0
    
    def reset(self):
        """Reset motion analyzer state"""        self.prev_frame_gray = None


class SceneDetector:
    """Scene change detection for adaptive processing"""    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
        self.prev_histogram = None
    
    async def detect_scene_change(self, frame: np.ndarray) -> bool:
        """Detect if current frame represents a scene change"""        try:
            # Calculate color histogram
            hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            
            if self.prev_histogram is None:
                self.prev_histogram = hist
                return True  # First frame is always a scene change
            
            # Calculate histogram correlation
            correlation = cv2.compareHist(self.prev_histogram, hist, cv2.HISTCMP_CORREL)
            
            # Scene change if correlation is below threshold
            scene_change = correlation < self.threshold
            
            self.prev_histogram = hist
            return scene_change
            
        except Exception as e:
            logger.error(f"Error detecting scene change: {e}")
            return False
    
    def reset(self):
        """Reset scene detector state"""        self.prev_histogram = None


class SpatialWatermarkEmbedder:
    """Spatial domain watermarking for video frames"""    
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
    
    async def embed_dct_watermark(self,
                                frame: np.ndarray,
                                watermark_bits: List[int],
                                strength: float = 0.1) -> Tuple[np.ndarray, int]:
        """Embed watermark using DCT in frame"""        try:
            if len(frame.shape) != 3:
                raise ValueError("Frame must be color image")
            
            # Convert to YUV for processing luminance
            yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            y_channel = yuv_frame[:, :, 0].astype(np.float32)
            
            height, width = y_channel.shape
            watermarked_y = y_channel.copy()
            bits_embedded = 0
            
            # Process in 8x8 blocks
            for y in range(0, height - self.block_size, self.block_size):
                for x in range(0, width - self.block_size, self.block_size):
                    if bits_embedded >= len(watermark_bits):
                        break
                    
                    # Extract block
                    block = y_channel[y:y+self.block_size, x:x+self.block_size]
                    
                    # DCT transform
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    
                    # Embed watermark bit in mid-frequency coefficient
                    bit = watermark_bits[bits_embedded]
                    
                    # Choose coefficient position (avoid DC and high frequencies)
                    coeff_pos = (2, 3) if bits_embedded % 2 == 0 else (3, 2)
                    
                    if bit == 1:
                        dct_block[coeff_pos] += strength * abs(dct_block[coeff_pos]) + strength * 10
                    else:
                        dct_block[coeff_pos] -= strength * abs(dct_block[coeff_pos]) + strength * 10
                    
                    # Inverse DCT
                    watermarked_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                    watermarked_y[y:y+self.block_size, x:x+self.block_size] = watermarked_block
                    
                    bits_embedded += 1
                
                if bits_embedded >= len(watermark_bits):
                    break
            
            # Reconstruct frame
            watermarked_yuv = yuv_frame.copy()
            watermarked_yuv[:, :, 0] = np.clip(watermarked_y, 0, 255).astype(np.uint8)
            watermarked_frame = cv2.cvtColor(watermarked_yuv, cv2.COLOR_YUV2BGR)
            
            return watermarked_frame, bits_embedded
            
        except Exception as e:
            logger.error(f"Error in DCT watermark embedding: {e}")
            return frame, 0
    
    async def embed_dwt_watermark(self,
                                frame: np.ndarray,
                                watermark_bits: List[int],
                                strength: float = 0.1) -> Tuple[np.ndarray, int]:
        """Embed watermark using DWT in frame"""        try:
            # Convert to grayscale for DWT processing
            if len(frame.shape) == 3:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
            else:
                gray_frame = frame.astype(np.float32)
            
            # DWT decomposition
            coeffs = pywt.dwt2(gray_frame, 'haar')
            cA, (cH, cV, cD) = coeffs
            
            # Embed in detail coefficients
            bits_embedded = 0
            modified_cH = cH.copy()
            
            height, width = cH.shape
            positions_per_bit = max(1, (height * width) // len(watermark_bits))
            
            for i, bit in enumerate(watermark_bits):
                if i * positions_per_bit < height * width:
                    y_pos = (i * positions_per_bit) // width
                    x_pos = (i * positions_per_bit) % width
                    
                    if y_pos < height and x_pos < width:
                        if bit == 1:
                            modified_cH[y_pos, x_pos] += strength * abs(modified_cH[y_pos, x_pos]) + strength
                        else:
                            modified_cH[y_pos, x_pos] -= strength * abs(modified_cH[y_pos, x_pos]) + strength
                        
                        bits_embedded += 1
            
            # Reconstruct image
            modified_coeffs = (cA, (modified_cH, cV, cD))
            watermarked_gray = pywt.idwt2(modified_coeffs, 'haar')
            
            # Convert back to color if needed
            if len(frame.shape) == 3:
                # Map grayscale back to color channels
                watermarked_frame = frame.copy()
                for channel in range(3):
                    watermarked_frame[:, :, channel] = np.clip(watermarked_gray, 0, 255)
            else:
                watermarked_frame = np.clip(watermarked_gray, 0, 255).astype(np.uint8)
            
            return watermarked_frame, bits_embedded
            
        except Exception as e:
            logger.error(f"Error in DWT watermark embedding: {e}")
            return frame, 0
    
    async def embed_lsb_watermark(self,
                                frame: np.ndarray,
                                watermark_bits: List[int],
                                channel: int = 2) -> Tuple[np.ndarray, int]:
        """Embed watermark using LSB in frame"""        try:
            watermarked_frame = frame.copy()
            height, width = frame.shape[:2]
            
            bits_embedded = 0
            bit_index = 0
            
            # Embed in specified channel (default: blue channel)
            for y in range(0, height, 4):  # Skip pixels for imperceptibility
                for x in range(0, width, 4):
                    if bit_index >= len(watermark_bits):
                        break
                    
                    # Modify LSB
                    pixel_value = watermarked_frame[y, x, channel]
                    bit = watermark_bits[bit_index]
                    
                    if bit == 1:
                        watermarked_frame[y, x, channel] = pixel_value | 1
                    else:
                        watermarked_frame[y, x, channel] = pixel_value & 0xFE
                    
                    bit_index += 1
                    bits_embedded += 1
                
                if bit_index >= len(watermark_bits):
                    break
            
            return watermarked_frame, bits_embedded
            
        except Exception as e:
            logger.error(f"Error in LSB watermark embedding: {e}")
            return frame, 0


class TemporalWatermarkEmbedder:
    """Temporal domain watermarking across video frames"""    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.frame_buffer: List[np.ndarray] = []
    
    async def embed_temporal_correlation(self,
                                       frames: List[np.ndarray],
                                       watermark_bits: List[int],
                                       strength: float = 0.1) -> List[np.ndarray]:
        """Embed watermark using temporal correlation"""        try:
            if len(frames) < 2:
                return frames
            
            watermarked_frames = [frame.copy() for frame in frames]
            bits_per_frame_pair = len(watermark_bits) // (len(frames) - 1)
            
            for i in range(len(frames) - 1):
                start_bit = i * bits_per_frame_pair
                end_bit = min((i + 1) * bits_per_frame_pair, len(watermark_bits))
                frame_bits = watermark_bits[start_bit:end_bit]
                
                if frame_bits:
                    # Apply temporal modification
                    current_frame = watermarked_frames[i]
                    next_frame = watermarked_frames[i + 1]
                    
                    # Modify correlation between frames
                    modified_next = await self._modify_temporal_correlation(
                        current_frame, next_frame, frame_bits, strength
                    )
                    
                    watermarked_frames[i + 1] = modified_next
            
            return watermarked_frames
            
        except Exception as e:
            logger.error(f"Error in temporal correlation embedding: {e}")
            return frames
    
    async def _modify_temporal_correlation(self,
                                         frame1: np.ndarray,
                                         frame2: np.ndarray,
                                         bits: List[int],
                                         strength: float) -> np.ndarray:
        """Modify temporal correlation between two frames"""        try:
            # Convert to grayscale for correlation analysis
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY) if len(frame1.shape) == 3 else frame1
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY) if len(frame2.shape) == 3 else frame2
            
            modified_frame2 = frame2.copy()
            
            # Process in blocks
            block_size = 16
            height, width = gray1.shape
            bit_index = 0
            
            for y in range(0, height - block_size, block_size):
                for x in range(0, width - block_size, block_size):
                    if bit_index >= len(bits):
                        break
                    
                    block1 = gray1[y:y+block_size, x:x+block_size]
                    block2 = gray2[y:y+block_size, x:x+block_size]
                    
                    # Calculate correlation
                    correlation = np.corrcoef(block1.flatten(), block2.flatten())[0, 1]
                    
                    if not np.isnan(correlation):
                        bit = bits[bit_index]
                        
                        # Modify correlation based on bit value
                        if bit == 1:
                            # Increase correlation
                            adjustment = strength * (block1.astype(np.float32) - block2.astype(np.float32))
                        else:
                            # Decrease correlation
                            adjustment = -strength * (block1.astype(np.float32) - block2.astype(np.float32))
                        
                        # Apply adjustment to all channels
                        for channel in range(modified_frame2.shape[2]):
                            modified_block = modified_frame2[y:y+block_size, x:x+block_size, channel].astype(np.float32)
                            modified_block += adjustment
                            modified_frame2[y:y+block_size, x:x+block_size, channel] = np.clip(modified_block, 0, 255).astype(np.uint8)
                    
                    bit_index += 1
                
                if bit_index >= len(bits):
                    break
            
            return modified_frame2
            
        except Exception as e:
            logger.error(f"Error modifying temporal correlation: {e}")
            return frame2


class VideoWatermarkEngine:
    """    Professional Video Watermarking Engine
    
    Advanced digital watermarking system for video content supporting:
    - Spatial domain techniques (DCT, DWT, LSB)
    - Temporal domain techniques (correlation, motion vectors)
    - Adaptive frame selection
    - Quality preservation
    - Real-time processing capabilities
    """    
    def __init__(self, config: Optional[VideoWatermarkConfig] = None):
        self.config = config or VideoWatermarkConfig()
        
        # Initialize components
        self.spatial_embedder = SpatialWatermarkEmbedder(self.config.spatial_block_size)
        self.temporal_embedder = TemporalWatermarkEmbedder(self.config.temporal_window)
        self.motion_analyzer = MotionAnalyzer()
        self.scene_detector = SceneDetector()
        
        # Processing state
        self.current_frame_number = 0
        self.frame_metadata: List[FrameMetadata] = []
        self.total_bits_embedded = 0
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def embed_watermark(self,
                            video_path: str,
                            watermark_data: bytes,
                            output_path: str,
                            progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """        Embed watermark in video file
        
        Args:
            video_path: Input video file path
            watermark_data: Binary data to embed
            output_path: Output video file path
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with embedding results and statistics
        """        start_time = datetime.now()
        
        try:
            if not VIDEO_AVAILABLE:
                raise ValueError("Video processing libraries not available")
            
            # Validate input
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Convert watermark data to bits
            watermark_bits = self._data_to_bits(watermark_data)
            
            # Initialize video capture and writer
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            video_info = await self._get_video_info(cap)
            
            # Calculate embedding capacity
            capacity_info = await self._calculate_embedding_capacity(video_info, watermark_bits)
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                output_path,
                fourcc,
                video_info['fps'],
                (video_info['width'], video_info['height'])
            )
            
            # Reset processing state
            self.current_frame_number = 0
            self.frame_metadata = []
            self.total_bits_embedded = 0
            self.motion_analyzer.reset()
            self.scene_detector.reset()
            
            # Process frames
            processing_result = await self._process_video_frames(
                cap, out, watermark_bits, video_info, progress_callback
            )
            
            # Cleanup
            cap.release()
            out.release()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Compile results
            result = {
                'success': True,
                'video_info': video_info,
                'watermark_info': {
                    'data_size_bytes': len(watermark_data),
                    'total_bits': len(watermark_bits),
                    'bits_embedded': self.total_bits_embedded,
                    'embedding_rate': self.total_bits_embedded / len(watermark_bits) if watermark_bits else 0
                },
                'processing_info': {
                    'technique': self.config.technique.value,
                    'frame_selection': self.config.frame_selection.value,
                    'frames_processed': processing_result['frames_processed'],
                    'frames_watermarked': processing_result['frames_watermarked'],
                    'processing_time_seconds': processing_time
                },
                'capacity_analysis': capacity_info,
                'frame_metadata': [fm.__dict__ for fm in self.frame_metadata[:100]],  # Limit for output size
                'quality_metrics': processing_result.get('quality_metrics', {}),
                'output_path': output_path
            }
            
            logger.info(f"Video watermarking completed: {self.total_bits_embedded}/{len(watermark_bits)} bits embedded")
            return result
            
        except Exception as e:
            logger.error(f"Error in video watermarking: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_seconds': (datetime.now() - start_time).total_seconds()
            }
    
    async def detect_watermark(self,
                             watermarked_video_path: str,
                             original_video_path: Optional[str] = None,
                             expected_data_length: Optional[int] = None) -> Dict[str, Any]:
        """        Detect and extract watermark from video
        
        Args:
            watermarked_video_path: Path to watermarked video
            original_video_path: Optional path to original video for comparison
            expected_data_length: Expected length of embedded data
            
        Returns:
            Dictionary with detection results
        """        start_time = datetime.now()
        
        try:
            if not VIDEO_AVAILABLE:
                raise ValueError("Video processing libraries not available")
            
            # Open watermarked video
            cap = cv2.VideoCapture(watermarked_video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {watermarked_video_path}")
            
            # Open original video if provided
            original_cap = None
            if original_video_path:
                original_cap = cv2.VideoCapture(original_video_path)
                if not original_cap.isOpened():
                    logger.warning(f"Could not open original video: {original_video_path}")
                    original_cap = None
            
            # Get video info
            video_info = await self._get_video_info(cap)
            
            # Estimate expected bits
            if expected_data_length is None:
                expected_data_length = 64  # Default assumption
            expected_bits = expected_data_length * 8
            
            # Extract watermark
            extraction_result = await self._extract_watermark_from_frames(
                cap, original_cap, expected_bits
            )
            
            # Cleanup
            cap.release()
            if original_cap:
                original_cap.release()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Process results
            detected = extraction_result['confidence'] > 0.5
            extracted_data = None
            
            if detected and extraction_result['extracted_bits']:
                try:
                    extracted_data = self._bits_to_data(extraction_result['extracted_bits'][:expected_bits])
                except Exception as e:
                    logger.warning(f"Error converting extracted bits to data: {e}")
            
            return {
                'detected': detected,
                'confidence': extraction_result['confidence'],
                'extracted_data': extracted_data,
                'extracted_bits_count': len(extraction_result['extracted_bits']),
                'expected_bits': expected_bits,
                'video_info': video_info,
                'detection_method': self.config.technique.value,
                'processing_time_seconds': processing_time,
                'frame_analysis': extraction_result.get('frame_analysis', {})
            }
            
        except Exception as e:
            logger.error(f"Error in watermark detection: {e}")
            return {
                'detected': False,
                'confidence': 0.0,
                'error': str(e),
                'processing_time_seconds': (datetime.now() - start_time).total_seconds()
            }
    
    async def _get_video_info(self, cap: cv2.VideoCapture) -> Dict[str, Any]:
        """Extract video information"""        try:
            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration_seconds': 0.0,
                'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
            }
            
            if info['fps'] > 0:
                info['duration_seconds'] = info['frame_count'] / info['fps']
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {
                'width': 640, 'height': 480, 'fps': 30.0,
                'frame_count': 0, 'duration_seconds': 0.0, 'codec': 0
            }
    
    async def _calculate_embedding_capacity(self, 
                                          video_info: Dict[str, Any],
                                          watermark_bits: List[int]) -> Dict[str, Any]:
        """Calculate embedding capacity and requirements"""        try:
            total_frames = video_info['frame_count']
            
            # Calculate frames to be processed based on selection strategy
            if self.config.frame_selection == VideoFrameSelection.UNIFORM:
                frames_to_process = total_frames // self.config.frame_interval
            elif self.config.frame_selection == VideoFrameSelection.KEYFRAMES_ONLY:
                frames_to_process = total_frames // 10  # Estimate 10% keyframes
            else:
                frames_to_process = min(total_frames, self.config.max_frames)
            
            # Calculate capacity per frame
            frame_area = video_info['width'] * video_info['height']
            
            if self.config.technique == VideoWatermarkTechnique.FRAME_DCT:
                bits_per_frame = (frame_area // (self.config.spatial_block_size ** 2)) // 4
            elif self.config.technique == VideoWatermarkTechnique.FRAME_LSB:
                bits_per_frame = frame_area // 16  # Skip pixels for imperceptibility
            else:
                bits_per_frame = frame_area // 64  # Conservative estimate
            
            total_capacity = frames_to_process * bits_per_frame
            
            return {
                'total_frames': total_frames,
                'frames_to_process': frames_to_process,
                'bits_per_frame': bits_per_frame,
                'total_capacity_bits': total_capacity,
                'watermark_bits_required': len(watermark_bits),
                'capacity_utilization': len(watermark_bits) / total_capacity if total_capacity > 0 else 1.0,
                'sufficient_capacity': total_capacity >= len(watermark_bits)
            }
            
        except Exception as e:
            logger.error(f"Error calculating embedding capacity: {e}")
            return {
                'total_capacity_bits': 0,
                'sufficient_capacity': False,
                'error': str(e)
            }
    
    async def _process_video_frames(self,
                                  cap: cv2.VideoCapture,
                                  out: cv2.VideoWriter,
                                  watermark_bits: List[int],
                                  video_info: Dict[str, Any],
                                  progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Process video frames for watermark embedding"""        try:
            frames_processed = 0
            frames_watermarked = 0
            bit_index = 0
            
            # Calculate total frames for progress tracking
            total_frames = min(video_info['frame_count'], self.config.max_frames)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                self.current_frame_number = frames_processed
                
                # Check if we should process this frame
                should_process = await self._should_process_frame(frame, frames_processed)
                
                if should_process and bit_index < len(watermark_bits):
                    # Calculate bits to embed in this frame
                    remaining_bits = len(watermark_bits) - bit_index
                    bits_per_frame = min(remaining_bits, self._calculate_bits_per_frame(frame))
                    
                    if bits_per_frame > 0:
                        frame_bits = watermark_bits[bit_index:bit_index + bits_per_frame]
                        
                        # Embed watermark in frame
                        watermarked_frame, bits_embedded = await self._embed_frame_watermark(
                            frame, frame_bits
                        )
                        
                        if bits_embedded > 0:
                            frame = watermarked_frame
                            bit_index += bits_embedded
                            self.total_bits_embedded += bits_embedded
                            frames_watermarked += 1
                            
                            # Store frame metadata
                            frame_meta = FrameMetadata(
                                frame_number=frames_processed,
                                timestamp_ms=frames_processed / video_info['fps'] * 1000,
                                is_keyframe=await self._is_keyframe(frame),
                                motion_level=await self.motion_analyzer.analyze_motion(frame),
                                complexity_score=await self._calculate_frame_complexity(frame),
                                watermark_applied=True,
                                embedding_strength=self.config.embedding_strength,
                                bits_embedded=bits_embedded
                            )
                            self.frame_metadata.append(frame_meta)
                
                # Write frame to output
                out.write(frame)
                frames_processed += 1
                
                # Progress callback
                if progress_callback and frames_processed % 30 == 0:  # Every 30 frames
                    progress = frames_processed / total_frames
                    await progress_callback(progress, frames_processed, frames_watermarked)
                
                # Check limits
                if frames_processed >= self.config.max_frames:
                    break
                if bit_index >= len(watermark_bits):
                    # Continue processing remaining frames without watermarking
                    pass
            
            return {
                'frames_processed': frames_processed,
                'frames_watermarked': frames_watermarked,
                'bits_embedded': self.total_bits_embedded,
                'quality_metrics': await self._calculate_quality_metrics()
            }
            
        except Exception as e:
            logger.error(f"Error processing video frames: {e}")
            raise
    
    async def _should_process_frame(self, frame: np.ndarray, frame_number: int) -> bool:
        """Determine if frame should be processed for watermarking"""        try:
            # Uniform selection
            if self.config.frame_selection == VideoFrameSelection.UNIFORM:
                return frame_number % self.config.frame_interval == 0
            
            # Keyframes only
            elif self.config.frame_selection == VideoFrameSelection.KEYFRAMES_ONLY:
                return await self._is_keyframe(frame)
            
            # Scene changes
            elif self.config.frame_selection == VideoFrameSelection.SCENE_CHANGES:
                return await self.scene_detector.detect_scene_change(frame)
            
            # Motion-based selection
            elif self.config.frame_selection == VideoFrameSelection.HIGH_MOTION:
                motion = await self.motion_analyzer.analyze_motion(frame)
                return motion > self.config.motion_threshold
            
            elif self.config.frame_selection == VideoFrameSelection.LOW_MOTION:
                motion = await self.motion_analyzer.analyze_motion(frame)
                return motion <= self.config.motion_threshold
            
            # Adaptive selection
            elif self.config.frame_selection == VideoFrameSelection.ADAPTIVE:
                return await self._adaptive_frame_selection(frame, frame_number)
            
            else:
                return True  # Default: process all frames
                
        except Exception as e:
            logger.error(f"Error in frame selection: {e}")
            return False
    
    async def _embed_frame_watermark(self, 
                                   frame: np.ndarray,
                                   watermark_bits: List[int]) -> Tuple[np.ndarray, int]:
        """Embed watermark in a single frame"""        try:
            if self.config.technique == VideoWatermarkTechnique.FRAME_DCT:
                return await self.spatial_embedder.embed_dct_watermark(
                    frame, watermark_bits, self.config.embedding_strength
                )
            
            elif self.config.technique == VideoWatermarkTechnique.FRAME_DWT:
                return await self.spatial_embedder.embed_dwt_watermark(
                    frame, watermark_bits, self.config.embedding_strength
                )
            
            elif self.config.technique == VideoWatermarkTechnique.FRAME_LSB:
                return await self.spatial_embedder.embed_lsb_watermark(
                    frame, watermark_bits
                )
            
            else:
                logger.warning(f"Unsupported technique: {self.config.technique}")
                return frame, 0
                
        except Exception as e:
            logger.error(f"Error embedding frame watermark: {e}")
            return frame, 0
    
    async def _extract_watermark_from_frames(self,
                                           cap: cv2.VideoCapture,
                                           original_cap: Optional[cv2.VideoCapture],
                                           expected_bits: int) -> Dict[str, Any]:
        """Extract watermark from video frames"""        try:
            extracted_bits = []
            confidence_scores = []
            frames_analyzed = 0
            
            while len(extracted_bits) < expected_bits:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Get original frame if available
                original_frame = None
                if original_cap:
                    ret_orig, original_frame = original_cap.read()
                    if not ret_orig:
                        original_frame = None
                
                # Extract bits from frame
                frame_bits, frame_confidence = await self._extract_frame_watermark(
                    frame, original_frame, expected_bits - len(extracted_bits)
                )
                
                if frame_bits:
                    extracted_bits.extend(frame_bits)
                    confidence_scores.extend([frame_confidence] * len(frame_bits))
                
                frames_analyzed += 1
                
                # Limit analysis
                if frames_analyzed >= self.config.max_frames:
                    break
            
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return {
                'extracted_bits': extracted_bits,
                'confidence': overall_confidence,
                'frames_analyzed': frames_analyzed,
                'frame_analysis': {
                    'bits_per_frame_avg': len(extracted_bits) / max(1, frames_analyzed),
                    'confidence_distribution': {
                        'mean': overall_confidence,
                        'std': np.std(confidence_scores) if confidence_scores else 0.0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting watermark from frames: {e}")
            return {
                'extracted_bits': [],
                'confidence': 0.0,
                'frames_analyzed': 0,
                'error': str(e)
            }
    
    async def _extract_frame_watermark(self,
                                     frame: np.ndarray,
                                     original_frame: Optional[np.ndarray],
                                     max_bits: int) -> Tuple[List[int], float]:
        """Extract watermark from a single frame"""        try:
            # Placeholder implementation - would need original frame for proper extraction
            # This is a simplified version for demonstration
            
            if self.config.technique == VideoWatermarkTechnique.FRAME_LSB:
                return await self._extract_lsb_from_frame(frame, max_bits)
            else:
                # For DCT/DWT, we would need the original for comparison
                if original_frame is not None:
                    return await self._extract_spatial_from_frame(frame, original_frame, max_bits)
                else:
                    # Blind detection (more complex)
                    return [], 0.0
                    
        except Exception as e:
            logger.error(f"Error extracting frame watermark: {e}")
            return [], 0.0
    
    async def _extract_lsb_from_frame(self, frame: np.ndarray, max_bits: int) -> Tuple[List[int], float]:
        """Extract LSB watermark from frame"""        try:
            height, width = frame.shape[:2]
            extracted_bits = []
            
            for y in range(0, height, 4):
                for x in range(0, width, 4):
                    if len(extracted_bits) >= max_bits:
                        break
                    
                    # Extract LSB from blue channel
                    pixel_value = frame[y, x, 2]
                    bit = pixel_value & 1
                    extracted_bits.append(bit)
                
                if len(extracted_bits) >= max_bits:
                    break
            
            # Simple confidence estimate
            confidence = 0.7 if extracted_bits else 0.0
            
            return extracted_bits, confidence
            
        except Exception as e:
            logger.error(f"Error extracting LSB: {e}")
            return [], 0.0
    
    async def _extract_spatial_from_frame(self,
                                        watermarked_frame: np.ndarray,
                                        original_frame: np.ndarray,
                                        max_bits: int) -> Tuple[List[int], float]:
        """Extract spatial domain watermark by comparison"""        try:
            # This would implement DCT/DWT comparison extraction
            # Placeholder implementation
            return [], 0.5
            
        except Exception as e:
            logger.error(f"Error extracting spatial watermark: {e}")
            return [], 0.0
    
    # Helper methods
    
    def _data_to_bits(self, data: bytes) -> List[int]:
        """Convert bytes to bit list"""        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return bits
    
    def _bits_to_data(self, bits: List[int]) -> bytes:
        """Convert bit list to bytes"""        data = bytearray()
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | bits[i + j]
                data.append(byte)
        return bytes(data)
    
    async def _is_keyframe(self, frame: np.ndarray) -> bool:
        """Detect if frame is a keyframe (simplified)"""        # This is a placeholder - proper keyframe detection would require codec info
        return self.current_frame_number % 30 == 0  # Assume keyframe every 30 frames
    
    async def _calculate_frame_complexity(self, frame: np.ndarray) -> float:
        """Calculate frame complexity score"""        try:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate variance (higher variance = more complex)
            complexity = np.var(gray_frame) / 255.0
            
            return float(complexity)
            
        except Exception as e:
            logger.error(f"Error calculating frame complexity: {e}")
            return 0.0
    
    def _calculate_bits_per_frame(self, frame: np.ndarray) -> int:
        """Calculate how many bits can be embedded in this frame"""        height, width = frame.shape[:2]
        frame_area = height * width
        
        if self.config.technique == VideoWatermarkTechnique.FRAME_DCT:
            return (frame_area // (self.config.spatial_block_size ** 2)) // 4
        elif self.config.technique == VideoWatermarkTechnique.FRAME_LSB:
            return frame_area // 16
        else:
            return frame_area // 64
    
    async def _adaptive_frame_selection(self, frame: np.ndarray, frame_number: int) -> bool:
        """Adaptive frame selection logic"""        try:
            # Combine multiple criteria
            motion = await self.motion_analyzer.analyze_motion(frame)
            complexity = await self._calculate_frame_complexity(frame)
            scene_change = await self.scene_detector.detect_scene_change(frame)
            
            # Score based on multiple factors
            score = 0.0
            
            # Prefer medium motion (not too static, not too dynamic)
            if 0.2 <= motion <= 0.8:
                score += 0.3
            
            # Prefer medium complexity
            if 0.3 <= complexity <= 0.7:
                score += 0.3
            
            # Prefer frames after scene changes
            if scene_change:
                score += 0.4
            
            # Select frame if score is high enough
            return score >= 0.5
            
        except Exception as e:
            logger.error(f"Error in adaptive frame selection: {e}")
            return frame_number % self.config.frame_interval == 0
    
    async def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculate quality metrics for processed video"""        try:
            if not self.frame_metadata:
                return {}
            
            total_frames = len(self.frame_metadata)
            watermarked_frames = sum(1 for fm in self.frame_metadata if fm.watermark_applied)
            
            avg_motion = np.mean([fm.motion_level for fm in self.frame_metadata])
            avg_complexity = np.mean([fm.complexity_score for fm in self.frame_metadata])
            avg_bits_per_frame = np.mean([fm.bits_embedded for fm in self.frame_metadata if fm.bits_embedded > 0])
            
            return {
                'total_frames_processed': total_frames,
                'frames_watermarked': watermarked_frames,
                'watermarking_rate': watermarked_frames / total_frames if total_frames > 0 else 0,
                'average_motion_level': float(avg_motion),
                'average_complexity_score': float(avg_complexity),
                'average_bits_per_frame': float(avg_bits_per_frame) if not np.isnan(avg_bits_per_frame) else 0.0,
                'embedding_strength_used': self.config.embedding_strength
            }
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            return {}
        """        try:
            if not VIDEO_AVAILABLE:
                raise ValueError("Video processing libraries not available")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            codec = cv2.VideoWriter_fourcc(*'mp4v')
            
            # Create output video writer
            out = cv2.VideoWriter(output_path, codec, fps, (width, height))
            
            # Frame selection strategy
            if frame_selection == "uniform":
                frames_to_watermark = list(range(0, total_frames, self.frame_skip))
            elif frame_selection == "keyframes":
                frames_to_watermark = await self._detect_keyframes(video_path)
            elif frame_selection == "random":
                import random
                frames_to_watermark = sorted(random.sample(range(total_frames), 
                                                         min(total_frames // 10, 100)))
            else:
                frames_to_watermark = list(range(0, min(total_frames, self.max_frames), 10))
            
            # Strength parameters
            strength_params = {
                "light": {"alpha": 0.02, "quality": 95},
                "medium": {"alpha": 0.05, "quality": 90},
                "strong": {"alpha": 0.08, "quality": 85},
                "maximum": {"alpha": 0.12, "quality": 80}
            }
            
            params = strength_params.get(strength, strength_params["medium"])
            alpha = params["alpha"]
            
            # Process frames
            frame_count = 0
            watermarked_frames = 0
            data_bits = self._data_to_bits(watermark_data)
            
            # Load image watermarking engine
            from .image_engine import ImageWatermarkEngine
            image_engine = ImageWatermarkEngine()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count in frames_to_watermark:
                    try:
                        # Apply spatial watermarking to frame
                        if spatial_method == "dct":
                            watermarked_frame, embed_info = await image_engine.embed_dct_watermark(
                                frame, watermark_data, strength, "mid"
                            )
                        elif spatial_method == "dwt":
                            watermarked_frame, embed_info = await image_engine.embed_dwt_watermark(
                                frame, watermark_data, strength, "haar", 2
                            )
                        else:  # LSB fallback
                            watermarked_frame, embed_info = await image_engine.embed_lsb_watermark(
                                frame, watermark_data, strength, ["red", "green"]
                            )
                        
                        out.write(watermarked_frame)
                        watermarked_frames += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to watermark frame {frame_count}: {e}")
                        out.write(frame)  # Write original frame
                else:
                    out.write(frame)
                
                frame_count += 1
                
                # Progress logging
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames")
            
            # Cleanup
            cap.release()
            out.release()
            
            result_info = {
                "method": "frame_watermarking",
                "spatial_method": spatial_method,
                "strength": strength,
                "total_frames": total_frames,
                "watermarked_frames": watermarked_frames,
                "frame_selection": frame_selection,
                "frames_selected": len(frames_to_watermark),
                "video_properties": {
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "duration": total_frames / fps
                },
                "output_path": output_path,
                "robustness_level": "medium_high"
            }
            
            return result_info
            
        except Exception as e:
            logger.error(f"Frame watermarking failed: {str(e)}")
            raise
    
    async def embed_temporal_watermark(
        self,
        video_path: str,
        watermark_data: bytes,
        output_path: str,
        strength: str = "medium",
        temporal_method: str = "motion_vectors"
    ) -> Dict[str, Any]:
        """        Embeds watermark using temporal redundancy between frames
        Exploits motion estimation and temporal correlations
        """        try:
            if not VIDEO_AVAILABLE:
                raise ValueError("Video processing libraries not available")
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            codec = cv2.VideoWriter_fourcc(*'mp4v')
            
            out = cv2.VideoWriter(output_path, codec, fps, (width, height))
            
            # Strength parameters
            strength_params = {
                "light": {"motion_threshold": 0.5, "alpha": 0.01},
                "medium": {"motion_threshold": 1.0, "alpha": 0.03},
                "strong": {"motion_threshold": 1.5, "alpha": 0.05},
                "maximum": {"motion_threshold": 2.0, "alpha": 0.08}
            }
            
            params = strength_params.get(strength, strength_params["medium"])
            motion_threshold = params["motion_threshold"]
            alpha = params["alpha"]
            
            data_bits = self._data_to_bits(watermark_data)
            
            # Initialize temporal processing
            frame_buffer = []
            frame_count = 0
            watermarked_regions = 0
            
            # Motion detection setup
            prev_gray = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_gray is not None:
                    # Calculate optical flow
                    flow = cv2.calcOpticalFlowPyrLK(
                        prev_gray, current_gray, None, None,
                        winSize=(15, 15),
                        maxLevel=2,
                        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
                    )
                    
                    if temporal_method == "motion_vectors":
                        watermarked_frame = await self._embed_motion_vector_watermark(
                            frame, current_gray, prev_gray, watermark_data, 
                            alpha, motion_threshold
                        )
                    elif temporal_method == "frame_difference":
                        watermarked_frame = await self._embed_frame_difference_watermark(
                            frame, current_gray, prev_gray, watermark_data, 
                            alpha, frame_count
                        )
                    else:  # temporal_correlation
                        watermarked_frame = await self._embed_temporal_correlation_watermark(
                            frame, frame_buffer, watermark_data, alpha
                        )
                    
                    watermarked_regions += 1
                else:
                    watermarked_frame = frame
                
                out.write(watermarked_frame)
                
                # Update buffer and previous frame
                frame_buffer.append(frame.copy())
                if len(frame_buffer) > self.temporal_window:
                    frame_buffer.pop(0)
                
                prev_gray = current_gray.copy()
                frame_count += 1
                
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames")
            
            cap.release()
            out.release()
            
            result_info = {
                "method": "temporal_watermarking",
                "temporal_method": temporal_method,
                "strength": strength,
                "total_frames": total_frames,
                "watermarked_regions": watermarked_regions,
                "motion_threshold": motion_threshold,
                "alpha": alpha,
                "temporal_window": self.temporal_window,
                "video_properties": {
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "duration": total_frames / fps
                },
                "output_path": output_path,
                "robustness_level": "very_high"
            }
            
            return result_info
            
        except Exception as e:
            logger.error(f"Temporal watermarking failed: {str(e)}")
            raise
    
    async def embed_invisible_watermark(
        self,
        video_path: str,
        watermark_data: bytes,
        output_path: str,
        strength: str = "medium",
        method: str = "hybrid"
    ) -> Dict[str, Any]:
        """        Embeds completely invisible watermark using advanced techniques
        Combines multiple embedding strategies for maximum imperceptibility
        """        try:
            if not VIDEO_AVAILABLE:
                raise ValueError("Video processing libraries not available")
            
            # Use hybrid approach combining spatial and temporal methods
            if method == "hybrid":
                # First pass: temporal watermarking
                temp_path = output_path.replace('.mp4', '_temp.mp4')
                temporal_result = await self.embed_temporal_watermark(
                    video_path, watermark_data, temp_path, strength, "motion_vectors"
                )
                
                # Second pass: spatial watermarking on selected frames
                final_result = await self.embed_frame_watermark(
                    temp_path, watermark_data, output_path, strength, "keyframes", "dct"
                )
                
                # Clean up temp file
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                result_info = {
                    "method": "hybrid_invisible",
                    "passes": ["temporal", "spatial"],
                    "temporal_result": temporal_result,
                    "spatial_result": final_result,
                    "robustness_level": "maximum"
                }
                
            elif method == "perceptual":
                # Use perceptual masking
                result_info = await self._embed_perceptual_watermark(
                    video_path, watermark_data, output_path, strength
                )
                
            else:  # adaptive
                result_info = await self._embed_adaptive_watermark(
                    video_path, watermark_data, output_path, strength
                )
            
            return result_info
            
        except Exception as e:
            logger.error(f"Invisible watermarking failed: {str(e)}")
            raise
    
    async def detect_video_watermark(
        self,
        video_path: str,
        detection_method: str = "auto",
        reference_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Detects and extracts watermark from video
        Supports multiple detection strategies
        """        try:
            if not VIDEO_AVAILABLE:
                raise ValueError("Video processing libraries not available")
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            detections = []
            confidence_scores = []
            
            # Load image watermarking engine for frame analysis
            from .image_engine import ImageWatermarkEngine
            image_engine = ImageWatermarkEngine()
            
            frame_count = 0
            sample_frames = min(50, total_frames // 10)  # Sample frames for detection
            
            while frame_count < sample_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip frames for sampling
                if frame_count % (total_frames // sample_frames) != 0:
                    frame_count += 1
                    continue
                
                # Try different detection methods on frame
                frame_detections = []
                
                if detection_method in ["auto", "dct"]:
                    try:
                        detected, info = await image_engine.detect_watermark(
                            frame, None, "DCT", reference_data or {}
                        )
                        if detected:
                            frame_detections.append(("DCT", info))
                    except:
                        pass
                
                if detection_method in ["auto", "dwt"]:
                    try:
                        detected, info = await image_engine.detect_watermark(
                            frame, None, "DWT", reference_data or {}
                        )
                        if detected:
                            frame_detections.append(("DWT", info))
                    except:
                        pass
                
                if detection_method in ["auto", "lsb"]:
                    try:
                        detected, info = await image_engine.detect_watermark(
                            frame, None, "LSB", reference_data or {}
                        )
                        if detected:
                            frame_detections.append(("LSB", info))
                    except:
                        pass
                
                detections.extend(frame_detections)
                frame_count += 1
            
            cap.release()
            
            # Analyze detection results
            if detections:
                # Calculate overall confidence
                confidences = [det[1].get("confidence", 0) for det in detections]
                avg_confidence = np.mean(confidences)
                max_confidence = np.max(confidences)
                
                # Find most consistent method
                method_counts = {}
                for method, _ in detections:
                    method_counts[method] = method_counts.get(method, 0) + 1
                
                most_common_method = max(method_counts.items(), key=lambda x: x[1])
                
                # Extract watermark data from best detection
                best_detection = max(detections, key=lambda x: x[1].get("confidence", 0))
                
                result = {
                    "watermark_detected": True,
                    "confidence": avg_confidence,
                    "max_confidence": max_confidence,
                    "detection_method": best_detection[0],
                    "frames_analyzed": sample_frames,
                    "detections_found": len(detections),
                    "method_distribution": method_counts,
                    "extracted_data": best_detection[1].get("extracted_data"),
                    "most_common_method": most_common_method
                }
            else:
                result = {
                    "watermark_detected": False,
                    "confidence": 0.0,
                    "frames_analyzed": sample_frames,
                    "detections_found": 0,
                    "message": "No watermark detected in sampled frames"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Video watermark detection failed: {str(e)}")
            return {
                "watermark_detected": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    # Helper methods
    
    async def _detect_keyframes(self, video_path: str) -> List[int]:
        """Detects keyframes in video for strategic watermark placement"""        try:
            cap = cv2.VideoCapture(video_path)
            keyframes = []
            frame_count = 0
            prev_frame = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate structural similarity
                    diff = cv2.absdiff(gray, prev_frame)
                    diff_score = np.mean(diff)
                    
                    # Keyframe threshold
                    if diff_score > 30:  # Significant scene change
                        keyframes.append(frame_count)
                
                prev_frame = gray.copy()
                frame_count += 1
                
                # Limit processing for performance
                if frame_count > 1000:
                    break
            
            cap.release()
            
            # Ensure minimum keyframes
            if len(keyframes) < 10:
                total_frames = frame_count
                keyframes = list(range(0, total_frames, total_frames // 20))
            
            return keyframes[:100]  # Limit to 100 keyframes
            
        except Exception as e:
            logger.error(f"Keyframe detection failed: {e}")
            return list(range(0, 1000, 50))  # Fallback
    
    async def _embed_motion_vector_watermark(
        self,
        frame: np.ndarray,
        current_gray: np.ndarray,
        prev_gray: np.ndarray,
        watermark_data: bytes,
        alpha: float,
        motion_threshold: float
    ) -> np.ndarray:
        """Embeds watermark in motion vector field"""        try:
            # Calculate dense optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                prev_gray, current_gray, None, None,
                winSize=(15, 15), maxLevel=2,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
            )
            
            # Create motion magnitude map
            motion_mag = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2) if flow is not None else np.zeros_like(current_gray)
            
            # Find high motion regions
            high_motion = motion_mag > motion_threshold
            
            # Embed in high motion regions (less noticeable)
            watermarked_frame = frame.copy().astype(np.float32)
            data_bits = self._data_to_bits(watermark_data)
            
            bit_index = 0
            for y in range(0, frame.shape[0], 8):
                for x in range(0, frame.shape[1], 8):
                    if bit_index >= len(data_bits):
                        break
                    
                    if y < high_motion.shape[0] and x < high_motion.shape[1]:
                        if high_motion[y, x]:
                            bit = data_bits[bit_index]
                            
                            # Modify pixel values slightly
                            modification = alpha * 255 * (2 * bit - 1)
                            watermarked_frame[y:y+8, x:x+8, :] += modification
                            
                            bit_index += 1
            
            return np.clip(watermarked_frame, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Motion vector watermarking failed: {e}")
            return frame
    
    async def _embed_frame_difference_watermark(
        self,
        frame: np.ndarray,
        current_gray: np.ndarray,
        prev_gray: np.ndarray,
        watermark_data: bytes,
        alpha: float,
        frame_index: int
    ) -> np.ndarray:
        """Embeds watermark using frame differences"""        try:
            # Calculate frame difference
            diff = cv2.absdiff(current_gray, prev_gray)
            
            # Find stable regions (low difference)
            stable_regions = diff < 10
            
            watermarked_frame = frame.copy().astype(np.float32)
            data_bits = self._data_to_bits(watermark_data)
            
            # Use frame index to determine bit position
            bit_index = frame_index % len(data_bits)
            bit = data_bits[bit_index]
            
            # Embed in stable regions
            y_coords, x_coords = np.where(stable_regions)
            
            if len(y_coords) > 0:
                # Select random subset of stable pixels
                indices = np.random.choice(len(y_coords), 
                                         min(len(y_coords), 100), replace=False)
                
                for idx in indices:
                    y, x = y_coords[idx], x_coords[idx]
                    modification = alpha * 255 * (2 * bit - 1)
                    watermarked_frame[y, x, :] += modification
            
            return np.clip(watermarked_frame, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Frame difference watermarking failed: {e}")
            return frame
    
    async def _embed_temporal_correlation_watermark(
        self,
        frame: np.ndarray,
        frame_buffer: List[np.ndarray],
        watermark_data: bytes,
        alpha: float
    ) -> np.ndarray:
        """Embeds watermark using temporal correlations"""        try:
            if len(frame_buffer) < 3:
                return frame
            
            # Calculate temporal variance
            frame_stack = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) 
                                  for f in frame_buffer[-3:]], axis=2)
            temporal_var = np.var(frame_stack, axis=2)
            
            # Find temporally stable regions
            stable_mask = temporal_var < 5
            
            watermarked_frame = frame.copy().astype(np.float32)
            data_bits = self._data_to_bits(watermark_data)
            
            # Embed in stable temporal regions
            y_coords, x_coords = np.where(stable_mask)
            
            if len(y_coords) > len(data_bits):
                # Spread bits across stable regions
                step = len(y_coords) // len(data_bits)
                
                for i, bit in enumerate(data_bits):
                    if i * step < len(y_coords):
                        y, x = y_coords[i * step], x_coords[i * step]
                        modification = alpha * 255 * (2 * bit - 1)
                        watermarked_frame[y, x, :] += modification
            
            return np.clip(watermarked_frame, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Temporal correlation watermarking failed: {e}")
            return frame


# Batch processing utilities

async def batch_process_videos(video_paths: List[str],
                             watermark_data: bytes,
                             output_directory: str,
                             config: Optional[VideoWatermarkConfig] = None,
                             max_concurrent: int = 2) -> List[Dict[str, Any]]:
    """    Batch process multiple videos for watermarking
    
    Args:
        video_paths: List of input video file paths
        watermark_data: Binary data to embed
        output_directory: Directory for output files
        config: Watermarking configuration
        max_concurrent: Maximum concurrent processing tasks
        
    Returns:
        List of processing results
    """    try:
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        engine = VideoWatermarkEngine(config)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_video(video_path: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    input_path = Path(video_path)
                    output_path = output_dir / f"watermarked_{input_path.name}"
                    
                    result = await engine.embed_watermark(
                        str(input_path),
                        watermark_data,
                        str(output_path)
                    )
                    
                    result['input_path'] = str(input_path)
                    return result
                    
                except Exception as e:
                    logger.error(f"Error processing {video_path}: {e}")
                    return {
                        'success': False,
                        'input_path': video_path,
                        'error': str(e)
                    }
        
        # Process all videos concurrently
        tasks = [process_single_video(path) for path in video_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'input_path': video_paths[i],
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
        
    except Exception as e:
        logger.error(f"Error in batch video processing: {e}")
        return []


# Quality assessment utilities

async def assess_video_watermark_quality(original_path: str,
                                       watermarked_path: str,
                                       sample_frames: int = 10) -> Dict[str, Any]:
    """    Assess quality of watermarked video
    
    Args:
        original_path: Path to original video
        watermarked_path: Path to watermarked video
        sample_frames: Number of frames to sample for assessment
        
    Returns:
        Quality assessment results
    """    try:
        if not VIDEO_AVAILABLE:
            raise ValueError("Video processing libraries not available")
        
        # Open videos
        original_cap = cv2.VideoCapture(original_path)
        watermarked_cap = cv2.VideoCapture(watermarked_path)
        
        if not original_cap.isOpened() or not watermarked_cap.isOpened():
            raise ValueError("Could not open video files for quality assessment")
        
        # Get video info
        frame_count = int(original_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
        
        psnr_values = []
        ssim_values = []
        
        for frame_idx in frame_indices:
            # Seek to frame
            original_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            watermarked_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            
            ret1, orig_frame = original_cap.read()
            ret2, water_frame = watermarked_cap.read()
            
            if ret1 and ret2:
                # Calculate PSNR
                mse = np.mean((orig_frame.astype(float) - water_frame.astype(float)) ** 2)
                if mse > 0:
                    psnr = 20 * np.log10(255.0 / np.sqrt(mse))
                    psnr_values.append(psnr)
                
                # Calculate SSIM (simplified)
                orig_gray = cv2.cvtColor(orig_frame, cv2.COLOR_BGR2GRAY)
                water_gray = cv2.cvtColor(water_frame, cv2.COLOR_BGR2GRAY)
                
                if MULTIMEDIA_AVAILABLE:
                    try:
                        import skimage.metrics
                        ssim = skimage.metrics.structural_similarity(orig_gray, water_gray, data_range=255)
                        ssim_values.append(ssim)
                    except ImportError:
                        pass
        
        original_cap.release()
        watermarked_cap.release()
        
        # Calculate statistics
        quality_metrics = {
            'psnr': {
                'mean': np.mean(psnr_values) if psnr_values else 0.0,
                'std': np.std(psnr_values) if psnr_values else 0.0,
                'min': np.min(psnr_values) if psnr_values else 0.0,
                'max': np.max(psnr_values) if psnr_values else 0.0
            },
            'ssim': {
                'mean': np.mean(ssim_values) if ssim_values else 0.0,
                'std': np.std(ssim_values) if ssim_values else 0.0,
                'min': np.min(ssim_values) if ssim_values else 0.0,
                'max': np.max(ssim_values) if ssim_values else 0.0
            },
            'frames_analyzed': len(frame_indices),
            'quality_level': 'excellent' if (np.mean(psnr_values) if psnr_values else 0) > 40 else 'good'
        }
        
        return quality_metrics
        
    except Exception as e:
        logger.error(f"Error in video quality assessment: {e}")
        return {
            'error': str(e),
            'frames_analyzed': 0
        }


# Factory functions

def create_video_watermark_engine(technique: VideoWatermarkTechnique = VideoWatermarkTechnique.FRAME_DCT,
                                frame_selection: VideoFrameSelection = VideoFrameSelection.UNIFORM,
                                quality_level: VideoQualityLevel = VideoQualityLevel.STREAMING) -> VideoWatermarkEngine:
    """    Factory function to create video watermark engine with common configurations
    """    config = VideoWatermarkConfig(
        technique=technique,
        frame_selection=frame_selection,
        quality_level=quality_level,
        frame_interval=10,
        max_frames=1000,
        temporal_window=5,
        spatial_block_size=8,
        embedding_strength=0.1,
        motion_threshold=0.5,
        preserve_keyframes=True,
        codec_compatibility=True
    )
    
    return VideoWatermarkEngine(config)


def create_high_quality_config() -> VideoWatermarkConfig:
    """Create configuration for high quality video watermarking"""    return VideoWatermarkConfig(
        technique=VideoWatermarkTechnique.FRAME_DCT,
        frame_selection=VideoFrameSelection.ADAPTIVE,
        quality_level=VideoQualityLevel.BROADCAST,
        frame_interval=20,
        max_frames=2000,
        temporal_window=10,
        spatial_block_size=8,
        embedding_strength=0.05,
        motion_threshold=0.3,
        preserve_keyframes=True,
        codec_compatibility=True
    )


def create_robust_config() -> VideoWatermarkConfig:
    """Create configuration for robust video watermarking"""    return VideoWatermarkConfig(
        technique=VideoWatermarkTechnique.SPATIAL_TEMPORAL,
        frame_selection=VideoFrameSelection.UNIFORM,
        quality_level=VideoQualityLevel.COMPRESSED,
        frame_interval=5,
        max_frames=1500,
        temporal_window=15,
        spatial_block_size=16,
        embedding_strength=0.2,
        motion_threshold=0.7,
        preserve_keyframes=False,
        codec_compatibility=True
    )


# Video format utilities

def get_supported_video_formats() -> List[str]:
    """Get list of supported video formats"""    return [
        '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',
        '.webm', '.m4v', '.3gp', '.ogv'
    ]


def validate_video_file(file_path: str) -> Dict[str, Any]:
    """Validate video file format and properties"""    try:
        path = Path(file_path)
        
        if not path.exists():
            return {'valid': False, 'error': 'File does not exist'}
        
        if path.suffix.lower() not in get_supported_video_formats():
            return {'valid': False, 'error': f'Unsupported format: {path.suffix}'}
        
        if not VIDEO_AVAILABLE:
            return {'valid': True, 'warning': 'Video libraries not available for detailed validation'}
        
        # Try to open with OpenCV
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return {'valid': False, 'error': 'Could not open video file'}
        
        # Get basic properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        return {
            'valid': True,
            'properties': {
                'frame_count': frame_count,
                'fps': fps,
                'width': width,
                'height': height,
                'duration_seconds': frame_count / fps if fps > 0 else 0,
                'file_size_mb': path.stat().st_size / (1024 * 1024)
            }
        }
        
    except Exception as e:
        return {'valid': False, 'error': str(e)}


__all__ = [
    'VideoWatermarkEngine',
    'VideoWatermarkTechnique',
    'VideoFrameSelection',
    'VideoQualityLevel',
    'VideoWatermarkConfig',
    'FrameMetadata',
    'SpatialWatermarkEmbedder',
    'TemporalWatermarkEmbedder',
    'MotionAnalyzer',
    'SceneDetector',
    'batch_process_videos',
    'assess_video_watermark_quality',
    'create_video_watermark_engine',
    'create_high_quality_config',
    'create_robust_config',
    'get_supported_video_formats',
    'validate_video_file'
]
