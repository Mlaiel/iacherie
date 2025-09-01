"""Watermarking Module Index
Entry point for the IA Influencer Agent watermarking system

Developed by: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Senior Backend + ML Engineer + DBA + Security Expert + 
               Microservices Architect + Audio Engineer + DevOps + AI Prompt Engineer

⚠️ INTELLECTUAL PROPERTY WARNING:
This watermarking system and all associated code are the exclusive intellectual property 
of Fahed Mlaiel. Unauthorized use is strictly prohibited.
"""
from .service_manager import (
    WatermarkServiceManager,
    WatermarkRequest, 
    WatermarkResponse,
    ContentType,
    WatermarkOperation
)
from .blockchain_registry import BlockchainWatermarkRegistry
from .forensic_analyzer import ForensicWatermarkAnalyzer
from .image_engine import ImageWatermarkEngine
from .video_engine import VideoWatermarkEngine
from .text_engine import TextWatermarkEngine

# Import core watermarking classes
from . import (
    WatermarkType,
    WatermarkStrength,
    WatermarkPurpose,
    WatermarkData,
    WatermarkResult,
    WatermarkDetectionResult,
    AudioWatermarker,
    ImageWatermarker,
    TextWatermarker,
    WatermarkingService,
    get_watermarking_service
)

__version__ = "1.0.0"

# Quick access functions for common operations
async def create_watermark_service(config: dict = None) -> WatermarkServiceManager:
    """Creates and initializes a professional watermarking service"""
    manager = WatermarkServiceManager(config or {})
    return manager

async def embed_watermark(
    content_data: bytes,
    content_type: str,
    owner_id: str,
    strength: str = "medium",
    method: str = "auto"
) -> WatermarkResponse:
    """Quick watermark embedding function"""
    manager = await create_watermark_service()
    
    request = WatermarkRequest(
        operation=WatermarkOperation.EMBED,
        content_type=ContentType(content_type),
        content_data=content_data,
        owner_id=owner_id,
        strength=strength,
        method=method
    )
    
    return await manager.process_watermark_request(request)

async def detect_watermark(
    content_data: bytes,
    content_type: str,
    detection_method: str = "auto"
) -> WatermarkResponse:
    """Quick watermark detection function"""
    manager = await create_watermark_service()
    
    request = WatermarkRequest(
        operation=WatermarkOperation.DETECT,
        content_type=ContentType(content_type),
        content_data=content_data,
        method=detection_method
    )
    
    return await manager.process_watermark_request(request)

async def verify_ownership(
    content_data: bytes,
    content_type: str,
    claimed_owner: str
) -> WatermarkResponse:
    """Quick ownership verification function"""
    manager = await create_watermark_service()
    
    request = WatermarkRequest(
        operation=WatermarkOperation.VERIFY,
        content_type=ContentType(content_type),
        content_data=content_data,
        owner_id=claimed_owner
    )
    
    return await manager.process_watermark_request(request)

async def forensic_analysis(
    content_data: bytes,
    content_type: str,
    claimed_owner: str
) -> WatermarkResponse:
    """Quick forensic analysis function"""
    manager = await create_watermark_service()
    
    request = WatermarkRequest(
        operation=WatermarkOperation.ANALYZE,
        content_type=ContentType(content_type),
        content_data=content_data,
        owner_id=claimed_owner
    )
    
    return await manager.process_watermark_request(request)

# Export all public APIs
__all__ = [
    # Core Service Classes
    'WatermarkServiceManager',
    'BlockchainWatermarkRegistry',
    'ForensicWatermarkAnalyzer',
    
    # Engine Classes
    'ImageWatermarkEngine',
    'VideoWatermarkEngine',
    'TextWatermarkEngine',
    'AudioWatermarker',
    'ImageWatermarker',
    'TextWatermarker',
    
    # Data Models
    'WatermarkRequest',
    'WatermarkResponse',
    'WatermarkData',
    'WatermarkResult',
    'WatermarkDetectionResult',
    
    # Enums
    'ContentType',
    'WatermarkOperation',
    'WatermarkType',
    'WatermarkStrength',
    'WatermarkPurpose',
    
    # Legacy Service
    'WatermarkingService',
    'get_watermarking_service',
    
    # Quick Access Functions
    'create_watermark_service',
    'embed_watermark',
    'detect_watermark',
    'verify_ownership',
    'forensic_analysis',
]
