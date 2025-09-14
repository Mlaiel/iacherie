"""🛡️ IP Protection Service - Unified Service Interface
====================================================

Complete IP Protection Service module providing unified access to:
- Invisible watermarking for all content formats
- Blockchain rights certification and timestamping
- Smart contracts for automatic royalty distribution
- Revenue tracking and legal compliance

Business Logic Flow:
User Upload → AI Analysis → Invisible Watermarking → Blockchain Registration → 
Smart Contract Creation → Revenue Distribution → Compliance Monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + Legal Tech + DevOps + DBA  
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL IP PROTECTION SYSTEM - NATIONAL SECURITY WARNING ⚠️
================================================================
This IP protection system contains classified technologies:
- Advanced Steganography: Revolutionary Invisible Watermarking
- Blockchain Legal Framework: Patent Pending Technology
- Smart Contract Automation: Proprietary Financial Innovation
- Revenue Distribution Logic: Trade Secret Implementation

UNAUTHORIZED ACCESS VIOLATES FEDERAL LAWS:
- Digital Millennium Copyright Act (DMCA) Violations
- Computer Fraud and Abuse Act (CFAA) Violations  
- Economic Espionage Act (EEA) Violations
- Maximum Penalties: $20M fines + Life imprisonment
- Asset Seizure: All intellectual property and financial assets

Contact mlaiel@live.de for MANDATORY IP protection licensing authorization.
All system activities are monitored and legally recorded for evidence.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
from pathlib import Path
import json

from pydantic import BaseModel, Field

# Import all protection services
from ..watermarking import (
    WatermarkingService, WatermarkType, WatermarkStrength, WatermarkData,
    WatermarkResult, WatermarkDetectionResult, get_watermarking_service
)
from ..blockchain import (
    BlockchainService, BlockchainNetwork, CertificationType,
    ContentHash, OwnershipRecord, BlockchainCertificate,
    get_blockchain_service
)
from .royalty_contracts import (
    RoyaltyDistributionEngine, RoyaltyContract, RoyaltyShare, RoyaltyType,
    PaymentStatus, DistributionMethod, get_royalty_distribution_engine
)

logger = logging.getLogger(__name__)


class ProtectionLevel(Enum):
    """IP protection levels available"""
    
    BASIC = "basic"           # Watermarking only
    STANDARD = "standard"     # Watermarking + blockchain registration
    PREMIUM = "premium"       # Standard + royalty automation
    ENTERPRISE = "enterprise" # Premium + advanced monitoring + legal


class ContentFormat(Enum):
    """Supported content formats for protection"""
    
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"


class ProtectionStatus(Enum):
    """Overall protection status"""
    
    UNPROTECTED = "unprotected"
    PROCESSING = "processing"
    WATERMARKED = "watermarked"
    BLOCKCHAIN_REGISTERED = "blockchain_registered"
    FULLY_PROTECTED = "fully_protected"
    FAILED = "failed"


@dataclass
class IPProtectionRequest:
    """Request for IP protection services"""
    
    content_id: str
    content_path: str
    owner_info: Dict[str, Any]
    protection_level: ProtectionLevel
    
    # Watermarking options
    watermark_strength: WatermarkStrength = WatermarkStrength.MEDIUM
    watermark_types: Optional[List[WatermarkType]] = None
    
    # Blockchain options
    blockchain_networks: Optional[List[BlockchainNetwork]] = None
    certification_types: Optional[List[CertificationType]] = None
    
    # Royalty options
    collaborators: Optional[List[Dict[str, Any]]] = None
    platform_fee_percentage: Decimal = Decimal('2.5')
    auto_distribution: bool = True
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IPProtectionResult:
    """Result of IP protection process"""
    
    request_id: str
    content_id: str
    protection_status: ProtectionStatus
    
    # Watermarking results
    watermark_results: List[WatermarkResult] = field(default_factory=list)
    watermark_ids: List[str] = field(default_factory=list)
    
    # Blockchain results  
    certificate_ids: List[str] = field(default_factory=list)
    blockchain_certificates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Royalty results
    royalty_contract_id: Optional[str] = None
    smart_contract_address: Optional[str] = None
    
    # Processing info
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def is_successful(self) -> bool:
        """Check if protection was successful"""
        return self.protection_status in [
            ProtectionStatus.WATERMARKED,
            ProtectionStatus.BLOCKCHAIN_REGISTERED, 
            ProtectionStatus.FULLY_PROTECTED
        ] and len(self.errors) == 0


class IPProtectionService:
    """Unified IP Protection Service orchestrating all protection components"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Service components
        self.watermarking_service: Optional[WatermarkingService] = None
        self.blockchain_service: Optional[BlockchainService] = None  
        self.royalty_engine: Optional[RoyaltyDistributionEngine] = None
        
        # Protection tracking
        self.active_protections: Dict[str, IPProtectionResult] = {}
        self.protection_history: List[IPProtectionResult] = []
        
        # Service status
        self.initialized = False
        self.running = False
        
        # Default configurations
        self.default_watermark_types = {
            ContentFormat.AUDIO: [WatermarkType.AUDIO_SPECTRAL, WatermarkType.AUDIO_LSB],
            ContentFormat.VIDEO: [WatermarkType.VIDEO_FRAME, WatermarkType.VIDEO_TEMPORAL],
            ContentFormat.IMAGE: [WatermarkType.IMAGE_DCT, WatermarkType.IMAGE_LSB],
            ContentFormat.TEXT: [WatermarkType.TEXT_SEMANTIC, WatermarkType.TEXT_LINGUISTIC],
        }
        
        logger.info("IPProtectionService initialized")
    
    async def initialize(self) -> bool:
        """Initialize all protection service components"""
        
        try:
            logger.info("Initializing IP Protection Service components...")
            
            # Initialize watermarking service
            watermark_config = self.config.get('watermarking', {})
            self.watermarking_service = WatermarkingService(watermark_config)
            if not await self.watermarking_service.initialize():
                raise RuntimeError("Failed to initialize watermarking service")
            
            # Initialize blockchain service
            blockchain_config = self.config.get('blockchain', {})
            self.blockchain_service = BlockchainService(blockchain_config)
            if not await self.blockchain_service.initialize():
                raise RuntimeError("Failed to initialize blockchain service")
            
            # Initialize royalty distribution engine
            royalty_config = self.config.get('royalty', {})
            self.royalty_engine = RoyaltyDistributionEngine(royalty_config)
            
            # Start background monitoring
            asyncio.create_task(self._protection_monitor())
            
            self.initialized = True
            self.running = True
            
            logger.info("IP Protection Service fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize IP Protection Service: {e}")
            return False
    
    async def protect_content(self, request: IPProtectionRequest) -> IPProtectionResult:
        """Apply comprehensive IP protection to content"""
        
        start_time = datetime.utcnow()
        request_id = f"protection_{request.content_id}_{int(start_time.timestamp())}"
        
        result = IPProtectionResult(
            request_id=request_id,
            content_id=request.content_id,
            protection_status=ProtectionStatus.PROCESSING
        )
        
        try:
            if not self.initialized:
                raise RuntimeError("IP Protection Service not initialized")
            
            # Validate content exists
            if not Path(request.content_path).exists():
                raise FileNotFoundError(f"Content file not found: {request.content_path}")
            
            # Detect content format
            content_format = self._detect_content_format(request.content_path)
            logger.info(f"Processing {content_format.value} content: {request.content_id}")
            
            # Track active protection
            self.active_protections[request_id] = result
            
            # Step 1: Apply watermarking
            if request.protection_level in [
                ProtectionLevel.BASIC, ProtectionLevel.STANDARD, 
                ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE
            ]:
                await self._apply_watermarking(request, result, content_format)
            
            # Step 2: Blockchain registration  
            if request.protection_level in [
                ProtectionLevel.STANDARD, ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE
            ]:
                await self._register_on_blockchain(request, result)
            
            # Step 3: Smart contract royalty setup
            if request.protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                await self._setup_royalty_contracts(request, result)
            
            # Step 4: Advanced monitoring (Enterprise only)
            if request.protection_level == ProtectionLevel.ENTERPRISE:
                await self._setup_advanced_monitoring(request, result)
            
            # Finalize protection
            result.completed_at = datetime.utcnow()
            result.processing_time = (result.completed_at - start_time).total_seconds()
            
            # Set final status
            if len(result.errors) == 0:
                if result.royalty_contract_id:
                    result.protection_status = ProtectionStatus.FULLY_PROTECTED
                elif result.certificate_ids:
                    result.protection_status = ProtectionStatus.BLOCKCHAIN_REGISTERED
                elif result.watermark_ids:
                    result.protection_status = ProtectionStatus.WATERMARKED
                else:
                    result.protection_status = ProtectionStatus.FAILED
                    result.errors.append("No protection measures applied successfully")
            else:
                result.protection_status = ProtectionStatus.FAILED
            
            # Store in history
            self.protection_history.append(result)
            
            logger.info(f"Content protection completed: {request_id} - Status: {result.protection_status.value}")
            return result
            
        except Exception as e:
            result.protection_status = ProtectionStatus.FAILED
            result.errors.append(f"Protection failed: {str(e)}")
            result.completed_at = datetime.utcnow()
            result.processing_time = (result.completed_at - start_time).total_seconds()
            
            logger.error(f"Content protection failed: {request_id} - {e}")
            return result
        
        finally:
            # Clean up tracking
            if request_id in self.active_protections:
                del self.active_protections[request_id]
    
    async def _apply_watermarking(
        self, 
        request -> None: IPProtectionRequest, 
        result -> None: IPProtectionResult,
        content_format -> None: ContentFormat
    ) -> None:
        """Apply watermarking to content"""
        
        try:
            # Determine watermark types to apply
            watermark_types = request.watermark_types
            if not watermark_types:
                watermark_types = self.default_watermark_types.get(content_format, [])
            
            if not watermark_types:
                result.warnings.append(f"No watermark types configured for {content_format.value}")
                return
            
            # Create watermark data
            watermark_data = WatermarkData(
                owner_id=request.owner_info['id'],
                content_id=request.content_id,
                creation_timestamp=datetime.utcnow(),
                license_info=request.owner_info.get('license_info', 'All rights reserved'),
                tracking_id=f"track_{request.content_id}",
                metadata={
                    'protection_level': request.protection_level.value,
                    'content_format': content_format.value,
                    **request.metadata
                }
            )
            
            # Apply each watermark type
            for watermark_type in watermark_types:
                try:
                    watermark_result = await self.watermarking_service.embed_watermark(
                        content_path=request.content_path,
                        watermark_data=watermark_data,
                        watermark_type=watermark_type,
                        strength=request.watermark_strength
                    )
                    
                    if watermark_result.success:
                        result.watermark_results.append(watermark_result)
                        result.watermark_ids.append(watermark_result.watermark_id)
                        logger.info(f"Watermark applied: {watermark_type.value} to {request.content_id}")
                    else:
                        result.warnings.append(f"Watermark failed: {watermark_type.value} - {watermark_result.error_message}")
                        
                except Exception as e:
                    result.warnings.append(f"Watermark error for {watermark_type.value}: {str(e)}")
            
            if not result.watermark_ids:
                result.errors.append("No watermarks applied successfully")
            
        except Exception as e:
            result.errors.append(f"Watermarking process failed: {str(e)}")
    
    async def _register_on_blockchain(self, request -> None: IPProtectionRequest, result -> None: IPProtectionResult) -> None:
        """Register content on blockchain for rights certification"""
        
        try:
            # Use watermarked content if available, otherwise original
            content_path = request.content_path
            if result.watermark_results:
                # Use the first successfully watermarked file
                watermarked_result = next(
                    (wr for wr in result.watermark_results if wr.success and wr.output_path),
                    None
                )
                if watermarked_result:
                    content_path = watermarked_result.output_path
            
            # Determine certification types
            cert_types = request.certification_types or [
                CertificationType.COPYRIGHT_REGISTRATION,
                CertificationType.TIMESTAMP_PROOF
            ]
            
            # Determine blockchain networks  
            networks = request.blockchain_networks or [BlockchainNetwork.ETHEREUM]
            
            # Register on each network and certification type
            for network in networks:
                for cert_type in cert_types:
                    try:
                        certificate_id = await self.blockchain_service.register_content_ownership(
                            content_id=request.content_id,
                            content_path=content_path,
                            owner_info=request.owner_info,
                            certification_type=cert_type,
                            network=network
                        )
                        
                        if certificate_id:
                            result.certificate_ids.append(certificate_id)
                            
                            # Get certificate details
                            certificate = await self.blockchain_service.get_certificate(certificate_id)
                            if certificate:
                                result.blockchain_certificates.append(certificate)
                            
                            logger.info(f"Blockchain registration: {cert_type.value} on {network.value}")
                        
                    except Exception as e:
                        result.warnings.append(f"Blockchain registration failed for {cert_type.value} on {network.value}: {str(e)}")
            
            if not result.certificate_ids:
                result.errors.append("No blockchain registrations completed successfully")
            
        except Exception as e:
            result.errors.append(f"Blockchain registration process failed: {str(e)}")
    
    async def _setup_royalty_contracts(self, request -> None: IPProtectionRequest, result -> None: IPProtectionResult) -> None:
        """Setup smart contracts for automatic royalty distribution"""
        
        try:
            if not request.collaborators:
                # Single creator scenario
                creators = [{
                    'wallet_address': request.owner_info.get('wallet_address', request.owner_info.get('address')),
                    'name': request.owner_info.get('name', 'Content Creator'),
                    'percentage': 100.0,
                    'role': 'creator'
                }]
            else:
                # Multi-collaborator scenario
                creators = []
                total_percentage = Decimal('0')
                
                for collaborator in request.collaborators:
                    percentage = Decimal(str(collaborator.get('percentage', 0)))
                    creators.append({
                        'wallet_address': collaborator['wallet_address'],
                        'name': collaborator.get('name', 'Collaborator'),
                        'percentage': float(percentage),
                        'role': collaborator.get('role', 'collaborator'),
                        'minimum_payment': collaborator.get('minimum_payment', 0.01)
                    })
                    total_percentage += percentage
                
                # Validate percentages
                if abs(total_percentage - 100) > Decimal('0.01'):
                    result.errors.append(f"Collaborator percentages sum to {total_percentage}%, must equal 100%")
                    return
            
            # Create royalty distribution contract
            contract_id = await self.royalty_engine.create_royalty_contract(
                content_id=request.content_id,
                creators=creators,
                platform_fee_percentage=request.platform_fee_percentage,
                network='ethereum'  # Default to Ethereum
            )
            
            if contract_id:
                result.royalty_contract_id = contract_id
                
                # Get contract details for smart contract address
                contract = self.royalty_engine.active_contracts.get(contract_id)
                if contract:
                    result.smart_contract_address = contract.contract_address
                
                logger.info(f"Royalty contract created: {contract_id} for content {request.content_id}")
            else:
                result.errors.append("Failed to create royalty distribution contract")
            
        except Exception as e:
            result.errors.append(f"Royalty contract setup failed: {str(e)}")
    
    async def _setup_advanced_monitoring(self, request -> None: IPProtectionRequest, result -> None: IPProtectionResult) -> None:
        """Setup advanced monitoring for enterprise-level protection"""
        
        try:
            # Advanced monitoring features for enterprise customers
            monitoring_config = {
                'content_id': request.content_id,
                'protection_level': 'enterprise',
                'real_time_alerts': True,
                'legal_automation': True,
                'revenue_tracking': True,
                'compliance_monitoring': True,
                'threat_intelligence': True
            }
            
            # This would integrate with monitoring services
            # For now, just log the configuration
            logger.info(f"Advanced monitoring configured for content {request.content_id}")
            
            result.metadata['monitoring_config'] = monitoring_config
            
        except Exception as e:
            result.warnings.append(f"Advanced monitoring setup warning: {str(e)}")
    
    async def verify_content_protection(self, content_id: str, content_path: str) -> Dict[str, Any]:
        """Verify all protection measures for content"""
        
        try:
            verification_result = {
                'content_id': content_id,
                'watermark_detection': {},
                'blockchain_verification': {},
                'royalty_contract_status': {},
                'overall_protection_score': 0.0,
                'verified_at': datetime.utcnow().isoformat()
            }
            
            protection_score = 0.0
            max_score = 0.0
            
            # Find protection record
            protection_record = next(
                (p for p in self.protection_history if p.content_id == content_id),
                None
            )
            
            if not protection_record:
                verification_result['error'] = "No protection record found for content"
                return verification_result
            
            # Verify watermarks
            if protection_record.watermark_ids:
                max_score += 30.0
                watermark_detections = []
                
                for i, watermark_id in enumerate(protection_record.watermark_ids):
                    if i < len(protection_record.watermark_results):
                        watermark_result = protection_record.watermark_results[i]
                        
                        try:
                            detection_result = await self.watermarking_service.detect_watermark(
                                content_path=content_path,
                                watermark_type=watermark_result.watermark_type,
                                expected_data_length=64
                            )
                            
                            watermark_detections.append({
                                'watermark_id': watermark_id,
                                'watermark_type': watermark_result.watermark_type.value,
                                'detected': detection_result.detected,
                                'confidence': detection_result.confidence
                            })
                            
                            if detection_result.detected and detection_result.confidence > 0.7:
                                protection_score += 10.0
                                
                        except Exception as e:
                            watermark_detections.append({
                                'watermark_id': watermark_id,
                                'error': str(e)
                            })
                
                verification_result['watermark_detection'] = {
                    'total_watermarks': len(protection_record.watermark_ids),
                    'detections': watermark_detections
                }
            
            # Verify blockchain registrations
            if protection_record.certificate_ids:
                max_score += 40.0
                blockchain_verifications = []
                
                for certificate_id in protection_record.certificate_ids:
                    try:
                        authenticity_result = await self.blockchain_service.verify_content_authenticity(
                            content_id=content_id,
                            content_path=content_path
                        )
                        
                        blockchain_verifications.append({
                            'certificate_id': certificate_id,
                            'authentic': authenticity_result.get('authentic', False),
                            'verification_results': authenticity_result.get('verification_results', [])
                        })
                        
                        if authenticity_result.get('authentic', False):
                            protection_score += 20.0
                            
                    except Exception as e:
                        blockchain_verifications.append({
                            'certificate_id': certificate_id,
                            'error': str(e)
                        })
                
                verification_result['blockchain_verification'] = {
                    'total_certificates': len(protection_record.certificate_ids),
                    'verifications': blockchain_verifications
                }
            
            # Verify royalty contract
            if protection_record.royalty_contract_id:
                max_score += 30.0
                
                try:
                    contract_analytics = await self.royalty_engine.get_contract_analytics(
                        protection_record.royalty_contract_id
                    )
                    
                    verification_result['royalty_contract_status'] = {
                        'contract_id': protection_record.royalty_contract_id,
                        'contract_active': contract_analytics['contract_info']['is_active'],
                        'total_distributed': contract_analytics['financial_summary']['total_distributed'],
                        'distribution_count': contract_analytics['financial_summary']['distribution_count']
                    }
                    
                    if contract_analytics['contract_info']['is_active']:
                        protection_score += 30.0
                        
                except Exception as e:
                    verification_result['royalty_contract_status'] = {
                        'contract_id': protection_record.royalty_contract_id,
                        'error': str(e)
                    }
            
            # Calculate overall protection score
            if max_score > 0:
                verification_result['overall_protection_score'] = (protection_score / max_score) * 100.0
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Content protection verification failed: {e}")
            return {
                'content_id': content_id,
                'error': f"Verification failed: {str(e)}",
                'verified_at': datetime.utcnow().isoformat()
            }
    
    async def distribute_revenue(
        self, 
        content_id: str, 
        revenue_amount: Decimal, 
        royalty_type: RoyaltyType = RoyaltyType.STREAMING_ROYALTY,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Distribute revenue for protected content"""
        
        try:
            # Find protection record with royalty contract
            protection_record = next(
                (p for p in self.protection_history 
                 if p.content_id == content_id and p.royalty_contract_id),
                None
            )
            
            if not protection_record:
                raise ValueError(f"No royalty contract found for content {content_id}")
            
            # Execute distribution
            distribution_result = await self.royalty_engine.distribute_royalties(
                contract_id=protection_record.royalty_contract_id,
                revenue_amount=revenue_amount,
                royalty_type=royalty_type,
                metadata=metadata
            )
            
            logger.info(f"Revenue distributed for content {content_id}: {revenue_amount}")
            return distribution_result
            
        except Exception as e:
            logger.error(f"Revenue distribution failed for content {content_id}: {e}")
            raise
    
    async def get_protection_status(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive protection status for content"""
        
        protection_record = next(
            (p for p in self.protection_history if p.content_id == content_id),
            None
        )
        
        if not protection_record:
            return None
        
        return {
            'content_id': content_id,
            'protection_status': protection_record.protection_status.value,
            'protection_level': protection_record.request_id.split('_')[1] if '_' in protection_record.request_id else 'unknown',
            'watermarks_applied': len(protection_record.watermark_ids),
            'blockchain_certificates': len(protection_record.certificate_ids),
            'royalty_contract_active': protection_record.royalty_contract_id is not None,
            'processing_time': protection_record.processing_time,
            'created_at': protection_record.created_at.isoformat(),
            'completed_at': protection_record.completed_at.isoformat() if protection_record.completed_at else None,
            'errors': protection_record.errors,
            'warnings': protection_record.warnings
        }
    
    async def get_analytics_summary(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Get comprehensive analytics for IP protection service"""
        
        try:
            # Filter protection history by date range
            history = self.protection_history
            if date_range:
                start_date, end_date = date_range
                history = [
                    p for p in history 
                    if start_date <= p.created_at <= end_date
                ]
            
            # Calculate statistics
            total_protections = len(history)
            successful_protections = len([p for p in history if p.is_successful()])
            failed_protections = len([p for p in history if p.protection_status == ProtectionStatus.FAILED])
            
            # Protection level breakdown
            protection_levels = {}
            for level in ProtectionLevel:
                protection_levels[level.value] = len([
                    p for p in history 
                    if level.value in p.request_id.lower()
                ])
            
            # Content format breakdown
            content_formats = {}
            watermark_stats = {
                'total_watermarks': sum(len(p.watermark_ids) for p in history),
                'success_rate': 0.0
            }
            
            # Blockchain statistics
            blockchain_stats = {
                'total_certificates': sum(len(p.certificate_ids) for p in history),
                'networks_used': set()
            }
            
            # Royalty statistics
            royalty_stats = {
                'contracts_created': len([p for p in history if p.royalty_contract_id]),
                'total_revenue_distributed': 0.0
            }
            
            # Calculate success rates
            success_rate = (successful_protections / total_protections * 100) if total_protections > 0 else 0
            if watermark_stats['total_watermarks'] > 0:
                successful_watermarks = sum(
                    len([wr for wr in p.watermark_results if wr.success]) 
                    for p in history
                )
                watermark_stats['success_rate'] = (successful_watermarks / watermark_stats['total_watermarks'] * 100)
            
            # Average processing time
            avg_processing_time = 0.0
            if history:
                total_time = sum(p.processing_time for p in history if p.processing_time > 0)
                valid_times = len([p for p in history if p.processing_time > 0])
                avg_processing_time = total_time / valid_times if valid_times > 0 else 0
            
            analytics = {
                'period': {
                    'start': date_range[0].isoformat() if date_range else 'all_time',
                    'end': date_range[1].isoformat() if date_range else 'all_time'
                },
                'overview': {
                    'total_protections': total_protections,
                    'successful_protections': successful_protections,
                    'failed_protections': failed_protections,
                    'success_rate_percentage': round(success_rate, 2),
                    'average_processing_time_seconds': round(avg_processing_time, 2)
                },
                'protection_levels': protection_levels,
                'watermarking': watermark_stats,
                'blockchain': blockchain_stats,
                'royalties': royalty_stats,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate analytics summary: {e}")
            return {}
    
    def _detect_content_format(self, content_path: str) -> ContentFormat:
        """Detect content format from file extension"""
        
        file_path = Path(content_path)
        suffix = file_path.suffix.lower()
        
        audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma'}
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'}
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
        text_extensions = {'.txt', '.md', '.rtf'}
        document_extensions = {'.pdf', '.doc', '.docx', '.html', '.xml'}
        
        if suffix in audio_extensions:
            return ContentFormat.AUDIO
        elif suffix in video_extensions:
            return ContentFormat.VIDEO
        elif suffix in image_extensions:
            return ContentFormat.IMAGE
        elif suffix in text_extensions:
            return ContentFormat.TEXT
        elif suffix in document_extensions:
            return ContentFormat.DOCUMENT
        else:
            return ContentFormat.MULTIMEDIA  # Default fallback
    
    async def _protection_monitor(self) -> None:
        """Background task to monitor protection status"""
        
        while self.running:
            try:
                # Monitor active protections
                current_time = datetime.utcnow()
                
                for request_id, result in list(self.active_protections.items()):
                    # Check for timeouts (15 minutes max)
                    if (current_time - result.created_at).total_seconds() > 900:
                        result.protection_status = ProtectionStatus.FAILED
                        result.errors.append("Protection process timed out")
                        result.completed_at = current_time
                        
                        # Move to history
                        self.protection_history.append(result)
                        del self.active_protections[request_id]
                        
                        logger.warning(f"Protection process timed out: {request_id}")
                
                # Monitor blockchain transactions
                # (This would check for transaction confirmations in production)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Protection monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def shutdown(self) -> None:
        """Gracefully shutdown IP protection service"""
        
        try:
            logger.info("Shutting down IP Protection Service...")
            self.running = False
            
            # Shutdown component services
            if self.watermarking_service:
                await self.watermarking_service.shutdown()
            
            if self.blockchain_service:
                await self.blockchain_service.shutdown()
            
            # Save any pending data
            logger.info("IP Protection Service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during IP protection service shutdown: {e}")


# Service singleton
ip_protection_service = IPProtectionService()


async def get_ip_protection_service() -> IPProtectionService:
    """Get the IP protection service instance"""
    return ip_protection_service


# Convenience functions for easy access

async def protect_content_quick(
    content_id: str,
    content_path: str,
    owner_info: Dict[str, Any],
    protection_level: ProtectionLevel = ProtectionLevel.STANDARD
) -> IPProtectionResult:
    """Quick content protection with default settings"""
    
    service = await get_ip_protection_service()
    if not service.initialized:
        await service.initialize()
    
    request = IPProtectionRequest(
        content_id=content_id,
        content_path=content_path,
        owner_info=owner_info,
        protection_level=protection_level
    )
    
    return await service.protect_content(request)


async def verify_content_quick(content_id: str, content_path: str) -> Dict[str, Any]:
    """Quick content protection verification"""
    
    service = await get_ip_protection_service()
    return await service.verify_content_protection(content_id, content_path)


__all__ = [
    # Main service
    'IPProtectionService',
    'get_ip_protection_service',
    
    # Data models
    'IPProtectionRequest',
    'IPProtectionResult', 
    'ProtectionLevel',
    'ContentFormat',
    'ProtectionStatus',
    
    # Convenience functions
    'protect_content_quick',
    'verify_content_quick',
    
    # Re-export from submodules
    'WatermarkingService',
    'BlockchainService', 
    'RoyaltyDistributionEngine',
    'WatermarkType',
    'WatermarkStrength',
    'BlockchainNetwork',
    'CertificationType',
    'RoyaltyType'
]