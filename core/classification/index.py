"""Content Classification Module Index

Central orchestrator and entry point for the content classification system.
Provides unified interface for all classification, detection, and analysis capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.

⚠️ STRONG WARNING: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted
to the full extent of German and international copyright law.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime
from pathlib import Path
import mimetypes
from concurrent.futures import ThreadPoolExecutor

from . import (
    ClassifierFactory,
    ContentCategorizer,
    GenreDetector,
    MoodAnalyzer,
    QualityAssessor,
    SimilarityMatcher,
    ViolationDetector,
    CLASSIFICATION_THRESHOLDS,
    SUPPORTED_FORMATS
)
from ..engines.orchestration_engine import OrchestrationEngine
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class ClassificationOrchestrator:
    """
    Central orchestrator for content classification operations.
    
    Features:
    - Unified classification interface for all content types
    - Intelligent routing and load balancing
    - Batch processing capabilities
    - Real-time monitoring and analytics
    - Quality assurance and validation
    - Performance optimization and caching
    """
    
    def __init__(self):
        """
Initialize classification orchestrator."""
        self.settings = get_settings()
        
        # Initialize core components
        self.factory = ClassifierFactory()
        self.categorizer = ContentCategorizer()
        self.genre_detector = GenreDetector()
        self.mood_analyzer = MoodAnalyzer()
        self.quality_assessor = QualityAssessor()
        self.similarity_matcher = SimilarityMatcher()
        self.violation_detector = ViolationDetector()
        
        # Orchestration engine
        self.orchestration_engine = OrchestrationEngine()
        
        # Thread pool for parallel processing
        self.max_workers = self.settings.get('CLASSIFICATION_MAX_WORKERS', 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Performance tracking
        self.processed_count = 0
        self.error_count = 0
        self.last_performance_report = datetime.utcnow()
        
    @track_performance
    async def classify_content_comprehensive(
        self,
        content_path: str,
        content_id: str,
        owner_id: str,
        analysis_options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive content classification and analysis.
        
        Args:
            content_path: Path to content file
            content_id: Unique content identifier
            owner_id: Content owner identifier
            analysis_options: Optional analysis configuration
            
        Returns:
            Comprehensive classification results
        """
        try:
            # Determine content type
            content_type = self._determine_content_type(content_path)
            
            # Default analysis options
            default_options = {
                'genre_detection': True,
                'mood_analysis': True,
                'quality_assessment': True,
                'similarity_matching': True,
                'violation_detection': True,
                'categorization': True
            }
            
            if analysis_options:
                default_options.update(analysis_options)
            
            # Initialize results structure
            results = {
                'content_id': content_id,
                'content_type': content_type,
                'content_path': content_path,
                'owner_id': owner_id,
                'timestamp': datetime.utcnow().isoformat(),
                'analysis_status': 'processing'
            }
            
            # Parallel classification tasks
            tasks = []
            
            # Core classification
            classifier = self.factory.create_classifier(content_type)
            classification_task = asyncio.create_task(
                self._run_in_executor(classifier.classify, content_path)
            )
            tasks.append(('classification', classification_task))
            
            # Optional analyses
            if default_options['genre_detection']:
                genre_task = asyncio.create_task(
                    self._run_in_executor(self.genre_detector.detect_genre, content_path, content_type)
                )
                tasks.append(('genre', genre_task))
            
            if default_options['mood_analysis']:
                mood_task = asyncio.create_task(
                    self._run_in_executor(self.mood_analyzer.analyze_mood, content_path, content_type)
                )
                tasks.append(('mood', mood_task))
            
            if default_options['quality_assessment']:
                quality_task = asyncio.create_task(
                    self._run_in_executor(self.quality_assessor.assess_quality, content_path, content_type)
                )
                tasks.append(('quality', quality_task))
            
            if default_options['categorization']:
                category_task = asyncio.create_task(
                    self._run_in_executor(self.categorizer.categorize_content, content_path, content_type)
                )
                tasks.append(('categorization', category_task))
            
            # Execute tasks and collect results
            for name, task in tasks:
                try:
                    result = await task
                    results[name] = result
                except Exception as e:
                    logger.error(f"Error in {name} analysis: {e}")
                    results[name] = {'error': str(e), 'status': 'failed'}
            
            # Similarity matching (if enabled)
            if default_options['similarity_matching']:
                try:
                    similar_content = await self._run_in_executor(
                        self.similarity_matcher.find_similar_content,
                        content_path, content_type, 10
                    )
                    results['similarity'] = {
                        'similar_content': similar_content,
                        'status': 'completed'
                    }
                except Exception as e:
                    logger.error(f"Error in similarity matching: {e}")
                    results['similarity'] = {'error': str(e), 'status': 'failed'}
            
            # Violation detection (if enabled)
            if default_options['violation_detection']:
                try:
                    violations = await self._run_in_executor(
                        self.violation_detector.detect_violations,
                        content_id, content_path, content_type, owner_id
                    )
                    results['violations'] = {
                        'detected_violations': violations,
                        'violation_count': len(violations),
                        'status': 'completed'
                    }
                except Exception as e:
                    logger.error(f"Error in violation detection: {e}")
                    results['violations'] = {'error': str(e), 'status': 'failed'}
            
            # Add content to similarity index
            try:
                self.similarity_matcher.add_content_to_index(
                    content_path, content_type, content_id
                )
            except Exception as e:
                logger.warning(f"Could not add content to similarity index: {e}")
            
            # Calculate overall confidence and quality scores
            results['summary'] = self._calculate_summary_metrics(results)
            results['analysis_status'] = 'completed'
            
            # Update performance metrics
            self.processed_count += 1
            
            logger.info(f"Comprehensive classification completed for content {content_id}")
            return results
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in comprehensive classification: {e}")
            return {
                'content_id': content_id,
                'error': str(e),
                'analysis_status': 'failed',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _run_in_executor(self, func, *args):
        """Run blocking function in thread pool executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
    
    def _determine_content_type(self, content_path: str) -> str:
        """
Determine content type from file path."""
        try:
            # Get file extension
            file_path = Path(content_path)
            extension = file_path.suffix.lower()
            
            # Check against supported formats
            for content_type, extensions in SUPPORTED_FORMATS.items():
                if extension in extensions:
                    return content_type
            
            # Try MIME type detection
            mime_type, _ = mimetypes.guess_type(content_path)
            if mime_type:
                if mime_type.startswith('audio/'):
                    return 'audio'
                elif mime_type.startswith('video/'):
                    return 'video'
                elif mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('text/'):
                    return 'text'
            
            # Default to multimodal for unknown types
            return 'multimodal'
            
        except Exception as e:
            logger.error(f"Error determining content type: {e}")
            return 'unknown'
    
    def _calculate_summary_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary metrics from classification results."""
        try:
            summary = {
                'overall_confidence': 0.0,
                'quality_score': 0.0,
                'risk_level': 'low',
                'recommendation': 'approved'
            }
            
            # Collect confidence scores
            confidences = []
            
            if 'classification' in results and 'confidence' in results['classification']:
                confidences.append(results['classification']['confidence'])
            
            if 'genre' in results and 'confidence' in results['genre']:
                confidences.append(results['genre']['confidence'])
            
            if 'mood' in results and 'confidence' in results['mood']:
                confidences.append(results['mood']['confidence'])
            
            # Calculate overall confidence
            if confidences:
                summary['overall_confidence'] = float(np.mean(confidences))
            
            # Get quality score
            if 'quality' in results and 'overall_score' in results['quality']:
                summary['quality_score'] = results['quality']['overall_score']
            
            # Determine risk level based on violations
            if 'violations' in results:
                violation_count = results['violations'].get('violation_count', 0)
                if violation_count > 0:
                    summary['risk_level'] = 'high'
                    summary['recommendation'] = 'review_required'
                elif violation_count == 0:
                    summary['risk_level'] = 'low'
                    summary['recommendation'] = 'approved'
            
            # Adjust recommendation based on quality
            if summary['quality_score'] < 0.5:
                summary['recommendation'] = 'quality_improvement_needed'
            elif summary['quality_score'] > 0.8 and summary['risk_level'] == 'low':
                summary['recommendation'] = 'premium_approved'
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating summary metrics: {e}")
            return {
                'overall_confidence': 0.0,
                'quality_score': 0.0,
                'risk_level': 'unknown',
                'recommendation': 'manual_review'
            }
    
    @track_performance
    async def batch_classify_content(
        self,
        content_list: List[Dict[str, str]],
        analysis_options: Optional[Dict[str, bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Batch classify multiple content items.
        
        Args:
            content_list: List of content items with path, id, owner_id
            analysis_options: Optional analysis configuration
            
        Returns:
            List of classification results
        """
        try:
            logger.info(f"Starting batch classification of {len(content_list)} items")
            
            # Create tasks for parallel processing
            tasks = []
            for content_item in content_list:
                task = asyncio.create_task(
                    self.classify_content_comprehensive(
                        content_item['content_path'],
                        content_item['content_id'],
                        content_item['owner_id'],
                        analysis_options
                    )
                )
                tasks.append(task)
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = {
                        'content_id': content_list[i]['content_id'],
                        'error': str(result),
                        'analysis_status': 'failed',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    processed_results.append(error_result)
                    self.error_count += 1
                else:
                    processed_results.append(result)
                    self.processed_count += 1
            
            logger.info(f"Batch classification completed: {len(processed_results)} items processed")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch classification: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the classification system."""
        try:
            current_time = datetime.utcnow()
            time_since_last_report = (current_time - self.last_performance_report).total_seconds()
            
            metrics = {
                'processed_count': self.processed_count,
                'error_count': self.error_count,
                'success_rate': (self.processed_count - self.error_count) / max(self.processed_count, 1),
                'processing_rate': self.processed_count / max(time_since_last_report, 1),
                'uptime_seconds': time_since_last_report,
                'active_workers': self.max_workers,
                'similarity_index_stats': self.similarity_matcher.get_similarity_stats()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on classification system."""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {}
            }
            
            # Check classifiers
            try:
                test_classifier = self.factory.create_classifier('audio')
                health_status['components']['audio_classifier'] = 'healthy'
            except Exception as e:
                health_status['components']['audio_classifier'] = f'error: {e}'
                health_status['status'] = 'degraded'
            
            # Check similarity matcher
            try:
                stats = self.similarity_matcher.get_similarity_stats()
                health_status['components']['similarity_matcher'] = 'healthy'
                health_status['similarity_index_size'] = stats.get('audio_index_size', 0)
            except Exception as e:
                health_status['components']['similarity_matcher'] = f'error: {e}'
                health_status['status'] = 'degraded'
            
            # Check violation detector
            try:
                detector_stats = self.violation_detector.get_violation_stats('test_user')
                health_status['components']['violation_detector'] = 'healthy'
            except Exception as e:
                health_status['components']['violation_detector'] = f'error: {e}'
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def shutdown(self):
        """Gracefully shutdown the classification orchestrator."""
        try:
            logger.info("Shutting down classification orchestrator...")
            
            # Shutdown thread pool
            self.executor.shutdown(wait=True)
            
            # Save similarity indexes
            self.similarity_matcher.save_indexes()
            
            logger.info("Classification orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> ClassificationOrchestrator:
    """Get global classification orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ClassificationOrchestrator()
    return _orchestrator


# Convenience functions for direct access
async def classify_content(content_path: str, content_id: str, owner_id: str) -> Dict[str, Any]:
    """
Convenience function for content classification."""
    orchestrator = get_orchestrator()
    return await orchestrator.classify_content_comprehensive(content_path, content_id, owner_id)


async def batch_classify(content_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
Convenience function for batch classification."""
    orchestrator = get_orchestrator()
    return await orchestrator.batch_classify_content(content_list)


def get_health_status() -> Dict[str, Any]:
    """
Convenience function for health check."""
    orchestrator = get_orchestrator()
    return orchestrator.health_check()


def get_metrics() -> Dict[str, Any]:
    """
Convenience function for performance metrics."""
    orchestrator = get_orchestrator()
    return orchestrator.get_performance_metrics()
