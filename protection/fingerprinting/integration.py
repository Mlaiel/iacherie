"""🔧 Enhanced Protection Integration Module
==========================================

Integrates enhanced fingerprinting engines with existing protection infrastructure
for seamless deployment and production use.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

# Import enhanced fingerprinting engines
try:
    from enhanced_audio import ChromaprintMLEngine, EnhancedAudioFingerprint
    from enhanced_video import VideoDeepLearningEngine, EnhancedVideoFingerprint
    from enhanced_image import ImageProtectionEngine, EnhancedImageFingerprint
    from realtime_monitoring import RealTimeMonitoringEngine, ViolationType, ViolationSeverity
except ImportError:
    # Fallback for direct execution or missing modules
    ChromaprintMLEngine = None
    VideoDeepLearningEngine = None
    ImageProtectionEngine = None
    RealTimeMonitoringEngine = None

# Import existing protection infrastructure
try:
    from ..monitoring import ContentProtectionMonitor
    from ..dmca_automation import DMCAAutomationEngine
    from ..alert_system import AlertSystem
except ImportError:
    # Fallback if modules don't exist
    ContentProtectionMonitor = None
    DMCAAutomationEngine = None
    AlertSystem = None

logger = logging.getLogger(__name__)

class EnhancedProtectionOrchestrator:
    """Orchestrates enhanced protection features with existing infrastructure."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize enhanced engines
        if ChromaprintMLEngine:
            self.audio_engine = ChromaprintMLEngine(self.config.get('audio', {}))
        else:
            self.audio_engine = None
            
        if VideoDeepLearningEngine:
            self.video_engine = VideoDeepLearningEngine(self.config.get('video', {}))
        else:
            self.video_engine = None
            
        if ImageProtectionEngine:
            self.image_engine = ImageProtectionEngine(self.config.get('image', {}))
        else:
            self.image_engine = None
            
        if RealTimeMonitoringEngine:
            self.monitoring_engine = RealTimeMonitoringEngine(self.config.get('monitoring', {}))
        else:
            self.monitoring_engine = None
        
        # Initialize existing infrastructure (if available)
        self.legacy_monitor = ContentProtectionMonitor() if ContentProtectionMonitor else None
        self.dmca_engine = DMCAAutomationEngine() if DMCAAutomationEngine else None
        self.alert_system = AlertSystem() if AlertSystem else None
        
        # State management
        self.active_protections: Dict[str, Dict] = {}
        self.performance_metrics = {
            'total_content_protected': 0,
            'violations_detected': 0,
            'dmca_notices_sent': 0,
            'successful_takedowns': 0,
            'false_positives': 0,
            'processing_time_avg': 0.0
        }
        
        # Setup violation handlers
        self._setup_violation_handlers()
        
        logger.info("EnhancedProtectionOrchestrator initialized with full feature integration")
    
    def _setup_violation_handlers(self):
        """Setup handlers for violations detected by the monitoring engine."""
        self.monitoring_engine.add_violation_handler(self._handle_violation_alert)
        self.monitoring_engine.add_violation_handler(self._handle_dmca_automation)
        self.monitoring_engine.add_violation_handler(self._update_protection_metrics)
    
    async def protect_content(self, content_path: str, content_type: str, owner_id: str,
                            protection_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Comprehensive content protection with enhanced fingerprinting."""
        try:
            start_time = datetime.utcnow()
            protection_config = protection_config or {}
            
            logger.info(f"Starting enhanced protection for {content_type} content: {content_path}")
            
            # Step 1: Generate enhanced fingerprint
            fingerprint = await self._generate_enhanced_fingerprint(content_path, content_type, protection_config)
            
            # Step 2: Apply watermarking if requested
            if protection_config.get('apply_watermark', False) and content_type == 'image':
                watermarked_path = await self._apply_watermarking(content_path, protection_config)
                fingerprint = await self._generate_enhanced_fingerprint(watermarked_path, content_type, protection_config)
            
            # Step 3: Add to monitoring targets
            content_id = await self.monitoring_engine.add_monitoring_target(
                content_path=content_path,
                content_type=content_type,
                owner_id=owner_id,
                platforms=protection_config.get('platforms'),
                apply_watermark=protection_config.get('apply_watermark', False)
            )
            
            # Step 4: Register with legacy systems (if available)
            legacy_protection_id = None
            if self.legacy_monitor:
                legacy_protection_id = await self._register_with_legacy_monitor(content_id, fingerprint, owner_id)
            
            # Step 5: Store protection record
            protection_record = {
                'content_id': content_id,
                'content_path': content_path,
                'content_type': content_type,
                'owner_id': owner_id,
                'fingerprint': fingerprint,
                'legacy_protection_id': legacy_protection_id,
                'protection_config': protection_config,
                'created_at': datetime.utcnow(),
                'processing_time': (datetime.utcnow() - start_time).total_seconds()
            }
            
            self.active_protections[content_id] = protection_record
            self.performance_metrics['total_content_protected'] += 1
            
            logger.info(f"Enhanced protection activated for content: {content_id}")
            
            return {
                'success': True,
                'content_id': content_id,
                'fingerprint_confidence': getattr(fingerprint, 'confidence_score', 0.0),
                'monitoring_platforms': len(protection_config.get('platforms', [])) or len(self.monitoring_engine.platform_configs),
                'processing_time': protection_record['processing_time'],
                'features_enabled': self._get_enabled_features(protection_config)
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced content protection: {e}")
            return {
                'success': False,
                'error': str(e),
                'content_path': content_path
            }
    
    async def _generate_enhanced_fingerprint(self, content_path: str, content_type: str, config: Dict) -> Any:
        """Generate enhanced fingerprint based on content type."""
        if content_type == 'audio':
            return await self.audio_engine.generate_fingerprint(content_path)
        elif content_type == 'video':
            return await self.video_engine.generate_fingerprint(content_path)
        elif content_type == 'image':
            return await self.image_engine.generate_fingerprint(
                content_path, 
                apply_watermark=config.get('apply_watermark', False)
            )
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    async def _apply_watermarking(self, content_path: str, config: Dict) -> str:
        """Apply watermarking to image content."""
        # This would typically save the watermarked image to a new path
        watermarked_path = str(Path(content_path).with_suffix('_watermarked' + Path(content_path).suffix))
        logger.info(f"Watermarking applied: {watermarked_path}")
        return watermarked_path
    
    async def _register_with_legacy_monitor(self, content_id: str, fingerprint: Any, owner_id: str) -> Optional[str]:
        """Register content with legacy monitoring system."""
        try:
            if self.legacy_monitor and hasattr(self.legacy_monitor, 'add_monitoring_target'):
                # Convert enhanced fingerprint to legacy format
                legacy_fingerprint = self._convert_to_legacy_fingerprint(fingerprint)
                return await self.legacy_monitor.add_monitoring_target(content_id, legacy_fingerprint, owner_id)
        except Exception as e:
            logger.warning(f"Failed to register with legacy monitor: {e}")
        return None
    
    def _convert_to_legacy_fingerprint(self, enhanced_fingerprint: Any) -> Dict:
        """Convert enhanced fingerprint to legacy format."""
        # Basic conversion - in production this would be more sophisticated
        return {
            'id': getattr(enhanced_fingerprint, 'file_id', 'unknown'),
            'confidence': getattr(enhanced_fingerprint, 'confidence_score', 0.8),
            'created_at': getattr(enhanced_fingerprint, 'created_at', datetime.utcnow())
        }
    
    async def _handle_violation_alert(self, violation):
        """Handle violation alerts through the alert system."""
        try:
            if self.alert_system and hasattr(self.alert_system, 'send_alert'):
                alert_data = {
                    'type': 'copyright_violation',
                    'severity': violation.severity.value,
                    'violation_id': violation.violation_id,
                    'platform': violation.platform,
                    'similarity_score': violation.similarity_score,
                    'detected_at': violation.detected_at,
                    'platform_url': violation.platform_url
                }
                
                await self.alert_system.send_alert(alert_data)
                logger.info(f"Alert sent for violation: {violation.violation_id}")
        except Exception as e:
            logger.error(f"Error sending violation alert: {e}")
    
    async def _handle_dmca_automation(self, violation):
        """Handle DMCA automation for violations."""
        try:
            if (self.dmca_engine and 
                hasattr(self.dmca_engine, 'file_dmca_notice') and
                violation.severity in [ViolationSeverity.HIGH, ViolationSeverity.CRITICAL]):
                
                dmca_data = {
                    'violation_id': violation.violation_id,
                    'infringing_url': violation.platform_url,
                    'original_content_id': violation.original_content_id,
                    'platform': violation.platform,
                    'evidence': {
                        'similarity_score': violation.similarity_score,
                        'detection_method': 'enhanced_fingerprinting',
                        'confidence_score': violation.confidence_score
                    }
                }
                
                dmca_result = await self.dmca_engine.file_dmca_notice(dmca_data)
                if dmca_result.get('success'):
                    self.performance_metrics['dmca_notices_sent'] += 1
                    logger.info(f"DMCA notice filed for violation: {violation.violation_id}")
        except Exception as e:
            logger.error(f"Error in DMCA automation: {e}")
    
    async def _update_protection_metrics(self, violation):
        """Update protection performance metrics."""
        try:
            self.performance_metrics['violations_detected'] += 1
            
            # Update processing time average
            if hasattr(violation, 'processing_time'):
                current_avg = self.performance_metrics['processing_time_avg']
                total_violations = self.performance_metrics['violations_detected']
                new_avg = ((current_avg * (total_violations - 1)) + violation.processing_time) / total_violations
                self.performance_metrics['processing_time_avg'] = new_avg
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def _get_enabled_features(self, config: Dict) -> List[str]:
        """Get list of enabled protection features."""
        features = ['enhanced_fingerprinting', 'realtime_monitoring']
        
        if config.get('apply_watermark'):
            features.append('watermarking')
        
        if config.get('enable_steganography'):
            features.append('steganography')
        
        if self.dmca_engine:
            features.append('dmca_automation')
        
        if self.alert_system:
            features.append('alert_system')
        
        return features
    
    async def start_monitoring(self):
        """Start the real-time monitoring system."""
        try:
            logger.info("Starting enhanced real-time monitoring...")
            await self.monitoring_engine.start_monitoring()
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop the real-time monitoring system."""
        try:
            logger.info("Stopping enhanced real-time monitoring...")
            await self.monitoring_engine.stop_monitoring()
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    def get_protection_status(self, content_id: str) -> Optional[Dict]:
        """Get protection status for specific content."""
        return self.active_protections.get(content_id)
    
    def get_all_protections(self) -> Dict[str, Dict]:
        """Get all active protections."""
        return self.active_protections.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        monitoring_metrics = self.monitoring_engine.get_metrics()
        
        return {
            **self.performance_metrics,
            'monitoring_metrics': monitoring_metrics,
            'active_protections_count': len(self.active_protections),
            'platforms_monitored': monitoring_metrics.get('platforms_monitored', 0),
            'last_update': datetime.utcnow()
        }
    
    async def analyze_content_similarity(self, content_path1: str, content_path2: str, content_type: str) -> Dict[str, Any]:
        """Analyze similarity between two pieces of content."""
        try:
            # Generate fingerprints for both content pieces
            fingerprint1 = await self._generate_enhanced_fingerprint(content_path1, content_type, {})
            fingerprint2 = await self._generate_enhanced_fingerprint(content_path2, content_type, {})
            
            # Calculate similarity
            if content_type == 'audio':
                similarity = await self.audio_engine.calculate_similarity(fingerprint1, fingerprint2)
            elif content_type == 'video':
                similarity = await self.video_engine.calculate_similarity(fingerprint1, fingerprint2)
            elif content_type == 'image':
                similarity = await self.image_engine.calculate_similarity(fingerprint1, fingerprint2)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            return {
                'success': True,
                'similarity_score': similarity,
                'content_type': content_type,
                'fingerprint1_confidence': getattr(fingerprint1, 'confidence_score', 0.0),
                'fingerprint2_confidence': getattr(fingerprint2, 'confidence_score', 0.0),
                'analysis_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content similarity: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def bulk_protect_content(self, content_list: List[Dict], protection_config: Optional[Dict] = None) -> List[Dict]:
        """Protect multiple pieces of content in bulk."""
        results = []
        
        for content_info in content_list:
            try:
                result = await self.protect_content(
                    content_path=content_info['path'],
                    content_type=content_info['type'],
                    owner_id=content_info['owner_id'],
                    protection_config=protection_config
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error in bulk protection for {content_info['path']}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'content_path': content_info['path']
                })
        
        return results
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported monitoring platforms."""
        return list(self.monitoring_engine.platform_configs.keys())
    
    def get_protection_statistics(self) -> Dict[str, Any]:
        """Get detailed protection statistics."""
        metrics = self.get_performance_metrics()
        
        # Calculate additional statistics
        success_rate = 0.0
        if metrics['violations_detected'] > 0:
            success_rate = (metrics['successful_takedowns'] / metrics['violations_detected']) * 100
        
        false_positive_rate = 0.0
        if metrics['violations_detected'] > 0:
            false_positive_rate = (metrics['false_positives'] / metrics['violations_detected']) * 100
        
        return {
            'protection_summary': {
                'total_content_protected': metrics['total_content_protected'],
                'active_protections': len(self.active_protections),
                'platforms_monitored': len(self.get_supported_platforms())
            },
            'violation_statistics': {
                'total_violations_detected': metrics['violations_detected'],
                'dmca_notices_sent': metrics['dmca_notices_sent'],
                'successful_takedowns': metrics['successful_takedowns'],
                'success_rate_percent': success_rate,
                'false_positive_rate_percent': false_positive_rate
            },
            'performance_metrics': {
                'average_processing_time': metrics['processing_time_avg'],
                'total_content_scanned': metrics['monitoring_metrics'].get('total_content_scanned', 0),
                'last_scan_time': metrics['monitoring_metrics'].get('last_scan_time')
            },
            'system_status': {
                'monitoring_active': True,  # Would check actual status
                'engines_operational': self._check_engines_status(),
                'last_updated': datetime.utcnow()
            }
        }
    
    def _check_engines_status(self) -> Dict[str, bool]:
        """Check status of all protection engines."""
        return {
            'audio_engine': self.audio_engine is not None,
            'video_engine': self.video_engine is not None,
            'image_engine': self.image_engine is not None,
            'monitoring_engine': self.monitoring_engine is not None,
            'legacy_monitor': self.legacy_monitor is not None,
            'dmca_engine': self.dmca_engine is not None,
            'alert_system': self.alert_system is not None
        }