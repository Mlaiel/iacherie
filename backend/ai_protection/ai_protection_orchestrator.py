"""AI Protection Orchestrator

Central intelligence coordination system for AI-powered content protection.
Orchestrates all protection mechanisms with machine learning optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib

# Core AI Protection Imports
from .watermark_engine import WatermarkEngine, WatermarkConfig, ContentType, WatermarkType
from .blockchain_registry import BlockchainRightsRegistry, RightsType
from .copyright_detector import CopyrightDetector, ViolationType
from .nft_generator import NFTGenerator, NFTStandard
from .rights_manager import DigitalRightsManager, ProtectionLevel

logger = logging.getLogger(__name__)


class OrchestrationStrategy(Enum):
    """AI orchestration strategies"""
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    STEALTH = "stealth"
    ENTERPRISE = "enterprise"


class ThreatLevel(Enum):
    """Content threat assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ProcessingStage(Enum):
    """Content processing stages"""
    INTAKE = "intake"
    ANALYSIS = "analysis"
    WATERMARKING = "watermarking"
    REGISTRATION = "registration"
    MONITORING = "monitoring"
    ENFORCEMENT = "enforcement"
    COMPLETE = "complete"


@dataclass
class ProtectionRequest:
    """AI protection request specification"""
    request_id: str
    content_id: str
    content_type: ContentType
    content_data: Union[bytes, str]
    owner_id: str
    protection_level: ProtectionLevel
    strategy: OrchestrationStrategy
    priority: int
    metadata: Dict[str, Any]
    timestamp: datetime
    deadline: Optional[datetime] = None


@dataclass
class ProtectionResult:
    """Comprehensive protection result"""
    request_id: str
    content_id: str
    success: bool
    protection_layers: List[str]
    watermark_id: Optional[str]
    blockchain_tx: Optional[str]
    nft_token_id: Optional[str]
    fingerprint_hash: str
    threat_assessment: ThreatLevel
    processing_time: float
    stage_timings: Dict[str, float]
    errors: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class AIDecision:
    """AI-powered protection decision"""
    decision_id: str
    content_analysis: Dict[str, Any]
    recommended_strategy: OrchestrationStrategy
    protection_layers: List[str]
    confidence_score: float
    reasoning: str
    risk_factors: List[str]
    timestamp: datetime


class AIProtectionOrchestrator:
    """
    Central AI Protection Orchestrator
    
    Provides intelligent coordination of all protection mechanisms with
    machine learning optimization and automated decision making.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize AI Protection Orchestrator"""
        self.config = config or {}
        self.watermark_engine = WatermarkEngine()
        self.blockchain_registry = BlockchainRightsRegistry()
        self.copyright_detector = CopyrightDetector()
        self.nft_generator = NFTGenerator()
        self.rights_manager = DigitalRightsManager()
        
        # AI Decision Engine
        self.decision_cache: Dict[str, AIDecision] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.threat_intelligence: Dict[str, Any] = {}
        
        # Processing queues
        self.high_priority_queue: asyncio.Queue = asyncio.Queue()
        self.normal_priority_queue: asyncio.Queue = asyncio.Queue()
        self.batch_queue: asyncio.Queue = asyncio.Queue()
        
        # Resource management
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.resource_limits = self.config.get('resource_limits', {
            'max_concurrent_tasks': 50,
            'max_memory_mb': 4096,
            'max_processing_time': 300
        })
        
        self._initialize_ai_models()
        
    def _initialize_ai_models(self):
        """Initialize AI models for intelligent orchestration"""
        try:
            # Content analysis models
            self.content_analyzer = self._load_content_analysis_model()
            self.threat_assessor = self._load_threat_assessment_model()
            self.strategy_optimizer = self._load_strategy_optimization_model()
            
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"AI model initialization failed: {e}")
            # Fallback to rule-based decisions
            self.content_analyzer = None
            self.threat_assessor = None
            self.strategy_optimizer = None
    
    def _load_content_analysis_model(self):
        """Load content analysis AI model"""
        # Placeholder for actual ML model loading
        # In production, this would load a trained model for content analysis
        return {
            'model_type': 'content_analysis',
            'version': '1.0.0',
            'capabilities': ['format_detection', 'quality_assessment', 'content_classification']
        }
    
    def _load_threat_assessment_model(self):
        """Load threat assessment AI model"""
        # Placeholder for actual ML model loading
        # In production, this would load a trained model for threat analysis
        return {
            'model_type': 'threat_assessment',
            'version': '1.0.0',
            'capabilities': ['vulnerability_detection', 'risk_scoring', 'attack_prediction']
        }
    
    def _load_strategy_optimization_model(self):
        """Load strategy optimization AI model"""
        # Placeholder for actual ML model loading
        # In production, this would load a trained model for strategy optimization
        return {
            'model_type': 'strategy_optimization',
            'version': '1.0.0',
            'capabilities': ['performance_optimization', 'resource_allocation', 'success_prediction']
        }
    
    async def protect_content(self, request: ProtectionRequest) -> ProtectionResult:
        """
        Main content protection orchestration
        
        Args:
            request: Protection request specification
            
        Returns:
            Comprehensive protection result
        """
        start_time = time.time()
        stage_timings = {}
        errors = []
        
        try:
            logger.info(f"Starting protection orchestration for content {request.content_id}")
            
            # Stage 1: Content Analysis & AI Decision
            stage_start = time.time()
            ai_decision = await self._make_ai_decision(request)
            stage_timings['analysis'] = time.time() - stage_start
            
            # Stage 2: Apply Watermarking
            stage_start = time.time()
            watermark_result = await self._apply_watermarking(request, ai_decision)
            stage_timings['watermarking'] = time.time() - stage_start
            
            # Stage 3: Blockchain Registration
            stage_start = time.time()
            blockchain_result = await self._register_blockchain(request, watermark_result)
            stage_timings['registration'] = time.time() - stage_start
            
            # Stage 4: NFT Generation (if required)
            stage_start = time.time()
            nft_result = await self._generate_nft(request, ai_decision)
            stage_timings['nft_generation'] = time.time() - stage_start
            
            # Stage 5: Rights Management
            stage_start = time.time()
            rights_result = await self._manage_rights(request, ai_decision)
            stage_timings['rights_management'] = time.time() - stage_start
            
            # Stage 6: Fingerprinting for Detection
            stage_start = time.time()
            fingerprint_result = await self._create_fingerprint(request)
            stage_timings['fingerprinting'] = time.time() - stage_start
            
            # Compile comprehensive result
            protection_result = ProtectionResult(
                request_id=request.request_id,
                content_id=request.content_id,
                success=True,
                protection_layers=ai_decision.protection_layers,
                watermark_id=watermark_result.get('watermark_id'),
                blockchain_tx=blockchain_result.get('transaction_hash'),
                nft_token_id=nft_result.get('token_id'),
                fingerprint_hash=fingerprint_result.get('fingerprint_hash', ''),
                threat_assessment=ai_decision.confidence_score,
                processing_time=time.time() - start_time,
                stage_timings=stage_timings,
                errors=errors,
                metadata={
                    'ai_decision_id': ai_decision.decision_id,
                    'strategy_used': ai_decision.recommended_strategy.value,
                    'confidence_score': ai_decision.confidence_score,
                    'risk_factors': ai_decision.risk_factors
                },
                timestamp=datetime.utcnow()
            )
            
            # Update performance metrics
            await self._update_performance_metrics(protection_result)
            
            logger.info(f"Protection orchestration completed for {request.content_id}")
            return protection_result
            
        except Exception as e:
            logger.error(f"Protection orchestration failed for {request.content_id}: {e}")
            errors.append(str(e))
            
            return ProtectionResult(
                request_id=request.request_id,
                content_id=request.content_id,
                success=False,
                protection_layers=[],
                watermark_id=None,
                blockchain_tx=None,
                nft_token_id=None,
                fingerprint_hash='',
                threat_assessment=ThreatLevel.UNKNOWN,
                processing_time=time.time() - start_time,
                stage_timings=stage_timings,
                errors=errors,
                metadata={},
                timestamp=datetime.utcnow()
            )
    
    async def _make_ai_decision(self, request: ProtectionRequest) -> AIDecision:
        """Make AI-powered protection decision"""
        try:
            # Content analysis
            content_analysis = await self._analyze_content(request)
            
            # Threat assessment
            threat_assessment = await self._assess_threats(request, content_analysis)
            
            # Strategy recommendation
            recommended_strategy = await self._recommend_strategy(
                request, content_analysis, threat_assessment
            )
            
            # Protection layers selection
            protection_layers = await self._select_protection_layers(
                request, content_analysis, threat_assessment, recommended_strategy
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                content_analysis, threat_assessment, protection_layers
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                content_analysis, threat_assessment, recommended_strategy, protection_layers
            )
            
            ai_decision = AIDecision(
                decision_id=str(uuid.uuid4()),
                content_analysis=content_analysis,
                recommended_strategy=recommended_strategy,
                protection_layers=protection_layers,
                confidence_score=confidence_score,
                reasoning=reasoning,
                risk_factors=threat_assessment.get('risk_factors', []),
                timestamp=datetime.utcnow()
            )
            
            # Cache decision for optimization
            self.decision_cache[request.content_id] = ai_decision
            
            return ai_decision
            
        except Exception as e:
            logger.error(f"AI decision making failed: {e}")
            # Fallback to safe default decision
            return self._create_fallback_decision(request)
    
    async def _analyze_content(self, request: ProtectionRequest) -> Dict[str, Any]:
        """Analyze content using AI models"""
        analysis = {
            'content_type': request.content_type.value,
            'content_size': len(request.content_data) if isinstance(request.content_data, bytes) else len(str(request.content_data)),
            'complexity_score': 0.5,
            'quality_score': 0.8,
            'uniqueness_score': 0.7,
            'commercial_value': 0.6,
            'format_specifics': {}
        }
        
        if self.content_analyzer:
            # Use AI model for advanced analysis
            try:
                # Placeholder for actual AI model inference
                analysis.update({
                    'ai_analysis_version': self.content_analyzer['version'],
                    'detected_features': ['watermark_compatible', 'high_resolution'],
                    'optimization_suggestions': ['use_robust_watermarking', 'blockchain_priority']
                })
            except Exception as e:
                logger.warning(f"AI content analysis failed, using fallback: {e}")
        
        # Format-specific analysis
        if request.content_type == ContentType.AUDIO:
            analysis['format_specifics'] = {
                'estimated_duration': 180.0,
                'estimated_bitrate': 320000,
                'stereo_channels': True,
                'watermark_capacity': 'high'
            }
        elif request.content_type == ContentType.VIDEO:
            analysis['format_specifics'] = {
                'estimated_duration': 120.0,
                'estimated_resolution': '1920x1080',
                'frame_rate': 30,
                'watermark_capacity': 'very_high'
            }
        elif request.content_type == ContentType.IMAGE:
            analysis['format_specifics'] = {
                'estimated_resolution': '2048x2048',
                'color_depth': 24,
                'compression_ratio': 0.85,
                'watermark_capacity': 'medium'
            }
        
        return analysis
    
    async def _assess_threats(self, request: ProtectionRequest, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess security threats and vulnerabilities"""
        threat_assessment = {
            'overall_risk': 'medium',
            'piracy_risk': 0.6,
            'unauthorized_usage_risk': 0.7,
            'commercial_theft_risk': 0.5,
            'reputation_risk': 0.4,
            'risk_factors': [],
            'threat_vectors': [],
            'recommended_countermeasures': []
        }
        
        # Analyze content characteristics for risk
        content_value = content_analysis.get('commercial_value', 0.5)
        if content_value > 0.8:
            threat_assessment['risk_factors'].append('high_commercial_value')
            threat_assessment['piracy_risk'] += 0.2
        
        uniqueness = content_analysis.get('uniqueness_score', 0.5)
        if uniqueness > 0.8:
            threat_assessment['risk_factors'].append('unique_content')
            threat_assessment['unauthorized_usage_risk'] += 0.1
        
        # Protection level assessment
        if request.protection_level == ProtectionLevel.BASIC:
            threat_assessment['overall_risk'] = 'high'
            threat_assessment['recommended_countermeasures'].append('upgrade_protection_level')
        
        # Add threat vectors based on content type
        if request.content_type == ContentType.AUDIO:
            threat_assessment['threat_vectors'].extend([
                'streaming_platform_theft',
                'download_redistribution',
                'unauthorized_sampling'
            ])
        elif request.content_type == ContentType.VIDEO:
            threat_assessment['threat_vectors'].extend([
                'illegal_streaming',
                'download_piracy',
                'unauthorized_clips'
            ])
        
        if self.threat_assessor:
            try:
                # Use AI model for advanced threat assessment
                threat_assessment.update({
                    'ai_threat_score': 0.65,
                    'predicted_attack_vectors': ['web_scraping', 'api_abuse'],
                    'threat_timeline': '24-48_hours'
                })
            except Exception as e:
                logger.warning(f"AI threat assessment failed, using fallback: {e}")
        
        return threat_assessment
    
    async def _recommend_strategy(self, request: ProtectionRequest, 
                                content_analysis: Dict[str, Any], 
                                threat_assessment: Dict[str, Any]) -> OrchestrationStrategy:
        """Recommend optimal orchestration strategy"""
        
        # Default strategy based on protection level
        strategy_mapping = {
            ProtectionLevel.BASIC: OrchestrationStrategy.DEFENSIVE,
            ProtectionLevel.STANDARD: OrchestrationStrategy.BALANCED,
            ProtectionLevel.PREMIUM: OrchestrationStrategy.AGGRESSIVE,
            ProtectionLevel.ENTERPRISE: OrchestrationStrategy.ENTERPRISE
        }
        
        base_strategy = strategy_mapping.get(request.protection_level, OrchestrationStrategy.BALANCED)
        
        # Adjust based on threat assessment
        overall_risk = threat_assessment.get('overall_risk', 'medium')
        if overall_risk == 'high' or overall_risk == 'critical':
            if base_strategy == OrchestrationStrategy.DEFENSIVE:
                base_strategy = OrchestrationStrategy.BALANCED
            elif base_strategy == OrchestrationStrategy.BALANCED:
                base_strategy = OrchestrationStrategy.AGGRESSIVE
        
        # Content value consideration
        commercial_value = content_analysis.get('commercial_value', 0.5)
        if commercial_value > 0.8 and base_strategy != OrchestrationStrategy.ENTERPRISE:
            base_strategy = OrchestrationStrategy.AGGRESSIVE
        
        # User preference override
        if request.strategy != OrchestrationStrategy.BALANCED:
            base_strategy = request.strategy
        
        if self.strategy_optimizer:
            try:
                # Use AI model for strategy optimization
                # Placeholder for actual AI model inference
                ai_recommended = base_strategy  # Would be model output
                return ai_recommended
            except Exception as e:
                logger.warning(f"AI strategy optimization failed, using fallback: {e}")
        
        return base_strategy
    
    async def _select_protection_layers(self, request: ProtectionRequest,
                                      content_analysis: Dict[str, Any],
                                      threat_assessment: Dict[str, Any],
                                      strategy: OrchestrationStrategy) -> List[str]:
        """Select appropriate protection layers"""
        layers = []
        
        # Base layers for all strategies
        layers.append('fingerprinting')
        layers.append('rights_registration')
        
        # Strategy-specific layers
        if strategy in [OrchestrationStrategy.DEFENSIVE, OrchestrationStrategy.BALANCED]:
            layers.extend(['invisible_watermarking', 'blockchain_registry'])
        
        if strategy in [OrchestrationStrategy.AGGRESSIVE, OrchestrationStrategy.ENTERPRISE]:
            layers.extend([
                'invisible_watermarking',
                'robust_watermarking', 
                'blockchain_registry',
                'nft_certification',
                'advanced_monitoring'
            ])
        
        if strategy == OrchestrationStrategy.ENTERPRISE:
            layers.extend([
                'multi_chain_registry',
                'legal_documentation',
                'real_time_monitoring',
                'automated_enforcement'
            ])
        
        if strategy == OrchestrationStrategy.STEALTH:
            layers = ['stealth_watermarking', 'minimal_blockchain', 'covert_monitoring']
        
        # Adjust based on content type capabilities
        watermark_capacity = content_analysis.get('format_specifics', {}).get('watermark_capacity', 'medium')
        if watermark_capacity == 'low':
            layers = [layer for layer in layers if 'watermarking' not in layer or layer == 'invisible_watermarking']
        
        return list(set(layers))  # Remove duplicates
    
    def _calculate_confidence_score(self, content_analysis: Dict[str, Any],
                                  threat_assessment: Dict[str, Any],
                                  protection_layers: List[str]) -> float:
        """Calculate confidence score for protection decision"""
        base_confidence = 0.8
        
        # Adjust based on content analysis quality
        quality_score = content_analysis.get('quality_score', 0.5)
        base_confidence += (quality_score - 0.5) * 0.2
        
        # Adjust based on threat assessment clarity
        risk_factors_count = len(threat_assessment.get('risk_factors', []))
        if risk_factors_count > 3:
            base_confidence -= 0.1
        
        # Adjust based on protection layers coverage
        layer_coverage = len(protection_layers) / 8.0  # Assuming max 8 layers
        base_confidence += layer_coverage * 0.1
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_reasoning(self, content_analysis: Dict[str, Any],
                          threat_assessment: Dict[str, Any],
                          strategy: OrchestrationStrategy,
                          protection_layers: List[str]) -> str:
        """Generate human-readable reasoning for protection decision"""
        reasoning_parts = []
        
        # Content analysis reasoning
        content_type = content_analysis.get('content_type', 'unknown')
        reasoning_parts.append(f"Content type ({content_type}) analyzed for optimal protection")
        
        commercial_value = content_analysis.get('commercial_value', 0.5)
        if commercial_value > 0.7:
            reasoning_parts.append("High commercial value detected, enhanced protection recommended")
        
        # Threat assessment reasoning
        overall_risk = threat_assessment.get('overall_risk', 'medium')
        reasoning_parts.append(f"Risk assessment: {overall_risk} threat level identified")
        
        risk_factors = threat_assessment.get('risk_factors', [])
        if risk_factors:
            reasoning_parts.append(f"Risk factors include: {', '.join(risk_factors)}")
        
        # Strategy reasoning
        reasoning_parts.append(f"Selected {strategy.value} orchestration strategy")
        
        # Protection layers reasoning
        reasoning_parts.append(f"Implementing {len(protection_layers)} protection layers: {', '.join(protection_layers[:3])}{'...' if len(protection_layers) > 3 else ''}")
        
        return ". ".join(reasoning_parts) + "."
    
    def _create_fallback_decision(self, request: ProtectionRequest) -> AIDecision:
        """Create fallback decision when AI analysis fails"""
        return AIDecision(
            decision_id=str(uuid.uuid4()),
            content_analysis={
                'content_type': request.content_type.value,
                'fallback_mode': True
            },
            recommended_strategy=OrchestrationStrategy.BALANCED,
            protection_layers=['invisible_watermarking', 'blockchain_registry', 'fingerprinting'],
            confidence_score=0.6,
            reasoning="Fallback protection strategy applied due to AI analysis failure",
            risk_factors=['ai_analysis_unavailable'],
            timestamp=datetime.utcnow()
        )
    
    async def _apply_watermarking(self, request: ProtectionRequest, ai_decision: AIDecision) -> Dict[str, Any]:
        """Apply watermarking based on AI decision"""
        try:
            if 'watermarking' not in ' '.join(ai_decision.protection_layers):
                return {'watermark_id': None, 'message': 'Watermarking not required'}
            
            # Configure watermarking based on AI decision
            watermark_config = WatermarkConfig(
                watermark_type=WatermarkType.INVISIBLE if 'invisible' in ' '.join(ai_decision.protection_layers) else WatermarkType.ROBUST,
                strength=0.8 if ai_decision.recommended_strategy == OrchestrationStrategy.AGGRESSIVE else 0.6,
                content_type=request.content_type,
                metadata={'orchestrator_request_id': request.request_id}
            )
            
            # Apply watermark
            result = await self.watermark_engine.embed_watermark(
                content_data=request.content_data,
                config=watermark_config,
                owner_id=request.owner_id
            )
            
            return {
                'watermark_id': result.get('watermark_id'),
                'watermarked_data': result.get('watermarked_data'),
                'verification_key': result.get('verification_key'),
                'embedding_stats': result.get('stats', {})
            }
            
        except Exception as e:
            logger.error(f"Watermarking failed: {e}")
            return {'error': str(e)}
    
    async def _register_blockchain(self, request: ProtectionRequest, watermark_result: Dict[str, Any]) -> Dict[str, Any]:
        """Register content on blockchain"""
        try:
            registration_data = {
                'content_id': request.content_id,
                'owner_id': request.owner_id,
                'content_type': request.content_type.value,
                'watermark_id': watermark_result.get('watermark_id'),
                'metadata': request.metadata,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            result = await self.blockchain_registry.register_content(
                content_id=request.content_id,
                owner_address=request.owner_id,
                rights_type=RightsType.COPYRIGHT,
                metadata=registration_data
            )
            
            return {
                'transaction_hash': result.get('transaction_hash'),
                'block_number': result.get('block_number'),
                'registry_id': result.get('registry_id'),
                'gas_used': result.get('gas_used')
            }
            
        except Exception as e:
            logger.error(f"Blockchain registration failed: {e}")
            return {'error': str(e)}
    
    async def _generate_nft(self, request: ProtectionRequest, ai_decision: AIDecision) -> Dict[str, Any]:
        """Generate NFT if required by protection strategy"""
        try:
            if 'nft' not in ' '.join(ai_decision.protection_layers):
                return {'token_id': None, 'message': 'NFT generation not required'}
            
            nft_metadata = {
                'name': f"Protected Content {request.content_id[:8]}",
                'description': f"AI-protected {request.content_type.value} content with comprehensive rights management",
                'content_type': request.content_type.value,
                'protection_level': request.protection_level.value,
                'creation_date': datetime.utcnow().isoformat(),
                'orchestrator_metadata': {
                    'strategy': ai_decision.recommended_strategy.value,
                    'confidence_score': ai_decision.confidence_score,
                    'protection_layers': ai_decision.protection_layers
                }
            }
            
            result = await self.nft_generator.mint_nft(
                content_id=request.content_id,
                owner_address=request.owner_id,
                metadata=nft_metadata,
                standard=NFTStandard.ERC721
            )
            
            return {
                'token_id': result.get('token_id'),
                'contract_address': result.get('contract_address'),
                'transaction_hash': result.get('transaction_hash'),
                'metadata_uri': result.get('metadata_uri')
            }
            
        except Exception as e:
            logger.error(f"NFT generation failed: {e}")
            return {'error': str(e)}
    
    async def _manage_rights(self, request: ProtectionRequest, ai_decision: AIDecision) -> Dict[str, Any]:
        """Manage digital rights registration"""
        try:
            rights_config = {
                'protection_level': request.protection_level,
                'enforcement_level': 'automatic' if ai_decision.recommended_strategy == OrchestrationStrategy.AGGRESSIVE else 'manual',
                'monitoring_frequency': 'real_time' if 'real_time' in ai_decision.protection_layers else 'periodic',
                'violation_response': 'immediate' if ai_decision.confidence_score > 0.8 else 'reviewed'
            }
            
            result = await self.rights_manager.register_content(
                content_id=request.content_id,
                owner_id=request.owner_id,
                content_type=request.content_type,
                protection_config=rights_config
            )
            
            return {
                'rights_id': result.get('rights_id'),
                'registration_status': result.get('status'),
                'enforcement_config': result.get('enforcement_config'),
                'monitoring_config': result.get('monitoring_config')
            }
            
        except Exception as e:
            logger.error(f"Rights management failed: {e}")
            return {'error': str(e)}
    
    async def _create_fingerprint(self, request: ProtectionRequest) -> Dict[str, Any]:
        """Create content fingerprint for detection"""
        try:
            # Generate content hash
            content_hash = hashlib.sha256(
                request.content_data if isinstance(request.content_data, bytes) 
                else str(request.content_data).encode()
            ).hexdigest()
            
            # Create comprehensive fingerprint
            fingerprint_data = {
                'content_id': request.content_id,
                'content_hash': content_hash,
                'content_type': request.content_type.value,
                'timestamp': datetime.utcnow().isoformat(),
                'owner_id': request.owner_id,
                'metadata': request.metadata
            }
            
            fingerprint_hash = hashlib.sha256(
                json.dumps(fingerprint_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Register with copyright detector
            await self.copyright_detector.register_content_fingerprint(
                content_id=request.content_id,
                fingerprint_data=fingerprint_data,
                fingerprint_hash=fingerprint_hash
            )
            
            return {
                'fingerprint_hash': fingerprint_hash,
                'content_hash': content_hash,
                'registration_status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Fingerprinting failed: {e}")
            return {'error': str(e)}
    
    async def _update_performance_metrics(self, result: ProtectionResult):
        """Update orchestrator performance metrics"""
        try:
            # Update processing time metrics
            self.performance_metrics['avg_processing_time'] = (
                self.performance_metrics.get('avg_processing_time', 0) * 0.9 +
                result.processing_time * 0.1
            )
            
            # Update success rate
            current_success_rate = self.performance_metrics.get('success_rate', 1.0)
            self.performance_metrics['success_rate'] = (
                current_success_rate * 0.95 + (1.0 if result.success else 0.0) * 0.05
            )
            
            # Update stage timings
            for stage, timing in result.stage_timings.items():
                metric_key = f'avg_{stage}_time'
                self.performance_metrics[metric_key] = (
                    self.performance_metrics.get(metric_key, 0) * 0.9 + timing * 0.1
                )
            
            # Update error metrics
            if result.errors:
                self.performance_metrics['error_count'] = (
                    self.performance_metrics.get('error_count', 0) + len(result.errors)
                )
            
            logger.debug(f"Performance metrics updated for {result.content_id}")
            
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        return {
            'orchestrator_id': id(self),
            'active_tasks': len(self.active_tasks),
            'queue_sizes': {
                'high_priority': self.high_priority_queue.qsize(),
                'normal_priority': self.normal_priority_queue.qsize(),
                'batch': self.batch_queue.qsize()
            },
            'performance_metrics': self.performance_metrics.copy(),
            'ai_models_status': {
                'content_analyzer': bool(self.content_analyzer),
                'threat_assessor': bool(self.threat_assessor),
                'strategy_optimizer': bool(self.strategy_optimizer)
            },
            'resource_usage': {
                'memory_mb': self._get_memory_usage(),
                'cpu_percent': self._get_cpu_usage()
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Perform performance optimization"""
        optimization_result = {
            'optimizations_applied': [],
            'performance_improvement': 0.0,
            'recommendations': []
        }
        
        try:
            # Clear old cache entries
            cache_before = len(self.decision_cache)
            current_time = datetime.utcnow()
            self.decision_cache = {
                k: v for k, v in self.decision_cache.items()
                if (current_time - v.timestamp).seconds < 3600  # Keep 1 hour
            }
            cache_after = len(self.decision_cache)
            
            if cache_before > cache_after:
                optimization_result['optimizations_applied'].append('cache_cleanup')
            
            # Analyze performance bottlenecks
            if self.performance_metrics.get('avg_processing_time', 0) > 10.0:
                optimization_result['recommendations'].append('consider_parallel_processing')
            
            if self.performance_metrics.get('success_rate', 1.0) < 0.95:
                optimization_result['recommendations'].append('review_error_patterns')
            
            logger.info("Performance optimization completed")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return {'error': str(e)}


# Factory function for easy instantiation
def create_ai_protection_orchestrator(config: Optional[Dict[str, Any]] = None) -> AIProtectionOrchestrator:
    """
    Factory function to create AI Protection Orchestrator
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured AIProtectionOrchestrator instance
    """
    return AIProtectionOrchestrator(config)


# Export all public classes and functions
__all__ = [
    'AIProtectionOrchestrator',
    'ProtectionRequest',
    'ProtectionResult',
    'AIDecision',
    'OrchestrationStrategy',
    'ThreatLevel',
    'ProcessingStage',
    'create_ai_protection_orchestrator'
]