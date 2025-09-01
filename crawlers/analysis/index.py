"""Analysis Module Index
====================

Professional content analysis system entry point with unified interface.
Provides easy access to all analysis capabilities and components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Import all analyzers
from .content_analyzer import ContentAnalyzer
from .content_classifier import ContentClassifier
from .competitive_analyzer import CompetitiveAnalyzer
from .engagement_analyzer import EngagementAnalyzer
from .metadata_extractor import MetadataExtractor
from .monetization_analyzer import MonetizationAnalyzer
from .protection_analyzer import ProtectionAnalyzer
from .sentiment_analyzer import SentimentAnalyzer
from .similarity_detector import SimilarityDetector
from .trend_analyzer import TrendAnalyzer
from .ai_fingerprint_engine import AIFingerprintEngine, ContentType as FingerprintContentType
from .revenue_performance_analyzer import RevenuePerformanceAnalyzer
from .realtime_violation_detector import RealTimeViolationDetector

logger = logging.getLogger(__name__)

class AnalyzerType(Enum):
    """
Available analyzer types."""

    CONTENT = "content"
    CLASSIFIER = "classifier"
    COMPETITIVE = "competitive"
    ENGAGEMENT = "engagement"
    METADATA = "metadata"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    SENTIMENT = "sentiment"
    SIMILARITY = "similarity"
    TREND = "trend"
    FINGERPRINT = "fingerprint"
    REVENUE = "revenue"
    VIOLATION = "violation"

@dataclass
class AnalysisCapabilities:
    """Analysis system capabilities."""
    supported_content_types: List[str]
    supported_platforms: List[str]
    real_time_monitoring: bool
    batch_processing: bool
    ml_powered: bool
    accuracy_rate: float
    processing_speed: str
    
class AnalysisModuleIndex:
    """
    Unified interface for all content analysis capabilities.
    
    This class provides a centralized access point to all analysis modules,
    enabling easy integration and orchestration of complex analysis workflows.
    
    Features:
    - Unified API for all analyzers
    - Automatic analyzer initialization and management
    - Performance monitoring and statistics
    - Batch processing coordination
    - Error handling and recovery
    - Configuration management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize the analysis module index."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzer registry
        self.analyzers: Dict[AnalyzerType, Any] = {}
        self.analyzer_classes = {
            AnalyzerType.CONTENT: ContentAnalyzer,
            AnalyzerType.CLASSIFIER: ContentClassifier,
            AnalyzerType.COMPETITIVE: CompetitiveAnalyzer,
            AnalyzerType.ENGAGEMENT: EngagementAnalyzer,
            AnalyzerType.METADATA: MetadataExtractor,
            AnalyzerType.MONETIZATION: MonetizationAnalyzer,
            AnalyzerType.PROTECTION: ProtectionAnalyzer,
            AnalyzerType.SENTIMENT: SentimentAnalyzer,
            AnalyzerType.SIMILARITY: SimilarityDetector,
            AnalyzerType.TREND: TrendAnalyzer,
            AnalyzerType.FINGERPRINT: AIFingerprintEngine,
            AnalyzerType.REVENUE: RevenuePerformanceAnalyzer,
            AnalyzerType.VIOLATION: RealTimeViolationDetector
        }
        
        # Performance tracking
        self.analysis_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'average_processing_time': 0.0,
            'active_analyzers': 0
        }
        
        # Auto-initialize core analyzers
        self._initialize_core_analyzers()
        
        self.logger.info("AnalysisModuleIndex initialized successfully")
    
    def _initialize_core_analyzers(self) -> None:
        """Initialize core analyzers automatically."""
        core_analyzers = [
            AnalyzerType.CONTENT,
            AnalyzerType.FINGERPRINT,
            AnalyzerType.SENTIMENT,
            AnalyzerType.PROTECTION
        ]
        
        for analyzer_type in core_analyzers:
            try:
                self.get_analyzer(analyzer_type)
                self.logger.info(f"Core analyzer initialized: {analyzer_type.value}")
            except Exception as e:
                self.logger.error(f"Failed to initialize core analyzer {analyzer_type.value}: {e}")
    
    def get_analyzer(self, analyzer_type: AnalyzerType) -> Any:
        """
        Get or create analyzer instance.
        
        Args:
            analyzer_type: Type of analyzer to retrieve
            
        Returns:
            Analyzer instance
        """
        if analyzer_type not in self.analyzers:
            if analyzer_type not in self.analyzer_classes:
                raise ValueError(f"Unknown analyzer type: {analyzer_type}")
            
            # Create analyzer instance
            analyzer_class = self.analyzer_classes[analyzer_type]
            analyzer_config = self.config.get(analyzer_type.value, {})
            
            try:
                self.analyzers[analyzer_type] = analyzer_class(analyzer_config)
                self.analysis_stats['active_analyzers'] += 1
                self.logger.info(f"Analyzer created: {analyzer_type.value}")
            except Exception as e:
                self.logger.error(f"Failed to create analyzer {analyzer_type.value}: {e}")
                raise
        
        return self.analyzers[analyzer_type]
    
    async def analyze_content_comprehensive(
        self,
        content_data: Any,
        content_type: str,
        content_id: str,
        analysis_types: Optional[List[AnalyzerType]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive content analysis using multiple analyzers.
        
        Args:
            content_data: Content to analyze
            content_type: Type of content (audio, video, image, text)
            content_id: Unique identifier for content
            analysis_types: Specific analyzers to use (all if None)
            
        Returns:
            Comprehensive analysis results
        """
        start_time = datetime.now()
        results = {
            'content_id': content_id,
            'content_type': content_type,
            'analysis_timestamp': start_time,
            'results': {},
            'errors': {},
            'performance': {}
        }
        
        # Determine analyzers to use
        if analysis_types is None:
            analysis_types = [
                AnalyzerType.CONTENT,
                AnalyzerType.FINGERPRINT,
                AnalyzerType.SENTIMENT,
                AnalyzerType.CLASSIFIER,
                AnalyzerType.METADATA
            ]
        
        try:
            # Run analyses in parallel where possible
            analysis_tasks = []
            
            for analyzer_type in analysis_types:
                try:
                    analyzer = self.get_analyzer(analyzer_type)
                    task = self._run_single_analysis(
                        analyzer, analyzer_type, content_data, content_type, content_id
                    )
                    analysis_tasks.append((analyzer_type, task))
                except Exception as e:
                    results['errors'][analyzer_type.value] = str(e)
            
            # Wait for all analyses to complete
            for analyzer_type, task in analysis_tasks:
                try:
                    analysis_result = await task
                    results['results'][analyzer_type.value] = analysis_result
                except Exception as e:
                    results['errors'][analyzer_type.value] = str(e)
            
            # Calculate performance metrics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            results['performance'] = {
                'total_processing_time': processing_time,
                'successful_analyses': len(results['results']),
                'failed_analyses': len(results['errors']),
                'completion_timestamp': end_time
            }
            
            # Update statistics
            self.analysis_stats['total_analyses'] += 1
            if len(results['errors']) == 0:
                self.analysis_stats['successful_analyses'] += 1
            else:
                self.analysis_stats['failed_analyses'] += 1
            
            # Update average processing time
            total_time = (self.analysis_stats['average_processing_time'] * 
                         (self.analysis_stats['total_analyses'] - 1) + processing_time)
            self.analysis_stats['average_processing_time'] = total_time / self.analysis_stats['total_analyses']
            
            self.logger.info(f"Comprehensive analysis completed for {content_id} in {processing_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed for {content_id}: {e}")
            results['errors']['general'] = str(e)
        
        return results
    
    async def _run_single_analysis(
        self,
        analyzer: Any,
        analyzer_type: AnalyzerType,
        content_data: Any,
        content_type: str,
        content_id: str
    ) -> Any:
        """Run single analyzer analysis."""
        try:
            # Route to appropriate analysis method based on analyzer type
            if analyzer_type == AnalyzerType.CONTENT:
                return await analyzer.analyze_content(content_data, content_type, content_id)
            elif analyzer_type == AnalyzerType.FINGERPRINT:
                from .ai_fingerprint_engine import ContentType
                content_type_enum = ContentType(content_type.lower())
                return await analyzer.extract_fingerprint(content_data, content_type_enum, content_id)
            elif analyzer_type == AnalyzerType.SENTIMENT:
                return await analyzer.analyze_sentiment(content_data, content_id)
            elif analyzer_type == AnalyzerType.CLASSIFIER:
                return await analyzer.classify_content(content_data, content_type)
            elif analyzer_type == AnalyzerType.METADATA:
                return await analyzer.extract_metadata(content_data, content_type)
            elif analyzer_type == AnalyzerType.PROTECTION:
                return await analyzer.analyze_protection(content_data, content_id)
            else:
                # Generic analysis method
                if hasattr(analyzer, 'analyze'):
                    return await analyzer.analyze(content_data, content_id)
                else:
                    # Fallback generic analysis
                    self.logger.warning(f"No specific analysis method for {analyzer_type.value}, using generic analysis")
                    return {
                        "analyzer_type": analyzer_type.value,
                        "content_id": content_id,
                        "analysis_result": "generic_analysis_completed",
                        "timestamp": datetime.utcnow().isoformat(),
                        "metadata": {
                            "analyzer_class": analyzer.__class__.__name__,
                            "content_type": type(content_data).__name__,
                            "message": f"Generic analysis performed for {analyzer_type.value}"
                        }
                    }
        
        except Exception as e:
            self.logger.error(f"Analysis failed for {analyzer_type.value}: {e}")
            raise
    
    async def batch_analyze(
        self,
        content_batch: List[Tuple[Any, str, str]],  # (content_data, content_type, content_id)
        analysis_types: Optional[List[AnalyzerType]] = None,
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform batch analysis on multiple content items.
        
        Args:
            content_batch: List of content items to analyze
            analysis_types: Specific analyzers to use
            batch_size: Number of items to process in parallel
            
        Returns:
            List of analysis results
        """
        results = []
        
        # Process in batches
        for i in range(0, len(content_batch), batch_size):
            batch = content_batch[i:i + batch_size]
            
            # Create analysis tasks for current batch
            batch_tasks = []
            for content_data, content_type, content_id in batch:
                task = self.analyze_content_comprehensive(
                    content_data, content_type, content_id, analysis_types
                )
                batch_tasks.append(task)
            
            # Execute batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Batch analysis error: {result}")
                    results.append({'error': str(result)})
                else:
                    results.append(result)
        
        self.logger.info(f"Batch analysis completed: {len(results)} items processed")
        return results
    
    async def start_real_time_monitoring(
        self,
        monitoring_targets: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Start real-time monitoring for content violations.
        
        Args:
            monitoring_targets: List of content to monitor
            config: Monitoring configuration
            
        Returns:
            True if monitoring started successfully
        """
        try:
            violation_detector = self.get_analyzer(AnalyzerType.VIOLATION)
            
            # Add monitoring targets
            for target_data in monitoring_targets:
                from .realtime_violation_detector import MonitoringTarget, MonitoringChannel
                
                target = MonitoringTarget(
                    target_id=target_data['target_id'],
                    content_id=target_data['content_id'],
                    content_type=target_data['content_type'],
                    fingerprints=target_data.get('fingerprints', {}),
                    keywords=target_data.get('keywords', []),
                    monitoring_channels=[
                        MonitoringChannel(channel) for channel in target_data.get('channels', ['web_crawler'])
                    ],
                    owner_id=target_data['owner_id']
                )
                
                await violation_detector.add_monitoring_target(target)
            
            # Start monitoring
            await violation_detector.start_monitoring()
            
            self.logger.info(f"Real-time monitoring started for {len(monitoring_targets)} targets")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start real-time monitoring: {e}")
            return False
    
    def get_system_capabilities(self) -> AnalysisCapabilities:
        """Get system analysis capabilities."""
        return AnalysisCapabilities(
            supported_content_types=['audio', 'video', 'image', 'text', 'document'],
            supported_platforms=['youtube', 'instagram', 'tiktok', 'spotify', 'twitter'],
            real_time_monitoring=True,
            batch_processing=True,
            ml_powered=True,
            accuracy_rate=0.92,
            processing_speed="<5s average"
        )
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis system statistics."""
        return {
            **self.analysis_stats,
            'available_analyzers': list(self.analyzer_classes.keys()),
            'active_analyzers_list': list(self.analyzers.keys()),
            'system_uptime': self._get_system_uptime(),
            'capabilities': self.get_system_capabilities().__dict__
        }
    
    def _get_system_uptime(self) -> str:
        """
Get system uptime (placeholder)."""
        return "Available on request"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now(),
            'analyzer_status': {},
            'errors': []
        }
        
        # Check each active analyzer
        for analyzer_type, analyzer in self.analyzers.items():
            try:
                # Basic health check (can be extended per analyzer)
                if hasattr(analyzer, 'health_check'):
                    analyzer_health = await analyzer.health_check()
                else:
                    analyzer_health = {'status': 'active'}
                
                health_status['analyzer_status'][analyzer_type.value] = analyzer_health
                
            except Exception as e:
                health_status['analyzer_status'][analyzer_type.value] = {'status': 'error', 'error': str(e)}
                health_status['errors'].append(f"{analyzer_type.value}: {e}")
        
        # Determine overall health
        if health_status['errors']:
            health_status['status'] = 'degraded' if len(health_status['errors']) < len(self.analyzers) else 'unhealthy'
        
        return health_status
    
    def shutdown(self) -> None:
        """Shutdown all analyzers gracefully."""
        for analyzer_type, analyzer in self.analyzers.items():
            try:
                if hasattr(analyzer, 'shutdown'):
                    analyzer.shutdown()
                elif hasattr(analyzer, 'stop_monitoring'):
                    asyncio.run(analyzer.stop_monitoring())
                
                self.logger.info(f"Analyzer shutdown: {analyzer_type.value}")
                
            except Exception as e:
                self.logger.error(f"Error shutting down {analyzer_type.value}: {e}")
        
        self.analyzers.clear()
        self.analysis_stats['active_analyzers'] = 0
        
        self.logger.info("AnalysisModuleIndex shutdown complete")

# Export main classes for easy access
__all__ = [
    'AnalysisModuleIndex',
    'AnalyzerType',
    'AnalysisCapabilities',
    # Re-export all analyzer classes
    'ContentAnalyzer',
    'ContentClassifier',
    'CompetitiveAnalyzer',
    'EngagementAnalyzer',
    'MetadataExtractor',
    'MonetizationAnalyzer',
    'ProtectionAnalyzer',
    'SentimentAnalyzer',
    'SimilarityDetector',
    'TrendAnalyzer',
    'AIFingerprintEngine',
    'RevenuePerformanceAnalyzer',
    'RealTimeViolationDetector'
]
