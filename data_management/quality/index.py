"""Quality Management Module Index - IA Influencer Agent
====================================================

Central index and factory for the enterprise-grade quality management system.
Provides unified access to all quality management components and orchestrates
quality workflows for multi-format content processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

🔒 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 🔒
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is STRICTLY PROHIBITED and will be prosecuted under international copyright law.

Business Logic: Quality request → Component factory → Workflow orchestration → 
Quality assessment → Results aggregation → Reporting & recommendations
"""import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass
from enum import Enum

# Import all quality management components
from .orchestrator import QualityOrchestrator
from .validator import (
    ContentValidator, AudioQualityValidator, VideoQualityValidator, 
    ImageQualityValidator, TextQualityValidator
)
from .metrics import (
    QualityMetricsEngine, ContentQualityScorer, PerformanceMetricsCalculator
)
from .integrity import (
    IntegrityController, ContentIntegrityVerifier, MetadataIntegrityChecker
)
from .compliance import (
    ComplianceChecker, ContentComplianceValidator, CopyrightComplianceChecker
)
from .reporter import (
    QualityReporter, QualityDashboardReporter, QualityAnalyticsReporter
)
from .processor import (
    QualityProcessor, BatchQualityProcessor, RealTimeQualityProcessor
)
from .monitor import (
    QualityMonitor, ContentQualityMonitor, SystemQualityMonitor
)
from .enhancer import (
    QualityEnhancer, ContentQualityEnhancer, AIQualityOptimizer
)


class QualityWorkflowType(Enum):
    """Types of quality workflows"""    CONTENT_VALIDATION = "content_validation"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    COMPLIANCE_CHECK = "compliance_check"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    REAL_TIME_MONITORING = "real_time_monitoring"
    BATCH_PROCESSING = "batch_processing"
    QUALITY_ENHANCEMENT = "quality_enhancement"


@dataclass
class QualityWorkflowConfig:
    """Configuration for quality workflows"""    workflow_type: QualityWorkflowType
    content_types: List[str]
    target_platforms: List[str]
    validation_level: str = "standard"
    enable_ai_enhancement: bool = True
    enable_compliance_check: bool = True
    enable_performance_monitoring: bool = True
    real_time_processing: bool = False
    generate_reports: bool = True
    custom_thresholds: Optional[Dict[str, float]] = None


class QualityManagerFactory:
    """    Factory class for creating quality management components and workflows.
    
    Provides centralized component creation, configuration management,
    and workflow orchestration for the IA Influencer quality system.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Component registry
        self._component_registry = {}
        self._workflow_registry = {}
        
        # Default configurations
        self.default_configs = {
            'orchestrator': {
                'max_concurrent_jobs': 10,
                'default_timeout': 300,
                'enable_caching': True,
                'cache_ttl': 3600
            },
            'validator': {
                'validation_timeout': 120,
                'enable_deep_analysis': True,
                'platform_specific_rules': True
            },
            'metrics': {
                'enable_trend_analysis': True,
                'metrics_retention_days': 30,
                'benchmark_updates': True
            },
            'integrity': {
                'cryptographic_verification': True,
                'metadata_preservation_check': True,
                'corruption_detection': True
            },
            'compliance': {
                'regulatory_updates': True,
                'platform_policy_sync': True,
                'copyright_database_access': True
            },
            'processor': {
                'batch_size': 100,
                'parallel_processing': True,
                'resource_optimization': True
            },
            'monitor': {
                'real_time_alerts': True,
                'performance_tracking': True,
                'quality_trends': True
            },
            'enhancer': {
                'ai_optimization': True,
                'automatic_enhancement': False,
                'quality_suggestions': True
            },
            'reporter': {
                'dashboard_updates': True,
                'analytics_retention': 90,
                'export_formats': ['json', 'pdf', 'csv']
            }
        }
    
    def create_orchestrator(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> QualityOrchestrator:
        """Create and configure a QualityOrchestrator instance."""        effective_config = {**self.default_configs['orchestrator']}
        if config:
            effective_config.update(config)
        
        if 'orchestrator' not in self._component_registry:
            self._component_registry['orchestrator'] = QualityOrchestrator(effective_config)
            self.logger.info("Created QualityOrchestrator instance")
        
        return self._component_registry['orchestrator']
    
    def create_content_validator(
        self, 
        content_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Union[ContentValidator, AudioQualityValidator, VideoQualityValidator, 
               ImageQualityValidator, TextQualityValidator]:
        """Create appropriate content validator based on content type."""        effective_config = {**self.default_configs['validator']}
        if config:
            effective_config.update(config)
        
        if content_type == 'audio':
            return AudioQualityValidator(effective_config)
        elif content_type == 'video':
            return VideoQualityValidator(effective_config)
        elif content_type == 'image':
            return ImageQualityValidator(effective_config)
        elif content_type == 'text':
            return TextQualityValidator(effective_config)
        else:
            return ContentValidator(effective_config)
    
    def create_metrics_engine(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> QualityMetricsEngine:
        """Create and configure a QualityMetricsEngine instance."""        effective_config = {**self.default_configs['metrics']}
        if config:
            effective_config.update(config)
        
        if 'metrics_engine' not in self._component_registry:
            self._component_registry['metrics_engine'] = QualityMetricsEngine(effective_config)
            self.logger.info("Created QualityMetricsEngine instance")
        
        return self._component_registry['metrics_engine']
    
    def create_content_scorer(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> ContentQualityScorer:
        """Create and configure a ContentQualityScorer instance."""        effective_config = {**self.default_configs['metrics']}
        if config:
            effective_config.update(config)
        
        return ContentQualityScorer(effective_config)
    
    def create_performance_calculator(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> PerformanceMetricsCalculator:
        """Create and configure a PerformanceMetricsCalculator instance."""        effective_config = {**self.default_configs['metrics']}
        if config:
            effective_config.update(config)
        
        return PerformanceMetricsCalculator(effective_config)
    
    def create_integrity_controller(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> IntegrityController:
        """Create and configure an IntegrityController instance."""        effective_config = {**self.default_configs['integrity']}
        if config:
            effective_config.update(config)
        
        if 'integrity_controller' not in self._component_registry:
            self._component_registry['integrity_controller'] = IntegrityController(effective_config)
            self.logger.info("Created IntegrityController instance")
        
        return self._component_registry['integrity_controller']
    
    def create_content_integrity_verifier(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> ContentIntegrityVerifier:
        """Create and configure a ContentIntegrityVerifier instance."""        effective_config = {**self.default_configs['integrity']}
        if config:
            effective_config.update(config)
        
        return ContentIntegrityVerifier(effective_config)
    
    def create_metadata_integrity_checker(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> MetadataIntegrityChecker:
        """Create and configure a MetadataIntegrityChecker instance."""        effective_config = {**self.default_configs['integrity']}
        if config:
            effective_config.update(config)
        
        return MetadataIntegrityChecker(effective_config)
    
    def create_compliance_checker(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> ComplianceChecker:
        """Create and configure a ComplianceChecker instance."""        effective_config = {**self.default_configs['compliance']}
        if config:
            effective_config.update(config)
        
        if 'compliance_checker' not in self._component_registry:
            self._component_registry['compliance_checker'] = ComplianceChecker(effective_config)
            self.logger.info("Created ComplianceChecker instance")
        
        return self._component_registry['compliance_checker']
    
    def create_content_compliance_validator(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> ContentComplianceValidator:
        """Create and configure a ContentComplianceValidator instance."""        effective_config = {**self.default_configs['compliance']}
        if config:
            effective_config.update(config)
        
        return ContentComplianceValidator(effective_config)
    
    def create_copyright_compliance_checker(
        self, 
        config: Optional[Dict[str, Any]] = None
    ) -> CopyrightComplianceChecker:
        """Create and configure a CopyrightComplianceChecker instance."""        effective_config = {**self.default_configs['compliance']}
        if config:
            effective_config.update(config)
        
        return CopyrightComplianceChecker(effective_config)
    
    def create_quality_processor(
        self, 
        processing_type: str = "standard",
        config: Optional[Dict[str, Any]] = None
    ) -> Union[QualityProcessor, BatchQualityProcessor, RealTimeQualityProcessor]:
        """Create appropriate quality processor based on processing type."""        effective_config = {**self.default_configs['processor']}
        if config:
            effective_config.update(config)
        
        if processing_type == "batch":
            return BatchQualityProcessor(effective_config)
        elif processing_type == "realtime":
            return RealTimeQualityProcessor(effective_config)
        else:
            return QualityProcessor(effective_config)
    
    def create_quality_monitor(
        self, 
        monitor_type: str = "standard",
        config: Optional[Dict[str, Any]] = None
    ) -> Union[QualityMonitor, ContentQualityMonitor, SystemQualityMonitor]:
        """Create appropriate quality monitor based on monitor type."""        effective_config = {**self.default_configs['monitor']}
        if config:
            effective_config.update(config)
        
        if monitor_type == "content":
            return ContentQualityMonitor(effective_config)
        elif monitor_type == "system":
            return SystemQualityMonitor(effective_config)
        else:
            return QualityMonitor(effective_config)
    
    def create_quality_enhancer(
        self, 
        enhancer_type: str = "standard",
        config: Optional[Dict[str, Any]] = None
    ) -> Union[QualityEnhancer, ContentQualityEnhancer, AIQualityOptimizer]:
        """Create appropriate quality enhancer based on enhancer type."""        effective_config = {**self.default_configs['enhancer']}
        if config:
            effective_config.update(config)
        
        if enhancer_type == "content":
            return ContentQualityEnhancer(effective_config)
        elif enhancer_type == "ai":
            return AIQualityOptimizer(effective_config)
        else:
            return QualityEnhancer(effective_config)
    
    def create_quality_reporter(
        self, 
        reporter_type: str = "standard",
        config: Optional[Dict[str, Any]] = None
    ) -> Union[QualityReporter, QualityDashboardReporter, QualityAnalyticsReporter]:
        """Create appropriate quality reporter based on reporter type."""        effective_config = {**self.default_configs['reporter']}
        if config:
            effective_config.update(config)
        
        if reporter_type == "dashboard":
            return QualityDashboardReporter(effective_config)
        elif reporter_type == "analytics":
            return QualityAnalyticsReporter(effective_config)
        else:
            return QualityReporter(effective_config)
    
    def create_quality_workflow(
        self, 
        workflow_config: QualityWorkflowConfig
    ) -> 'QualityWorkflow':
        """Create a complete quality workflow with all necessary components."""        workflow_id = f"{workflow_config.workflow_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create workflow components based on configuration
        components = {}
        
        # Always include orchestrator
        components['orchestrator'] = self.create_orchestrator()
        
        # Add components based on workflow type
        if workflow_config.workflow_type in [
            QualityWorkflowType.CONTENT_VALIDATION,
            QualityWorkflowType.COMPREHENSIVE_ANALYSIS
        ]:
            components['validator'] = self.create_content_validator()
            components['metrics_engine'] = self.create_metrics_engine()
            
        if workflow_config.enable_compliance_check:
            components['compliance_checker'] = self.create_compliance_checker()
            
        if workflow_config.workflow_type == QualityWorkflowType.COMPREHENSIVE_ANALYSIS:
            components['integrity_controller'] = self.create_integrity_controller()
            components['content_scorer'] = self.create_content_scorer()
            
        if workflow_config.enable_performance_monitoring:
            components['performance_calculator'] = self.create_performance_calculator()
            
        if workflow_config.real_time_processing:
            components['processor'] = self.create_quality_processor("realtime")
            components['monitor'] = self.create_quality_monitor("content")
        else:
            components['processor'] = self.create_quality_processor("batch")
            
        if workflow_config.enable_ai_enhancement:
            components['enhancer'] = self.create_quality_enhancer("ai")
            
        if workflow_config.generate_reports:
            components['reporter'] = self.create_quality_reporter("analytics")
        
        # Create workflow instance
        workflow = QualityWorkflow(
            workflow_id=workflow_id,
            config=workflow_config,
            components=components,
            factory=self
        )
        
        self._workflow_registry[workflow_id] = workflow
        self.logger.info(f"Created quality workflow: {workflow_id}")
        
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional['QualityWorkflow']:
        """Retrieve an existing workflow by ID."""        return self._workflow_registry.get(workflow_id)
    
    def list_workflows(self) -> List[str]:
        """List all active workflow IDs."""        return list(self._workflow_registry.keys())
    
    def cleanup_workflow(self, workflow_id: str) -> bool:
        """Clean up and remove a workflow."""        if workflow_id in self._workflow_registry:
            workflow = self._workflow_registry[workflow_id]
            workflow.cleanup()
            del self._workflow_registry[workflow_id]
            self.logger.info(f"Cleaned up workflow: {workflow_id}")
            return True
        return False


class QualityWorkflow:
    """    Complete quality workflow orchestrator for end-to-end quality management.
    
    Coordinates all quality management components to provide comprehensive
    content quality assessment, enhancement, and reporting.
    """    
    def __init__(
        self,
        workflow_id: str,
        config: QualityWorkflowConfig,
        components: Dict[str, Any],
        factory: QualityManagerFactory
    ):
        self.workflow_id = workflow_id
        self.config = config
        self.components = components
        self.factory = factory
        self.logger = logging.getLogger(f"{__name__}.QualityWorkflow")
        
        # Workflow state
        self.active = True
        self.results_cache = {}
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'average_processing_time': 0.0
        }
    
    async def process_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        target_platforms: Optional[List[str]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process content through the complete quality workflow."""        start_time = datetime.now()
        
        try:
            # Use workflow target platforms or provided ones
            platforms = target_platforms or self.config.target_platforms
            
            # Initialize results structure
            workflow_results = {
                'workflow_id': self.workflow_id,
                'content_type': content_type,
                'target_platforms': platforms,
                'processing_start': start_time.isoformat(),
                'validation_results': {},
                'metrics_results': {},
                'integrity_results': {},
                'compliance_results': {},
                'enhancement_results': {},
                'performance_results': {},
                'overall_quality_score': 0.0,
                'recommendations': [],
                'workflow_status': 'processing'
            }
            
            # Step 1: Content Validation
            if 'validator' in self.components:
                self.logger.info(f"Starting content validation for {content_type}")
                validation_results = await self.components['validator'].validate_content(
                    content_data=content_data,
                    content_type=content_type,
                    validation_level=self.config.validation_level
                )
                workflow_results['validation_results'] = validation_results
            
            # Step 2: Quality Metrics Calculation
            if 'metrics_engine' in self.components:
                self.logger.info("Calculating quality metrics")
                metrics_results = await self.components['metrics_engine'].calculate_quality_metrics(
                    content_data=content_data,
                    content_type=content_type,
                    validation_results=workflow_results.get('validation_results', {})
                )
                workflow_results['metrics_results'] = metrics_results
            
            # Step 3: Content Scoring
            if 'content_scorer' in self.components:
                self.logger.info("Calculating content quality scores")
                scoring_results = {}
                for platform in platforms:
                    platform_score = await self.components['content_scorer'].calculate_content_score(
                        content_type=content_type,
                        quality_metrics=workflow_results.get('metrics_results', {}),
                        platform_target=platform
                    )
                    scoring_results[platform] = platform_score
                workflow_results['scoring_results'] = scoring_results
            
            # Step 4: Integrity Verification
            if 'integrity_controller' in self.components:
                self.logger.info("Verifying content integrity")
                integrity_results = await self.components['integrity_controller'].verify_integrity(
                    content_data=content_data,
                    content_type=content_type,
                    integrity_level="comprehensive"
                )
                workflow_results['integrity_results'] = integrity_results
            
            # Step 5: Compliance Checking
            if 'compliance_checker' in self.components:
                self.logger.info("Checking compliance requirements")
                compliance_results = await self.components['compliance_checker'].check_compliance(
                    content_data=content_data,
                    content_type=content_type,
                    target_platforms=platforms,
                    compliance_level="comprehensive"
                )
                workflow_results['compliance_results'] = compliance_results
            
            # Step 6: Performance Analysis
            if 'performance_calculator' in self.components:
                processing_time = (datetime.now() - start_time).total_seconds()
                content_size = len(str(content_data)) if isinstance(content_data, str) else len(content_data) if isinstance(content_data, bytes) else 1000
                
                performance_results = await self.components['performance_calculator'].calculate_performance_metrics(
                    content_type=content_type,
                    processing_time=processing_time,
                    content_size=content_size
                )
                workflow_results['performance_results'] = performance_results
            
            # Step 7: Quality Enhancement (if enabled)
            if 'enhancer' in self.components and self.config.enable_ai_enhancement:
                self.logger.info("Generating quality enhancement recommendations")
                enhancement_results = await self.components['enhancer'].analyze_enhancement_opportunities(
                    content_data=content_data,
                    content_type=content_type,
                    quality_results=workflow_results
                )
                workflow_results['enhancement_results'] = enhancement_results
            
            # Step 8: Overall Quality Assessment
            overall_score = self._calculate_overall_quality_score(workflow_results)
            workflow_results['overall_quality_score'] = overall_score
            
            # Step 9: Generate Comprehensive Recommendations
            recommendations = self._generate_workflow_recommendations(workflow_results)
            workflow_results['recommendations'] = recommendations
            
            # Step 10: Generate Reports (if enabled)
            if 'reporter' in self.components and self.config.generate_reports:
                self.logger.info("Generating quality reports")
                report_results = await self.components['reporter'].generate_comprehensive_report(
                    workflow_results=workflow_results,
                    report_formats=['json', 'summary']
                )
                workflow_results['reports'] = report_results
            
            # Finalize workflow
            end_time = datetime.now()
            workflow_results.update({
                'processing_end': end_time.isoformat(),
                'total_processing_time': (end_time - start_time).total_seconds(),
                'workflow_status': 'completed'
            })
            
            # Update processing statistics
            self._update_processing_stats(workflow_results)
            
            # Cache results
            content_hash = hash(str(content_data)[:1000])  # Simplified hash
            self.results_cache[content_hash] = workflow_results
            
            self.logger.info(f"Quality workflow completed successfully: {self.workflow_id}")
            return workflow_results
            
        except Exception as e:
            error_time = datetime.now()
            self.logger.error(f"Quality workflow failed: {str(e)}")
            
            error_results = {
                'workflow_id': self.workflow_id,
                'content_type': content_type,
                'processing_start': start_time.isoformat(),
                'processing_end': error_time.isoformat(),
                'workflow_status': 'failed',
                'error': str(e),
                'overall_quality_score': 0.0,
                'recommendations': ['Review content and retry quality assessment']
            }
            
            self.processing_stats['failed'] += 1
            
            return error_results
    
    def _calculate_overall_quality_score(self, workflow_results: Dict[str, Any]) -> float:
        """Calculate overall quality score from all workflow components."""        scores = []
        weights = []
        
        # Validation score (25% weight)
        validation_results = workflow_results.get('validation_results', {})
        if 'score' in validation_results:
            scores.append(validation_results['score'])
            weights.append(0.25)
        
        # Metrics score (20% weight)
        metrics_results = workflow_results.get('metrics_results', {})
        if 'overall_score' in metrics_results:
            scores.append(metrics_results['overall_score'])
            weights.append(0.20)
        
        # Content scoring (25% weight)
        scoring_results = workflow_results.get('scoring_results', {})
        if scoring_results:
            platform_scores = [result.get('overall_score', 0.0) for result in scoring_results.values()]
            if platform_scores:
                avg_platform_score = sum(platform_scores) / len(platform_scores)
                scores.append(avg_platform_score)
                weights.append(0.25)
        
        # Integrity score (15% weight)
        integrity_results = workflow_results.get('integrity_results', {})
        if 'score' in integrity_results:
            scores.append(integrity_results['score'])
            weights.append(0.15)
        
        # Compliance score (15% weight)
        compliance_results = workflow_results.get('compliance_results', {})
        if 'score' in compliance_results:
            scores.append(compliance_results['score'])
            weights.append(0.15)
        
        # Calculate weighted average
        if scores and weights:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            overall_score = sum(score * weight for score, weight in zip(scores, normalized_weights))
            return round(overall_score, 3)
        
        return 0.5  # Neutral score if no components available
    
    def _generate_workflow_recommendations(self, workflow_results: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations from all workflow components."""        all_recommendations = []
        
        # Collect recommendations from all components
        for component_results in workflow_results.values():
            if isinstance(component_results, dict) and 'recommendations' in component_results:
                recommendations = component_results['recommendations']
                if isinstance(recommendations, list):
                    all_recommendations.extend(recommendations)
        
        # Add workflow-level recommendations
        overall_score = workflow_results.get('overall_quality_score', 0.0)
        
        if overall_score < 0.5:
            all_recommendations.append('Content requires significant quality improvements before publication')
        elif overall_score < 0.7:
            all_recommendations.append('Content quality is acceptable but has room for improvement')
        elif overall_score >= 0.9:
            all_recommendations.append('Excellent content quality - ready for premium distribution')
        
        # Platform-specific recommendations
        target_platforms = workflow_results.get('target_platforms', [])
        if len(target_platforms) > 1:
            all_recommendations.append('Consider platform-specific optimizations for best results')
        
        # Remove duplicates and sort by priority
        unique_recommendations = list(set(all_recommendations))
        return unique_recommendations[:10]  # Limit to top 10 recommendations
    
    def _update_processing_stats(self, workflow_results: Dict[str, Any]):
        """Update workflow processing statistics."""        self.processing_stats['total_processed'] += 1
        
        if workflow_results.get('workflow_status') == 'completed':
            self.processing_stats['successful'] += 1
        else:
            self.processing_stats['failed'] += 1
        
        # Update average processing time
        current_time = workflow_results.get('total_processing_time', 0.0)
        total_processed = self.processing_stats['total_processed']
        current_avg = self.processing_stats['average_processing_time']
        
        new_avg = ((current_avg * (total_processed - 1)) + current_time) / total_processed
        self.processing_stats['average_processing_time'] = round(new_avg, 3)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get workflow processing statistics."""        return {
            'workflow_id': self.workflow_id,
            'workflow_type': self.config.workflow_type.value,
            'active': self.active,
            'statistics': self.processing_stats.copy(),
            'cache_size': len(self.results_cache),
            'components_count': len(self.components)
        }
    
    def cleanup(self):
        """Clean up workflow resources."""        self.active = False
        self.results_cache.clear()
        self.components.clear()
        self.logger.info(f"Workflow {self.workflow_id} cleaned up")


# Convenience function for quick quality assessment
async def quick_quality_assessment(
    content_data: Union[bytes, str, Dict[str, Any]],
    content_type: str,
    target_platforms: Optional[List[str]] = None,
    validation_level: str = "standard"
) -> Dict[str, Any]:
    """    Perform a quick quality assessment using default workflow configuration.
    
    This is a convenience function for simple quality checks without
    creating a full workflow configuration.
    """    factory = QualityManagerFactory()
    
    workflow_config = QualityWorkflowConfig(
        workflow_type=QualityWorkflowType.CONTENT_VALIDATION,
        content_types=[content_type],
        target_platforms=target_platforms or ['general'],
        validation_level=validation_level,
        enable_ai_enhancement=False,
        enable_compliance_check=True,
        enable_performance_monitoring=False,
        real_time_processing=False,
        generate_reports=False
    )
    
    workflow = factory.create_quality_workflow(workflow_config)
    
    try:
        results = await workflow.process_content(
            content_data=content_data,
            content_type=content_type,
            target_platforms=target_platforms
        )
        return results
    finally:
        factory.cleanup_workflow(workflow.workflow_id)


# Convenience function for comprehensive analysis
async def comprehensive_quality_analysis(
    content_data: Union[bytes, str, Dict[str, Any]],
    content_type: str,
    target_platforms: List[str],
    enable_enhancement: bool = True
) -> Dict[str, Any]:
    """    Perform a comprehensive quality analysis with all features enabled.
    
    This function provides a complete quality assessment including
    validation, metrics, integrity, compliance, and enhancement recommendations.
    """    factory = QualityManagerFactory()
    
    workflow_config = QualityWorkflowConfig(
        workflow_type=QualityWorkflowType.COMPREHENSIVE_ANALYSIS,
        content_types=[content_type],
        target_platforms=target_platforms,
        validation_level="enterprise",
        enable_ai_enhancement=enable_enhancement,
        enable_compliance_check=True,
        enable_performance_monitoring=True,
        real_time_processing=False,
        generate_reports=True
    )
    
    workflow = factory.create_quality_workflow(workflow_config)
    
    try:
        results = await workflow.process_content(
            content_data=content_data,
            content_type=content_type,
            target_platforms=target_platforms
        )
        return results
    finally:
        factory.cleanup_workflow(workflow.workflow_id)
