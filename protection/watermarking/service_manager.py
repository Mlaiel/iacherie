"""Watermarking Service Manager
Central orchestration and management for all watermarking operations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import hashlib
import uuid
from pathlib import Path
import tempfile
import io

from .image_engine import ImageWatermarkEngine
from .video_engine import VideoWatermarkEngine  
from .text_engine import TextWatermarkEngine
from .blockchain_registry import BlockchainWatermarkRegistry
from .forensic_analyzer import ForensicWatermarkAnalyzer

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """
Supported content types for watermarking"""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class WatermarkOperation(Enum):
    """Watermarking operations"""

    EMBED = "embed"
    DETECT = "detect"
    VERIFY = "verify"
    EXTRACT = "extract"
    ANALYZE = "analyze"


@dataclass
class WatermarkRequest:
    """Watermark operation request"""
    operation: WatermarkOperation
    content_type: ContentType
    content_data: bytes
    watermark_data: Optional[bytes] = None
    owner_id: str = ""
    strength: str = "medium"
    method: str = "auto"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WatermarkResponse:
    """Watermark operation response"""
    success: bool
    operation: WatermarkOperation
    content_type: ContentType
    watermark_id: str
    processing_time: float
    confidence: float
    output_data: Optional[bytes] = None
    watermark_info: Dict[str, Any] = None
    blockchain_tx: str = ""
    forensic_evidence: Optional[Dict[str, Any]] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.watermark_info is None:
            self.watermark_info = {}


class WatermarkServiceManager:
    """
    Central watermarking service manager
    Orchestrates all watermarking operations across different content types
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engines = {}
        self.blockchain_registry = None
        self.forensic_analyzer = None
        
        # Performance tracking
        self.operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'processing_times': []
        }
        
        self._initialize_engines()
    
    def _initialize_engines(self):
        """
Initialize all watermarking engines"""
        try:
            # Initialize content-specific engines
            self.engines[ContentType.IMAGE] = ImageWatermarkEngine()
            self.engines[ContentType.VIDEO] = VideoWatermarkEngine()
            self.engines[ContentType.TEXT] = TextWatermarkEngine()
            
            # Initialize blockchain registry
            blockchain_config = self.config.get('blockchain', {})
            self.blockchain_registry = BlockchainWatermarkRegistry(blockchain_config)
            
            # Initialize forensic analyzer
            forensic_config = self.config.get('forensic', {})
            self.forensic_analyzer = ForensicWatermarkAnalyzer(forensic_config)
            
            logger.info("All watermarking engines initialized successfully")
            
        except Exception as e:
            logger.error(f"Engine initialization failed: {e}")
            raise
    
    async def process_watermark_request(self, request: WatermarkRequest) -> WatermarkResponse:
        """
        Main entry point for all watermarking operations
        Routes requests to appropriate engines and handles responses
        """
        start_time = datetime.now()
        watermark_id = str(uuid.uuid4())
        
        try:
            self.operation_stats['total_operations'] += 1
            
            # Validate request
            validation_result = await self._validate_request(request)
            if not validation_result['valid']:
                return WatermarkResponse(
                    success=False,
                    operation=request.operation,
                    content_type=request.content_type,
                    watermark_id=watermark_id,
                    processing_time=0.0,
                    confidence=0.0,
                    error_message=validation_result['error']
                )
            
            # Route to appropriate operation handler
            if request.operation == WatermarkOperation.EMBED:
                response = await self._handle_embed_operation(request, watermark_id)
            elif request.operation == WatermarkOperation.DETECT:
                response = await self._handle_detect_operation(request, watermark_id)
            elif request.operation == WatermarkOperation.VERIFY:
                response = await self._handle_verify_operation(request, watermark_id)
            elif request.operation == WatermarkOperation.EXTRACT:
                response = await self._handle_extract_operation(request, watermark_id)
            elif request.operation == WatermarkOperation.ANALYZE:
                response = await self._handle_analyze_operation(request, watermark_id)
            else:
                raise ValueError(f"Unsupported operation: {request.operation}")
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            response.processing_time = processing_time
            
            # Update statistics
            if response.success:
                self.operation_stats['successful_operations'] += 1
            else:
                self.operation_stats['failed_operations'] += 1
            
            self.operation_stats['processing_times'].append(processing_time)
            
            # Log operation
            await self._log_operation(request, response, processing_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Watermark operation failed: {e}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.operation_stats['failed_operations'] += 1
            
            return WatermarkResponse(
                success=False,
                operation=request.operation,
                content_type=request.content_type,
                watermark_id=watermark_id,
                processing_time=processing_time,
                confidence=0.0,
                error_message=str(e)
            )
    
    async def _handle_embed_operation(self, request: WatermarkRequest, watermark_id: str) -> WatermarkResponse:
        """Handles watermark embedding operations"""
        try:
            engine = self.engines.get(request.content_type)
            if not engine:
                raise ValueError(f"No engine available for content type: {request.content_type}")
            
            # Prepare watermark data
            if not request.watermark_data:
                watermark_payload = {
                    'watermark_id': watermark_id,
                    'owner_id': request.owner_id,
                    'timestamp': datetime.now().isoformat(),
                    'content_type': request.content_type.value,
                    'metadata': request.metadata
                }
                request.watermark_data = json.dumps(watermark_payload).encode('utf-8')
            
            # Content-specific embedding
            if request.content_type == ContentType.IMAGE:
                output_data, embed_info = await self._embed_image_watermark(
                    engine, request.content_data, request.watermark_data, request.strength, request.method
                )
            elif request.content_type == ContentType.VIDEO:
                output_data, embed_info = await self._embed_video_watermark(
                    engine, request.content_data, request.watermark_data, request.strength, request.method
                )
            elif request.content_type == ContentType.TEXT:
                output_data, embed_info = await self._embed_text_watermark(
                    engine, request.content_data, request.watermark_data, request.strength, request.method
                )
            else:
                raise ValueError(f"Embedding not supported for content type: {request.content_type}")
            
            # Register on blockchain
            blockchain_tx = ""
            if self.blockchain_registry:
                try:
                    content_hash = hashlib.sha256(request.content_data).hexdigest()
                    blockchain_result = await self.blockchain_registry.register_watermark(
                        embed_info, content_hash, request.owner_id
                    )
                    blockchain_tx = blockchain_result.get('blockchain_tx', '')
                except Exception as e:
                    logger.warning(f"Blockchain registration failed: {e}")
            
            return WatermarkResponse(
                success=True,
                operation=request.operation,
                content_type=request.content_type,
                watermark_id=watermark_id,
                processing_time=0.0,  # Will be set by caller
                confidence=embed_info.get('imperceptibility_score', 0.9),
                output_data=output_data,
                watermark_info=embed_info,
                blockchain_tx=blockchain_tx
            )
            
        except Exception as e:
            logger.error(f"Embed operation failed: {e}")
            raise
    
    async def _handle_detect_operation(self, request: WatermarkRequest, watermark_id: str) -> WatermarkResponse:
        """Handles watermark detection operations"""
        try:
            engine = self.engines.get(request.content_type)
            if not engine:
                raise ValueError(f"No engine available for content type: {request.content_type}")
            
            # Content-specific detection
            if request.content_type == ContentType.IMAGE:
                detection_result = await self._detect_image_watermark(
                    engine, request.content_data, request.method
                )
            elif request.content_type == ContentType.VIDEO:
                detection_result = await self._detect_video_watermark(
                    engine, request.content_data, request.method
                )
            elif request.content_type == ContentType.TEXT:
                detection_result = await self._detect_text_watermark(
                    engine, request.content_data, request.method
                )
            else:
                raise ValueError(f"Detection not supported for content type: {request.content_type}")
            
            detected = detection_result.get('watermark_detected', False)
            confidence = detection_result.get('confidence', 0.0)
            
            return WatermarkResponse(
                success=True,
                operation=request.operation,
                content_type=request.content_type,
                watermark_id=watermark_id,
                processing_time=0.0,
                confidence=confidence,
                watermark_info=detection_result
            )
            
        except Exception as e:
            logger.error(f"Detect operation failed: {e}")
            raise
    
    async def _handle_verify_operation(self, request: WatermarkRequest, watermark_id: str) -> WatermarkResponse:
        """Handles watermark verification operations"""
        try:
            # First detect watermark
            detection_response = await self._handle_detect_operation(request, watermark_id)
            
            if not detection_response.success or detection_response.confidence < 0.5:
                return WatermarkResponse(
                    success=False,
                    operation=request.operation,
                    content_type=request.content_type,
                    watermark_id=watermark_id,
                    processing_time=0.0,
                    confidence=0.0,
                    error_message="No reliable watermark detected for verification"
                )
            
            # Verify ownership using blockchain
            blockchain_verification = {}
            if self.blockchain_registry and request.owner_id:
                try:
                    content_hash = hashlib.sha256(request.content_data).hexdigest()
                    blockchain_verification = await self.blockchain_registry.verify_ownership(
                        content_hash, request.owner_id, detection_response.watermark_info
                    )
                except Exception as e:
                    logger.warning(f"Blockchain verification failed: {e}")
            
            # Combine detection and ownership verification
            overall_confidence = min(
                detection_response.confidence,
                blockchain_verification.get('confidence', 0.5)
            )
            
            verification_info = {
                'watermark_detection': detection_response.watermark_info,
                'blockchain_verification': blockchain_verification,
                'overall_confidence': overall_confidence,
                'verified_owner': request.owner_id,
                'verification_timestamp': datetime.now().isoformat()
            }
            
            return WatermarkResponse(
                success=True,
                operation=request.operation,
                content_type=request.content_type,
                watermark_id=watermark_id,
                processing_time=0.0,
                confidence=overall_confidence,
                watermark_info=verification_info
            )
            
        except Exception as e:
            logger.error(f"Verify operation failed: {e}")
            raise
    
    async def _handle_extract_operation(self, request: WatermarkRequest, watermark_id: str) -> WatermarkResponse:
        """Handles watermark extraction operations"""
        try:
            # Detection includes extraction for most methods
            detection_response = await self._handle_detect_operation(request, watermark_id)
            
            if detection_response.success:
                extracted_data = detection_response.watermark_info.get('extracted_data')
                
                # Try to decode watermark payload
                if extracted_data:
                    try:
                        if isinstance(extracted_data, dict):
                            decoded_payload = extracted_data
                        else:
                            decoded_payload = json.loads(extracted_data)
                        
                        extraction_info = {
                            'extracted_payload': decoded_payload,
                            'extraction_method': detection_response.watermark_info.get('method'),
                            'extraction_confidence': detection_response.confidence,
                            'extraction_timestamp': datetime.now().isoformat()
                        }
                        
                        return WatermarkResponse(
                            success=True,
                            operation=request.operation,
                            content_type=request.content_type,
                            watermark_id=watermark_id,
                            processing_time=0.0,
                            confidence=detection_response.confidence,
                            watermark_info=extraction_info
                        )
                    except:
                        pass
            
            return WatermarkResponse(
                success=False,
                operation=request.operation,
                content_type=request.content_type,
                watermark_id=watermark_id,
                processing_time=0.0,
                confidence=0.0,
                error_message="Could not extract watermark data"
            )
            
        except Exception as e:
            logger.error(f"Extract operation failed: {e}")
            raise
    
    async def _handle_analyze_operation(self, request: WatermarkRequest, watermark_id: str) -> WatermarkResponse:
        """Handles forensic analysis operations"""
        try:
            if not self.forensic_analyzer:
                raise ValueError("Forensic analyzer not available")
            
            # Conduct comprehensive forensic analysis
            forensic_evidence = await self.forensic_analyzer.conduct_comprehensive_analysis(
                request.content_data,
                request.content_type.value,
                request.owner_id,
                request.metadata.get('reference_watermark')
            )
            
            return WatermarkResponse(
                success=True,
                operation=request.operation,
                content_type=request.content_type,
                watermark_id=watermark_id,
                processing_time=0.0,
                confidence=forensic_evidence.confidence_score,
                forensic_evidence=asdict(forensic_evidence),
                watermark_info={
                    'forensic_analysis': True,
                    'evidence_strength': forensic_evidence.evidence_strength.value,
                    'evidence_id': forensic_evidence.evidence_id
                }
            )
            
        except Exception as e:
            logger.error(f"Analyze operation failed: {e}")
            raise
    
    # Content-specific helper methods
    
    async def _embed_image_watermark(
        self,
        engine: ImageWatermarkEngine,
        content_data: bytes,
        watermark_data: bytes,
        strength: str,
        method: str
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Embeds watermark in image content"""
        try:
            # Convert bytes to numpy array
            import numpy as np
            from PIL import Image
            
            image = Image.open(io.BytesIO(content_data))
            image_array = np.array(image)
            
            # Choose embedding method
            if method == "auto" or method == "dct":
                watermarked_array, embed_info = await engine.embed_dct_watermark(
                    image_array, watermark_data, strength
                )
            elif method == "dwt":
                watermarked_array, embed_info = await engine.embed_dwt_watermark(
                    image_array, watermark_data, strength
                )
            else:  # lsb
                watermarked_array, embed_info = await engine.embed_lsb_watermark(
                    image_array, watermark_data, strength
                )
            
            # Convert back to bytes
            watermarked_image = Image.fromarray(watermarked_array)
            output_buffer = io.BytesIO()
            watermarked_image.save(output_buffer, format=image.format or 'PNG')
            output_data = output_buffer.getvalue()
            
            return output_data, embed_info
            
        except Exception as e:
            logger.error(f"Image watermark embedding failed: {e}")
            raise
    
    async def _embed_video_watermark(
        self,
        engine: VideoWatermarkEngine,
        content_data: bytes,
        watermark_data: bytes,
        strength: str,
        method: str
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Embeds watermark in video content"""
        try:
            # Save content to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_input:
                temp_input.write(content_data)
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            # Choose embedding method
            if method == "auto" or method == "frame":
                embed_info = await engine.embed_frame_watermark(
                    temp_input_path, watermark_data, temp_output_path, strength
                )
            elif method == "temporal":
                embed_info = await engine.embed_temporal_watermark(
                    temp_input_path, watermark_data, temp_output_path, strength
                )
            else:  # invisible
                embed_info = await engine.embed_invisible_watermark(
                    temp_input_path, watermark_data, temp_output_path, strength
                )
            
            # Read output
            with open(temp_output_path, 'rb') as f:
                output_data = f.read()
            
            # Cleanup
            Path(temp_input_path).unlink(missing_ok=True)
            Path(temp_output_path).unlink(missing_ok=True)
            
            return output_data, embed_info
            
        except Exception as e:
            logger.error(f"Video watermark embedding failed: {e}")
            raise
    
    async def _embed_text_watermark(
        self,
        engine: TextWatermarkEngine,
        content_data: bytes,
        watermark_data: bytes,
        strength: str,
        method: str
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Embeds watermark in text content"""
        try:
            text_content = content_data.decode('utf-8')
            
            # Choose embedding method
            if method == "auto" or method == "semantic":
                watermarked_text, embed_info = await engine.embed_semantic_watermark(
                    text_content, watermark_data, strength
                )
            elif method == "linguistic":
                watermarked_text, embed_info = await engine.embed_linguistic_watermark(
                    text_content, watermark_data, strength
                )
            else:  # invisible
                watermarked_text, embed_info = await engine.embed_invisible_text_watermark(
                    text_content, watermark_data, strength
                )
            
            output_data = watermarked_text.encode('utf-8')
            
            return output_data, embed_info
            
        except Exception as e:
            logger.error(f"Text watermark embedding failed: {e}")
            raise
    
    # Detection helper methods
    
    async def _detect_image_watermark(
        self,
        engine: ImageWatermarkEngine,
        content_data: bytes,
        method: str
    ) -> Dict[str, Any]:
        """Detects watermark in image content"""
        try:
            # Implementation would detect watermark using various methods
            return {
                'watermark_detected': False,
                'confidence': 0.0,
                'method': method,
                'message': 'Image watermark detection not fully implemented'
            }
            
        except Exception as e:
            logger.error(f"Image watermark detection failed: {e}")
            return {'watermark_detected': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _detect_video_watermark(
        self,
        engine: VideoWatermarkEngine,
        content_data: bytes,
        method: str
    ) -> Dict[str, Any]:
        """Detects watermark in video content"""
        try:
            # Save content to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(content_data)
                temp_path = temp_file.name
            
            # Detect watermark
            detection_result = await engine.detect_video_watermark(temp_path, method)
            
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Video watermark detection failed: {e}")
            return {'watermark_detected': False, 'confidence': 0.0, 'error': str(e)}
    
    async def _detect_text_watermark(
        self,
        engine: TextWatermarkEngine,
        content_data: bytes,
        method: str
    ) -> Dict[str, Any]:
        """Detects watermark in text content"""
        try:
            text_content = content_data.decode('utf-8')
            
            # Detect watermark
            detection_result = await engine.detect_text_watermark(
                text_content, detection_method=method
            )
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Text watermark detection failed: {e}")
            return {'watermark_detected': False, 'confidence': 0.0, 'error': str(e)}
    
    # Utility methods
    
    async def _validate_request(self, request: WatermarkRequest) -> Dict[str, Any]:
        """Validates watermark request"""
        try:
            # Check content data
            if not request.content_data:
                return {'valid': False, 'error': 'Content data is required'}
            
            # Check content type support
            if request.content_type not in self.engines:
                return {'valid': False, 'error': f'Content type {request.content_type} not supported'}
            
            # Operation-specific validation
            if request.operation == WatermarkOperation.EMBED:
                if not request.owner_id:
                    return {'valid': False, 'error': 'Owner ID is required for embedding'}
            
            if request.operation in [WatermarkOperation.VERIFY, WatermarkOperation.ANALYZE]:
                if not request.owner_id:
                    return {'valid': False, 'error': 'Owner ID is required for verification/analysis'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    async def _log_operation(self, request: WatermarkRequest, response: WatermarkResponse, processing_time: float):
        """
Logs watermark operation"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': request.operation.value,
                'content_type': request.content_type.value,
                'watermark_id': response.watermark_id,
                'success': response.success,
                'processing_time': processing_time,
                'confidence': response.confidence,
                'owner_id': request.owner_id,
                'method': request.method,
                'strength': request.strength
            }
            
            logger.info(f"Watermark operation completed: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Operation logging failed: {e}")
    
    def get_operation_statistics(self) -> Dict[str, Any]:
        """Returns operation statistics"""
        try:
            processing_times = self.operation_stats['processing_times']
            
            stats = {
                'total_operations': self.operation_stats['total_operations'],
                'successful_operations': self.operation_stats['successful_operations'],
                'failed_operations': self.operation_stats['failed_operations'],
                'success_rate': 0.0,
                'average_processing_time': 0.0,
                'min_processing_time': 0.0,
                'max_processing_time': 0.0
            }
            
            if stats['total_operations'] > 0:
                stats['success_rate'] = stats['successful_operations'] / stats['total_operations']
            
            if processing_times:
                stats['average_processing_time'] = sum(processing_times) / len(processing_times)
                stats['min_processing_time'] = min(processing_times)
                stats['max_processing_time'] = max(processing_times)
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {}
    
    def detect_content_type(self, content_data: bytes, filename: str = "") -> ContentType:
        """Automatically detects content type from data and filename"""
        try:
            # Check file extension
            if filename:
                ext = Path(filename).suffix.lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                    return ContentType.IMAGE
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']:
                    return ContentType.VIDEO
                elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
                    return ContentType.AUDIO
                elif ext in ['.txt', '.md', '.html', '.xml', '.json']:
                    return ContentType.TEXT
                elif ext in ['.pdf', '.doc', '.docx', '.odt']:
                    return ContentType.DOCUMENT
            
            # Check magic bytes
            if content_data[:8] == b'\x89PNG\r\n\x1a\n':
                return ContentType.IMAGE
            elif content_data[:3] == b'\xff\xd8\xff':
                return ContentType.IMAGE
            elif content_data[:4] == b'RIFF' and content_data[8:12] == b'WAVE':
                return ContentType.AUDIO
            elif content_data[:4] in [b'ftyp', b'moov'] or b'ftyp' in content_data[:32]:
                return ContentType.VIDEO
            
            # Try to decode as text
            try:
                content_data.decode('utf-8')
                return ContentType.TEXT
            except:
                pass
            
            return ContentType.UNKNOWN
            
        except Exception as e:
            logger.error(f"Content type detection failed: {e}")
            return ContentType.UNKNOWN
