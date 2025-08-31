"""
Image Watermarking Core Engine
Advanced digital watermarking for image content with multiple embedding techniques
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

try:
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    from scipy.fft import dct, idct
    import pywt
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImageWatermarkEngine:
    """Professional image watermarking engine with multiple embedding techniques"""
    
    def __init__(self):
        self.block_size = 8  # For DCT
        self.max_payload = 1024  # Maximum bytes to embed
        
    async def embed_lsb_watermark(
        self,
        image_data: np.ndarray,
        watermark_data: bytes,
        strength: str = "medium",
        color_channels: List[str] = ["red", "green", "blue"]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Embeds watermark using Least Significant Bit technique
        High capacity but vulnerable to compression
        """



        try:
            if not IMAGING_AVAILABLE:
                raise ValueError("Imaging libraries not available")
            
            height, width, channels = image_data.shape
            data_bits = self._data_to_bits(watermark_data)
            
            # Strength parameters
            strength_params = {
                "light": {"bit_depth": 1, "skip_ratio": 8},
                "medium": {"bit_depth": 2, "skip_ratio": 4},
                "strong": {"bit_depth": 3, "skip_ratio": 2},
                "maximum": {"bit_depth": 4, "skip_ratio": 1}
            }
            
            params = strength_params.get(strength, strength_params["medium"])
            bit_depth = params["bit_depth"]
            skip_ratio = params["skip_ratio"]
            
            # Calculate capacity
            total_pixels = height * width * len(color_channels)
            capacity_bits = (total_pixels // skip_ratio) * bit_depth
            capacity_bytes = capacity_bits // 8
            
            if len(data_bits) > capacity_bits:
                raise ValueError(f"Data too large: {len(data_bits)} bits > {capacity_bits} capacity")
            
            # Create copy for modification
            watermarked_image = image_data.copy()
            
            # Channel mapping
            channel_map = {"red": 0, "green": 1, "blue": 2}
            
            bit_index = 0
            positions_used = []
            
            for y in range(0, height, skip_ratio):
                for x in range(0, width, skip_ratio):
                    for channel_name in color_channels:
                        if bit_index >= len(data_bits):
                            break
                        
                        channel_idx = channel_map[channel_name]
                        pixel_value = watermarked_image[y, x, channel_idx]
                        
                        # Embed bits in LSBs
                        for bit_pos in range(bit_depth):
                            if bit_index >= len(data_bits):
                                break
                            
                            bit_to_embed = data_bits[bit_index]
                            
                            # Clear the target bit and set new value
                            pixel_value = pixel_value & ~(1 << bit_pos)
                            pixel_value = pixel_value | (bit_to_embed << bit_pos)
                            
                            watermarked_image[y, x, channel_idx] = pixel_value
                            positions_used.append((y, x, channel_idx, bit_pos))
                            bit_index += 1
                    
                    if bit_index >= len(data_bits):
                        break
                if bit_index >= len(data_bits):
                    break
            
            # Calculate quality metrics
            mse = np.mean((image_data.astype(float) - watermarked_image.astype(float)) ** 2)
            psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
            
            result_info = {
                "method": "LSB",
                "strength": strength,
                "bit_depth": bit_depth,
                "data_embedded_bits": bit_index,
                "capacity_utilization": bit_index / capacity_bits,
                "positions_used": len(positions_used),
                "psnr": psnr,
                "channels_used": color_channels,
                "robustness_level": "low"  # LSB is fragile
            }
            
            return watermarked_image, result_info
            
        except Exception as e:
            logger.error(f"LSB watermarking failed: {str(e)}")
            raise
    
    async def embed_dct_watermark(
        self,
        image_data: np.ndarray,
        watermark_data: bytes,
        strength: str = "medium",
        frequency_band: str = "mid"
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Embeds watermark using Discrete Cosine Transform
        More robust to compression than LSB
        """



        try:
            if not IMAGING_AVAILABLE:
                raise ValueError("Imaging libraries not available")
            
            # Convert to YUV for better embedding
            image_yuv = cv2.cvtColor(image_data, cv2.COLOR_RGB2YUV)
            y_channel = image_yuv[:, :, 0].astype(np.float32)
            
            height, width = y_channel.shape
            data_bits = self._data_to_bits(watermark_data)
            
            # Strength parameters
            strength_params = {
                "light": {"alpha": 10, "quantization": 50},
                "medium": {"alpha": 20, "quantization": 30},
                "strong": {"alpha": 35, "quantization": 20},
                "maximum": {"alpha": 50, "quantization": 10}
            }
            
            params = strength_params.get(strength, strength_params["medium"])
            alpha = params["alpha"]
            quantization = params["quantization"]
            
            # Frequency band selection
            band_coefficients = {
                "low": [(1, 0), (0, 1), (1, 1)],
                "mid": [(2, 1), (1, 2), (2, 2), (3, 1), (1, 3)],
                "high": [(3, 2), (2, 3), (3, 3), (4, 2), (2, 4)]
            }
            
            target_coeffs = band_coefficients.get(frequency_band, band_coefficients["mid"])
            
            # Process in 8x8 blocks
            watermarked_y = y_channel.copy()
            blocks_processed = 0
            bit_index = 0
            
            for y in range(0, height - self.block_size + 1, self.block_size):
                for x in range(0, width - self.block_size + 1, self.block_size):
                    if bit_index >= len(data_bits):
                        break
                    
                    # Extract block
                    block = watermarked_y[y:y+self.block_size, x:x+self.block_size]
                    
                    # Apply DCT
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    
                    # Embed bits in selected coefficients
                    for coeff_y, coeff_x in target_coeffs:
                        if bit_index >= len(data_bits):
                            break
                        
                        if coeff_y < self.block_size and coeff_x < self.block_size:
                            bit_to_embed = data_bits[bit_index]
                            current_coeff = dct_block[coeff_y, coeff_x]
                            
                            # Quantization-based embedding
                            quantized = np.round(current_coeff / quantization)
                            
                            if bit_to_embed == 1:
                                if quantized % 2 == 0:
                                    quantized += 1
                            else:
                                if quantized % 2 == 1:
                                    quantized += 1 if quantized > 0 else -1
                            
                            dct_block[coeff_y, coeff_x] = quantized * quantization + alpha * (2 * bit_to_embed - 1)
                            bit_index += 1
                    
                    # Apply inverse DCT
                    modified_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                    watermarked_y[y:y+self.block_size, x:x+self.block_size] = modified_block
                    blocks_processed += 1
                
                if bit_index >= len(data_bits):
                    break
            
            # Reconstruct image
            watermarked_yuv = image_yuv.copy()
            watermarked_yuv[:, :, 0] = np.clip(watermarked_y, 0, 255).astype(np.uint8)
            watermarked_image = cv2.cvtColor(watermarked_yuv, cv2.COLOR_YUV2RGB)
            
            # Calculate quality metrics
            mse = np.mean((image_data.astype(float) - watermarked_image.astype(float)) ** 2)
            psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
            
            result_info = {
                "method": "DCT",
                "strength": strength,
                "alpha": alpha,
                "quantization": quantization,
                "frequency_band": frequency_band,
                "blocks_processed": blocks_processed,
                "data_embedded_bits": bit_index,
                "coefficients_per_block": len(target_coeffs),
                "psnr": psnr,
                "robustness_level": "high"
            }
            
            return watermarked_image, result_info
            
        except Exception as e:
            logger.error(f"DCT watermarking failed: {str(e)}")
            raise
    
    async def embed_dwt_watermark(
        self,
        image_data: np.ndarray,
        watermark_data: bytes,
        strength: str = "medium",
        wavelet: str = "haar",
        decomposition_level: int = 2
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Embeds watermark using Discrete Wavelet Transform
        Excellent robustness against geometric attacks
        """



        try:
            if not IMAGING_AVAILABLE:
                raise ValueError("Imaging libraries not available")
            
            # Convert to grayscale for DWT processing
            if len(image_data.shape) == 3:
                gray_channel = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
            else:
                gray_channel = image_data.copy()
            
            gray_channel = gray_channel.astype(np.float32)
            data_bits = self._data_to_bits(watermark_data)
            
            # Strength parameters
            strength_params = {
                "light": {"alpha": 0.01, "subband": "HL"},
                "medium": {"alpha": 0.03, "subband": "LH"},
                "strong": {"alpha": 0.05, "subband": "HH"},
                "maximum": {"alpha": 0.08, "subband": "LL"}
            }
            
            params = strength_params.get(strength, strength_params["medium"])
            alpha = params["alpha"]
            target_subband = params["subband"]
            
            # Multi-level DWT decomposition
            coeffs = pywt.wavedec2(gray_channel, wavelet, level=decomposition_level)
            
            # Select embedding location based on decomposition level
            if decomposition_level >= 1:
                target_level = 1  # Use first detail level
                cA, (cH, cV, cD) = coeffs[0], coeffs[target_level]
                
                subband_map = {
                    "LL": cA,
                    "HL": cH,
                    "LH": cV,
                    "HH": cD
                }
                
                target_coefficients = subband_map[target_subband]
            else:
                target_coefficients = coeffs[0]
            
            # Flatten coefficients for embedding
            flat_coeffs = target_coefficients.flatten()
            
            # Select significant coefficients for embedding
            significant_indices = np.where(np.abs(flat_coeffs) > np.mean(np.abs(flat_coeffs)))[0]
            
            if len(significant_indices) < len(data_bits):
                raise ValueError(f"Insufficient capacity: {len(significant_indices)} < {len(data_bits)}")
            
            # Embed data
            modified_coeffs = flat_coeffs.copy()
            bit_index = 0
            
            for idx in significant_indices[:len(data_bits)]:
                bit_to_embed = data_bits[bit_index]
                current_coeff = modified_coeffs[idx]
                
                # Adaptive embedding based on coefficient magnitude
                modification = alpha * np.abs(current_coeff)
                
                if bit_to_embed == 1:
                    modified_coeffs[idx] = current_coeff + modification
                else:
                    modified_coeffs[idx] = current_coeff - modification
                
                bit_index += 1
            
            # Reshape back to original subband shape
            modified_subband = modified_coeffs.reshape(target_coefficients.shape)
            
            # Update coefficients
            if target_subband == "LL":
                coeffs = list(coeffs)
                coeffs[0] = modified_subband
            else:
                modified_details = list(coeffs[target_level])
                subband_index = ["HL", "LH", "HH"].index(target_subband)
                modified_details[subband_index] = modified_subband
                coeffs = list(coeffs)
                coeffs[target_level] = tuple(modified_details)
            
            # Inverse DWT
            watermarked_gray = pywt.waverec2(coeffs, wavelet)
            watermarked_gray = np.clip(watermarked_gray, 0, 255).astype(np.uint8)
            
            # Convert back to original format
            if len(image_data.shape) == 3:
                watermarked_image = image_data.copy()
                # Apply changes proportionally to all channels
                for channel in range(3):
                    scale_factor = watermarked_gray.astype(float) / (gray_channel + 1e-8)
                    watermarked_image[:, :, channel] = np.clip(
                        image_data[:, :, channel].astype(float) * scale_factor, 0, 255
                    ).astype(np.uint8)
            else:
                watermarked_image = watermarked_gray
            
            # Calculate quality metrics
            mse = np.mean((image_data.astype(float) - watermarked_image.astype(float)) ** 2)
            psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
            
            result_info = {
                "method": "DWT",
                "strength": strength,
                "alpha": alpha,
                "wavelet": wavelet,
                "decomposition_level": decomposition_level,
                "target_subband": target_subband,
                "coefficients_modified": bit_index,
                "capacity_used": bit_index / len(significant_indices),
                "psnr": psnr,
                "robustness_level": "very_high"
            }
            
            return watermarked_image, result_info
            
        except Exception as e:
            logger.error(f"DWT watermarking failed: {str(e)}")
            raise
    
    async def detect_watermark(
        self,
        watermarked_image: np.ndarray,
        original_image: Optional[np.ndarray],
        method: str,
        embedding_params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Detects and extracts watermark from image
        Returns detection result with confidence score
        """



        try:
            if method == "LSB":
                return await self._detect_lsb_watermark(watermarked_image, embedding_params)
            elif method == "DCT":
                return await self._detect_dct_watermark(watermarked_image, embedding_params)
            elif method == "DWT":
                return await self._detect_dwt_watermark(watermarked_image, embedding_params)
            else:
                raise ValueError(f"Unsupported detection method: {method}")
                
        except Exception as e:
            logger.error(f"Watermark detection failed: {str(e)}")
            return False, {"error": str(e), "confidence": 0.0}
    
    def _data_to_bits(self, data: bytes) -> List[int]:
        """Converts byte data to bit array"""
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return bits
    
    def _bits_to_data(self, bits: List[int]) -> bytes:
        """Converts bit array back to byte data"""
        data = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= bits[i + j] << (7 - j)
            data.append(byte)
        return bytes(data)
    
    async def _detect_lsb_watermark(
        self,
        watermarked_image: np.ndarray,
        params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Detects LSB watermark"""



        try:
            height, width, channels = watermarked_image.shape
            bit_depth = params.get("bit_depth", 2)
            skip_ratio = params.get("skip_ratio", 4)
            color_channels = params.get("channels_used", ["red", "green", "blue"])
            expected_bits = params.get("data_embedded_bits", 0)
            
            channel_map = {"red": 0, "green": 1, "blue": 2}
            extracted_bits = []
            
            for y in range(0, height, skip_ratio):
                for x in range(0, width, skip_ratio):
                    for channel_name in color_channels:
                        if len(extracted_bits) >= expected_bits:
                            break
                        
                        channel_idx = channel_map[channel_name]
                        pixel_value = watermarked_image[y, x, channel_idx]
                        
                        for bit_pos in range(bit_depth):
                            if len(extracted_bits) >= expected_bits:
                                break
                            
                            bit = (pixel_value >> bit_pos) & 1
                            extracted_bits.append(bit)
                    
                    if len(extracted_bits) >= expected_bits:
                        break
                if len(extracted_bits) >= expected_bits:
                    break
            
            # Try to decode extracted bits
            if len(extracted_bits) >= 64:  # Minimum viable data
                try:
                    extracted_data = self._bits_to_data(extracted_bits[:expected_bits])
                    decoded_json = extracted_data.decode('utf-8')
                    watermark_data = json.loads(decoded_json)
                    
                    confidence = min(0.95, len(extracted_bits) / expected_bits)
                    
                    return True, {
                        "confidence": confidence,
                        "extracted_data": watermark_data,
                        "bits_extracted": len(extracted_bits),
                        "method": "LSB"
                    }
                except:
                    pass
            
            return False, {
                "confidence": 0.0,
                "error": "Could not decode watermark data",
                "bits_extracted": len(extracted_bits)
            }
            
        except Exception as e:
            return False, {"error": str(e), "confidence": 0.0}
    
    async def _detect_dct_watermark(
        self,
        watermarked_image: np.ndarray,
        params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Detects DCT watermark"""



        try:
            # Convert to YUV
            image_yuv = cv2.cvtColor(watermarked_image, cv2.COLOR_RGB2YUV)
            y_channel = image_yuv[:, :, 0].astype(np.float32)
            
            height, width = y_channel.shape
            quantization = params.get("quantization", 30)
            frequency_band = params.get("frequency_band", "mid")
            expected_bits = params.get("data_embedded_bits", 0)
            
            # Frequency band coefficients
            band_coefficients = {
                "low": [(1, 0), (0, 1), (1, 1)],
                "mid": [(2, 1), (1, 2), (2, 2), (3, 1), (1, 3)],
                "high": [(3, 2), (2, 3), (3, 3), (4, 2), (2, 4)]
            }
            
            target_coeffs = band_coefficients.get(frequency_band, band_coefficients["mid"])
            extracted_bits = []
            
            for y in range(0, height - self.block_size + 1, self.block_size):
                for x in range(0, width - self.block_size + 1, self.block_size):
                    if len(extracted_bits) >= expected_bits:
                        break
                    
                    # Extract block and apply DCT
                    block = y_channel[y:y+self.block_size, x:x+self.block_size]
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    
                    # Extract bits from coefficients
                    for coeff_y, coeff_x in target_coeffs:
                        if len(extracted_bits) >= expected_bits:
                            break
                        
                        if coeff_y < self.block_size and coeff_x < self.block_size:
                            coeff_value = dct_block[coeff_y, coeff_x]
                            quantized = np.round(coeff_value / quantization)
                            
                            # Extract bit based on parity
                            extracted_bit = int(quantized % 2)
                            extracted_bits.append(extracted_bit)
                
                if len(extracted_bits) >= expected_bits:
                    break
            
            # Decode extracted data
            if len(extracted_bits) >= 64:
                try:
                    extracted_data = self._bits_to_data(extracted_bits[:expected_bits])
                    decoded_json = extracted_data.decode('utf-8')
                    watermark_data = json.loads(decoded_json)
                    
                    confidence = min(0.90, len(extracted_bits) / expected_bits)
                    
                    return True, {
                        "confidence": confidence,
                        "extracted_data": watermark_data,
                        "bits_extracted": len(extracted_bits),
                        "method": "DCT"
                    }
                except:
                    pass
            
            return False, {
                "confidence": 0.0,
                "error": "Could not decode DCT watermark",
                "bits_extracted": len(extracted_bits)
            }
            
        except Exception as e:
            return False, {"error": str(e), "confidence": 0.0}
    
    async def _detect_dwt_watermark(
        self,
        watermarked_image: np.ndarray,
        params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Detects DWT watermark"""



        try:
            # Convert to grayscale
            if len(watermarked_image.shape) == 3:
                gray_channel = cv2.cvtColor(watermarked_image, cv2.COLOR_RGB2GRAY)
            else:
                gray_channel = watermarked_image.copy()
            
            gray_channel = gray_channel.astype(np.float32)
            
            wavelet = params.get("wavelet", "haar")
            decomposition_level = params.get("decomposition_level", 2)
            target_subband = params.get("target_subband", "LH")
            expected_bits = params.get("data_embedded_bits", 0)
            
            # DWT decomposition
            coeffs = pywt.wavedec2(gray_channel, wavelet, level=decomposition_level)
            
            # Select target subband
            if decomposition_level >= 1:
                target_level = 1
                cA, (cH, cV, cD) = coeffs[0], coeffs[target_level]
                
                subband_map = {
                    "LL": cA,
                    "HL": cH,
                    "LH": cV,
                    "HH": cD
                }
                
                target_coefficients = subband_map[target_subband]
            else:
                target_coefficients = coeffs[0]
            
            flat_coeffs = target_coefficients.flatten()
            significant_indices = np.where(np.abs(flat_coeffs) > np.mean(np.abs(flat_coeffs)))[0]
            
            # This is a simplified detection - in practice, you'd need the original
            # or use correlation-based detection
            confidence = min(1.0, len(significant_indices) / expected_bits) if expected_bits > 0 else 0.5
            
            return True, {
                "confidence": confidence,
                "method": "DWT",
                "coefficients_analyzed": len(significant_indices),
                "note": "DWT detection requires original image for accurate extraction"
            }
            
        except Exception as e:
            return False, {"error": str(e), "confidence": 0.0}
