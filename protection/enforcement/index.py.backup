"""Index file for Content Protection Enforcement Module
Main entry point and orchestration for comprehensive copyright enforcement system
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Core enforcement components
from . import (
    CopyrightEnforcementService,
    ContentMatchingEngine,
    PlatformHandlerManager,
    EvidenceCollectionService,
    LegalDocumentGenerator,
    AutomatedEscalationEngine,
    PerformanceAnalytics
)

# Import all enforcement classes and functions
from .content_matcher import *
from .platform_handlers import *
from .evidence_collector import *
from .legal_generator import *
from .escalation_manager import *
from .performance_analytics import *


logger = logging.getLogger(__name__)


class EnforcementOrchestrator:
    """
    Main orchestrator for the complete enforcement workflow
    Coordinates all enforcement components for comprehensive copyright protection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize core components
        self.enforcement_service = None
        self.content_matcher = None
        self.platform_handler = None
        self.evidence_collector = None
        self.legal_generator = None
        self.escalation_engine = None
        self.analytics = None
        
        # Workflow settings
        self.auto_enforcement = self.config.get('auto_enforcement', True)
        self.batch_processing = self.config.get('batch_processing', True)
        self.parallel_processing = self.config.get('parallel_processing', True)
        
        logger.info("Enforcement orchestrator initialized")
    
    async def initialize(self):
        """Initialize all enforcement components"""
        try:
            logger.info("Initializing enforcement components...")
            
            # Initialize core enforcement service
            from . import CopyrightEnforcementService
            self.enforcement_service = CopyrightEnforcementService(self.config.get('enforcement', {}))
            
            # Initialize content matching engine
            self.content_matcher = ContentMatchingEngine(self.config.get('content_matching', {}))
            await self.content_matcher.initialize()
            
            # Initialize platform handlers
            self.platform_handler = PlatformHandlerManager(self.config.get('platforms', {}))
            await self.platform_handler.initialize()
            
            # Initialize evidence collection
            self.evidence_collector = EvidenceCollectionService(self.config.get('evidence', {}))
            
            # Initialize legal document generator
            self.legal_generator = LegalDocumentGenerator(self.config.get('legal', {}))
            
            # Initialize escalation engine
            self.escalation_engine = AutomatedEscalationEngine(self.config.get('escalation', {}))
            
            # Initialize analytics
            self.analytics = PerformanceAnalytics(self.config.get('analytics', {}))
            
            logger.info("All enforcement components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing enforcement components: {e}")
            raise
    
    async def process_content_violation(
        self,
        original_content_id: str,
        suspected_violation_url: str,
        content_type: str = "audio",
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Complete workflow for processing a content violation
        
        Args:
            original_content_id: ID of the original protected content
            suspected_violation_url: URL of suspected infringing content
            content_type: Type of content (audio, video, text, image)
            priority: Processing priority (low, medium, high, urgent)
            
        Returns:
            Dict containing processing results and case information
        """
        try:
            logger.info(f"Processing content violation: {suspected_violation_url}")
            
            # Step 1: Content Analysis and Matching
            logger.debug("Step 1: Analyzing content for infringement")
            match_result = await self.content_matcher.analyze_content(
                original_content_id=original_content_id,
                suspected_content_url=suspected_violation_url,
                content_type=content_type
            )
            
            if not match_result.get('is_match', False):
                logger.info("No infringement detected")
                return {
                    'status': 'no_violation',
                    'match_result': match_result,
                    'case_id': None
                }
            
            # Step 2: Create Enforcement Case
            logger.debug("Step 2: Creating enforcement case")
            case_data = {
                'original_content_id': original_content_id,
                'violation_url': suspected_violation_url,
                'content_type': content_type,
                'priority': priority,
                'match_score': match_result.get('similarity_score', 0),
                'match_details': match_result,
                'detected_at': datetime.utcnow().isoformat()
            }
            
            case = await self.enforcement_service.create_case(case_data)
            case_id = case.id
            
            logger.info(f"Created enforcement case: {case_id}")
            
            # Step 3: Evidence Collection
            logger.debug("Step 3: Collecting evidence")
            evidence_package = await self.evidence_collector.collect_comprehensive_evidence(
                violation_url=suspected_violation_url,
                case_id=case_id,
                content_type=content_type
            )
            
            # Update case with evidence
            await self.enforcement_service.add_evidence(case_id, evidence_package)
            
            # Step 4: Platform Detection and Initial Action
            logger.debug("Step 4: Determining platform and taking initial action")
            platform_info = await self.platform_handler.detect_platform(suspected_violation_url)
            
            if platform_info:
                # Take initial enforcement action
                enforcement_result = await self.platform_handler.submit_takedown_request(
                    platform=platform_info['platform'],
                    violation_url=suspected_violation_url,
                    evidence_package=evidence_package,
                    case_id=case_id
                )
                
                # Update case with platform action
                await self.enforcement_service.update_case_status(
                    case_id=case_id,
                    status='platform_action_submitted',
                    details=enforcement_result
                )
            
            # Step 5: Monitor and Escalate if Needed
            if self.auto_enforcement:
                logger.debug("Step 5: Setting up automated monitoring and escalation")
                
                # Check if immediate escalation is needed
                escalation_rules = await self.escalation_engine.evaluate_case_for_escalation(
                    case_id=case_id,
                    case_data=case.to_dict()
                )
                
                for rule in escalation_rules:
                    if rule.priority >= 8:  # High priority rules
                        await self.escalation_engine.escalate_case(
                            case_id=case_id,
                            rule=rule,
                            trigger_data={'initial_assessment': True}
                        )
            
            # Step 6: Update Analytics
            logger.debug("Step 6: Updating performance analytics")
            await self.analytics.record_violation_processed(
                case_id=case_id,
                platform=platform_info.get('platform') if platform_info else 'unknown',
                content_type=content_type,
                match_score=match_result.get('similarity_score', 0)
            )
            
            result = {
                'status': 'violation_processed',
                'case_id': case_id,
                'match_result': match_result,
                'evidence_collected': len(evidence_package.get('evidence_items', [])),
                'platform_action': enforcement_result if platform_info else None,
                'escalations_triggered': len(escalation_rules) if escalation_rules else 0
            }
            
            logger.info(f"Content violation processing completed: {case_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing content violation: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'case_id': None
            }
    
    async def bulk_process_violations(
        self,
        violations: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Process multiple violations in batches
        
        Args:
            violations: List of violation data dictionaries
            batch_size: Number of violations to process concurrently
            
        Returns:
            List of processing results
        """
        try:
            logger.info(f"Processing {len(violations)} violations in batches of {batch_size}")
            
            results = []
            
            for i in range(0, len(violations), batch_size):
                batch = violations[i:i + batch_size]
                
                if self.parallel_processing:
                    # Process batch in parallel
                    tasks = [
                        self.process_content_violation(
                            original_content_id=violation.get('original_content_id'),
                            suspected_violation_url=violation.get('violation_url'),
                            content_type=violation.get('content_type', 'audio'),
                            priority=violation.get('priority', 'medium')
                        )
                        for violation in batch
                    ]
                    
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for j, result in enumerate(batch_results):
                        if isinstance(result, Exception):
                            logger.error(f"Error processing violation {i+j}: {result}")
                            results.append({
                                'status': 'error',
                                'error': str(result),
                                'violation_index': i + j
                            })
                        else:
                            results.append(result)
                else:
                    # Process batch sequentially
                    for j, violation in enumerate(batch):
                        try:
                            result = await self.process_content_violation(
                                original_content_id=violation.get('original_content_id'),
                                suspected_violation_url=violation.get('violation_url'),
                                content_type=violation.get('content_type', 'audio'),
                                priority=violation.get('priority', 'medium')
                            )
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Error processing violation {i+j}: {e}")
                            results.append({
                                'status': 'error',
                                'error': str(e),
                                'violation_index': i + j
                            })
                
                logger.debug(f"Completed batch {i//batch_size + 1}/{(len(violations) + batch_size - 1)//batch_size}")
            
            logger.info(f"Bulk processing completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk processing: {e}")
            raise
    
    async def generate_enforcement_report(
        self,
        report_type: str = "comprehensive",
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive enforcement report
        
        Args:
            report_type: Type of report (summary, comprehensive, detailed)
            time_period_days: Number of days to include in report
            
        Returns:
            Complete enforcement report
        """
        try:
            logger.info(f"Generating {report_type} enforcement report for {time_period_days} days")
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_period_days)
            
            # Generate performance report
            performance_report = await self.analytics.generate_performance_report(
                report_type=report_type,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get enforcement statistics
            enforcement_stats = await self.enforcement_service.get_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            # Get escalation statistics
            escalation_stats = await self.escalation_engine.get_escalation_statistics()
            
            # Get platform performance
            platform_stats = await self.platform_handler.get_platform_statistics()
            
            report = {
                'report_id': performance_report.id,
                'title': f"Enforcement Report - {report_type.title()}",
                'period': f"{start_date.date()} to {end_date.date()}",
                'generated_at': datetime.utcnow().isoformat(),
                'performance_metrics': [
                    {
                        'metric_id': m.metric_id,
                        'value': m.value,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in performance_report.metrics
                ],
                'enforcement_statistics': enforcement_stats,
                'escalation_statistics': escalation_stats,
                'platform_statistics': platform_stats,
                'insights': performance_report.insights,
                'recommendations': performance_report.recommendations,
                'charts': performance_report.charts
            }
            
            logger.info(f"Enforcement report generated: {performance_report.id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating enforcement report: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all enforcement components
        
        Returns:
            Health status of all components
        """
        try:
            health_status = {
                'overall_status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {}
            }
            
            # Check enforcement service
            try:
                if self.enforcement_service:
                    await self.enforcement_service.health_check()
                    health_status['components']['enforcement_service'] = 'healthy'
                else:
                    health_status['components']['enforcement_service'] = 'not_initialized'
            except Exception as e:
                health_status['components']['enforcement_service'] = f'unhealthy: {str(e)}'
                health_status['overall_status'] = 'degraded'
            
            # Check content matcher
            try:
                if self.content_matcher:
                    await self.content_matcher.health_check()
                    health_status['components']['content_matcher'] = 'healthy'
                else:
                    health_status['components']['content_matcher'] = 'not_initialized'
            except Exception as e:
                health_status['components']['content_matcher'] = f'unhealthy: {str(e)}'
                health_status['overall_status'] = 'degraded'
            
            # Check platform handlers
            try:
                if self.platform_handler:
                    platform_health = await self.platform_handler.health_check()
                    health_status['components']['platform_handlers'] = platform_health
                else:
                    health_status['components']['platform_handlers'] = 'not_initialized'
            except Exception as e:
                health_status['components']['platform_handlers'] = f'unhealthy: {str(e)}'
                health_status['overall_status'] = 'degraded'
            
            # Check evidence collector
            try:
                if self.evidence_collector:
                    evidence_health = await self.evidence_collector.health_check()
                    health_status['components']['evidence_collector'] = 'healthy'
                else:
                    health_status['components']['evidence_collector'] = 'not_initialized'
            except Exception as e:
                health_status['components']['evidence_collector'] = f'unhealthy: {str(e)}'
                health_status['overall_status'] = 'degraded'
            
            # Check legal generator
            try:
                if self.legal_generator:
                    health_status['components']['legal_generator'] = 'healthy'
                else:
                    health_status['components']['legal_generator'] = 'not_initialized'
            except Exception as e:
                health_status['components']['legal_generator'] = f'unhealthy: {str(e)}'
                health_status['overall_status'] = 'degraded'
            
            # Check escalation engine
            try:
                if self.escalation_engine:
                    health_status['components']['escalation_engine'] = 'healthy'
                else:
                    health_status['components']['escalation_engine'] = 'not_initialized'
            except Exception as e:
                health_status['components']['escalation_engine'] = f'unhealthy: {str(e)}'
                health_status['overall_status'] = 'degraded'
            
            # Check analytics
            try:
                if self.analytics:
                    health_status['components']['analytics'] = 'healthy'
                else:
                    health_status['components']['analytics'] = 'not_initialized'
            except Exception as e:
                health_status['components']['analytics'] = f'unhealthy: {str(e)}'
                health_status['overall_status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Shutdown all enforcement components gracefully"""
        try:
            logger.info("Shutting down enforcement orchestrator...")
            
            # Shutdown components in reverse order
            if self.analytics:
                await self.analytics.shutdown()
            
            if self.escalation_engine:
                await self.escalation_engine.shutdown()
            
            if self.platform_handler:
                await self.platform_handler.shutdown()
            
            if self.content_matcher:
                await self.content_matcher.shutdown()
            
            if self.enforcement_service:
                await self.enforcement_service.shutdown()
            
            logger.info("Enforcement orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global orchestrator instance
_orchestrator_instance = None


async def get_enforcement_orchestrator(config: Optional[Dict[str, Any]] = None) -> EnforcementOrchestrator:
    """Get or create the global enforcement orchestrator instance"""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = EnforcementOrchestrator(config)
        await _orchestrator_instance.initialize()
    
    return _orchestrator_instance


# Convenience functions for quick access
async def process_violation(
    original_content_id: str,
    violation_url: str,
    content_type: str = "audio",
    priority: str = "medium"
) -> Dict[str, Any]:
    """Quick function to process a single violation"""
    orchestrator = await get_enforcement_orchestrator()
    return await orchestrator.process_content_violation(
        original_content_id=original_content_id,
        suspected_violation_url=violation_url,
        content_type=content_type,
        priority=priority
    )


async def bulk_process_violations(violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Quick function to process multiple violations"""
    orchestrator = await get_enforcement_orchestrator()
    return await orchestrator.bulk_process_violations(violations)


async def generate_report(report_type: str = "comprehensive", days: int = 30) -> Dict[str, Any]:
    """Quick function to generate enforcement report"""
    orchestrator = await get_enforcement_orchestrator()
    return await orchestrator.generate_enforcement_report(report_type, days)


async def health_check() -> Dict[str, Any]:
    """Quick function to check system health"""
    orchestrator = await get_enforcement_orchestrator()
    return await orchestrator.health_check()


# Export all major components and functions
__all__ = [
    # Core orchestrator
    'EnforcementOrchestrator',
    'get_enforcement_orchestrator',
    
    # Convenience functions
    'process_violation',
    'bulk_process_violations',
    'generate_report',
    'health_check',
    
    # Import all component exports
    'CopyrightEnforcementService',
    'ContentMatchingEngine',
    'PlatformHandlerManager',
    'EvidenceCollectionService',
    'LegalDocumentGenerator',
    'AutomatedEscalationEngine',
    'PerformanceAnalytics',
    
    # All specific classes and functions from components
    'AudioMatcher',
    'VideoMatcher',
    'TextMatcher',
    'YouTubeHandler',
    'SpotifyHandler',
    'InstagramHandler',
    'TikTokHandler',
    'ScreenshotCollector',
    'MetadataCollector',
    'TimestampCollector',
    'DMCATemplateGenerator',
    'CeaseDesistGenerator',
    'LegalNoticeGenerator',
    'EscalationRule',
    'CaseEscalation',
    'MetricDefinition',
    'PerformanceReport'
]
