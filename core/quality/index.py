"""Quality Management System - Main Index Module

Central access point for all quality management components in the IA-Influencer platform.
This module provides convenient access to all quality analyzers, validators, and monitoring tools.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violators will face immediate legal action under German and international law.
Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, Any, Optional
import logging

# Import all quality components
from .content_validator import ContentQualityValidator
from .metrics_collector import QualityMetricsCollector
from .performance_monitor import PerformanceMonitor
from .validation_engine import ValidationEngine
from .seo_analyzer import SEOQualityAnalyzer
from .compliance_checker import ComplianceChecker
from .security_assessor import SecurityQualityAssessor
from .monetization_validator import MonetizationQualityValidator
from .platform_validator import PlatformQualityValidator
from .analytics_engine import QualityAnalyticsEngine
from .revenue_quality_analyzer import RevenueQualityAnalyzer
from .multiformat_analyzer import MultiFormatContentQualityAnalyzer
from .collaboration_analyzer import CollaborationQualityAnalyzer
from .protection_analyzer import ContentProtectionQualityAnalyzer

logger = logging.getLogger(__name__)


class QualityManagementSystem:
    """
    Central quality management system providing unified access to all quality components
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Quality Management System
        
        Args:
            config: Configuration dictionary for system components
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize all components
        self.content_validator = ContentQualityValidator()
        self.metrics_collector = QualityMetricsCollector()
        self.performance_monitor = PerformanceMonitor()
        self.validation_engine = ValidationEngine()
        self.seo_analyzer = SEOQualityAnalyzer()
        self.compliance_checker = ComplianceChecker()
        self.security_assessor = SecurityQualityAssessor()
        self.monetization_validator = MonetizationQualityValidator()
        self.platform_validator = PlatformQualityValidator()
        self.analytics_engine = QualityAnalyticsEngine()
        self.revenue_analyzer = RevenueQualityAnalyzer()
        self.multiformat_analyzer = MultiFormatContentQualityAnalyzer()
        self.collaboration_analyzer = CollaborationQualityAnalyzer()
        self.protection_analyzer = ContentProtectionQualityAnalyzer()
        
        self.logger.info("Quality Management System initialized successfully")
    
    async def comprehensive_quality_analysis(
        self,
        content_path: str,
        creator_data: Dict[str, Any],
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive quality analysis across all dimensions
        
        Args:
            content_path: Path to content file
            creator_data: Creator profile and data
            analysis_options: Options for analysis configuration
            
        Returns:
            Dict containing all analysis results
        """
        try:
            self.logger.info(f"Starting comprehensive quality analysis for {content_path}")
            
            results = {
                'content_path': content_path,
                'creator_id': creator_data.get('creator_id', 'unknown'),
                'analysis_timestamp': None,
                'overall_quality_score': 0.0,
                'analyses': {}
            }
            
            # Multi-format content analysis
            if analysis_options is None or analysis_options.get('multiformat_analysis', True):
                multiformat_result = await self.multiformat_analyzer.analyze_content_quality(
                    content_path, creator_data, analysis_options
                )
                results['analyses']['multiformat'] = multiformat_result.to_dict()
                results['analysis_timestamp'] = multiformat_result.analysis_timestamp.isoformat()
            
            # Content protection analysis
            if analysis_options is None or analysis_options.get('protection_analysis', True):
                protection_result = await self.protection_analyzer.analyze_protection_quality(
                    content_path, creator_data, analysis_options
                )
                results['analyses']['protection'] = protection_result.to_dict()
            
            # SEO analysis
            if analysis_options is None or analysis_options.get('seo_analysis', True):
                seo_result = await self.seo_analyzer.analyze_seo_quality(
                    {'content_path': content_path, **creator_data}
                )
                results['analyses']['seo'] = seo_result.to_dict()
            
            # Security assessment
            if analysis_options is None or analysis_options.get('security_analysis', True):
                security_result = await self.security_assessor.assess_security_quality(
                    {'content_path': content_path, **creator_data}
                )
                results['analyses']['security'] = security_result.to_dict()
            
            # Platform validation
            if analysis_options is None or analysis_options.get('platform_analysis', True):
                platform_result = await self.platform_validator.validate_platform_quality(
                    creator_data, 'all_platforms'
                )
                results['analyses']['platform'] = platform_result.to_dict()
            
            # Calculate overall quality score
            scores = []
            if 'multiformat' in results['analyses']:
                scores.append(results['analyses']['multiformat']['quality_metrics']['overall_score'])
            if 'protection' in results['analyses']:
                scores.append(results['analyses']['protection']['protection_readiness_score'])
            if 'seo' in results['analyses']:
                scores.append(results['analyses']['seo']['overall_seo_score'])
            if 'security' in results['analyses']:
                scores.append(results['analyses']['security']['overall_security_score'])
            if 'platform' in results['analyses']:
                scores.append(results['analyses']['platform']['overall_score'])
            
            if scores:
                results['overall_quality_score'] = sum(scores) / len(scores)
            
            self.logger.info(f"Comprehensive quality analysis completed with score {results['overall_quality_score']:.1f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive quality analysis: {str(e)}")
            raise
    
    async def creator_monetization_analysis(
        self,
        creator_data: Dict[str, Any],
        revenue_data: Dict[str, Any],
        engagement_data: Dict[str, Any],
        historical_data: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive creator monetization analysis
        
        Args:
            creator_data: Creator profile and metrics
            revenue_data: Revenue data across platforms
            engagement_data: Engagement metrics
            historical_data: Historical performance data
            
        Returns:
            Dict containing monetization analysis results
        """
        try:
            self.logger.info(f"Starting monetization analysis for creator {creator_data.get('creator_id', 'unknown')}")
            
            # Revenue quality analysis
            revenue_analysis = await self.revenue_analyzer.analyze_revenue_quality(
                creator_data, revenue_data, engagement_data, historical_data
            )
            
            # Monetization validation
            monetization_validation = await self.monetization_validator.validate_monetization_quality(
                creator_data, {'revenue_data': revenue_data, 'engagement_data': engagement_data}
            )
            
            results = {
                'creator_id': creator_data.get('creator_id', 'unknown'),
                'revenue_analysis': revenue_analysis.to_dict(),
                'monetization_validation': monetization_validation.to_dict(),
                'combined_score': (revenue_analysis.overall_revenue_quality_score + monetization_validation.overall_monetization_score) / 2
            }
            
            self.logger.info(f"Monetization analysis completed with combined score {results['combined_score']:.1f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in monetization analysis: {str(e)}")
            raise
    
    async def collaboration_opportunity_analysis(
        self,
        creator_data: Dict[str, Any],
        potential_partners: list,
        collaboration_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze collaboration opportunities and quality
        
        Args:
            creator_data: Primary creator data
            potential_partners: List of potential collaboration partners
            collaboration_preferences: Creator's collaboration preferences
            
        Returns:
            Dict containing collaboration analysis results
        """
        try:
            self.logger.info(f"Starting collaboration analysis for creator {creator_data.get('creator_id', 'unknown')}")
            
            collaboration_analysis = await self.collaboration_analyzer.analyze_collaboration_quality(
                creator_data, potential_partners, collaboration_preferences
            )
            
            return {
                'creator_id': creator_data.get('creator_id', 'unknown'),
                'collaboration_analysis': collaboration_analysis.to_dict(),
                'top_opportunities': len(collaboration_analysis.top_opportunities),
                'average_compatibility': collaboration_analysis.average_compatibility_score
            }
            
        except Exception as e:
            self.logger.error(f"Error in collaboration analysis: {str(e)}")
            raise
    
    async def compliance_validation(
        self,
        content_data: Dict[str, Any],
        platform_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive compliance validation
        
        Args:
            content_data: Content information and metadata
            platform_requirements: Platform-specific requirements
            
        Returns:
            Dict containing compliance validation results
        """
        try:
            self.logger.info("Starting compliance validation")
            
            compliance_result = await self.compliance_checker.check_compliance(
                content_data, platform_requirements or {}
            )
            
            return {
                'compliance_result': compliance_result.to_dict(),
                'is_compliant': compliance_result.overall_compliance_status == 'compliant',
                'critical_violations': len([v for v in compliance_result.violations if v.severity.value == 'critical'])
            }
            
        except Exception as e:
            self.logger.error(f"Error in compliance validation: {str(e)}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status and health
        
        Returns:
            Dict containing system status information
        """
        return {
            'system_name': 'Quality Management System',
            'version': '2.1.0',
            'status': 'operational',
            'components': {
                'content_validator': 'active',
                'metrics_collector': 'active',
                'performance_monitor': 'active',
                'validation_engine': 'active',
                'seo_analyzer': 'active',
                'compliance_checker': 'active',
                'security_assessor': 'active',
                'monetization_validator': 'active',
                'platform_validator': 'active',
                'analytics_engine': 'active',
                'revenue_analyzer': 'active',
                'multiformat_analyzer': 'active',
                'collaboration_analyzer': 'active',
                'protection_analyzer': 'active'
            },
            'created_by': 'Fahed Mlaiel',
            'contact': 'mlaiel@live.de'
        }


# Create a default instance for easy access
default_quality_system = None

def get_quality_system(config: Optional[Dict[str, Any]] = None) -> QualityManagementSystem:
    """
    Get or create the default quality management system instance
    
    Args:
        config: Optional configuration for the system
        
    Returns:
        QualityManagementSystem instance
    """
    global default_quality_system
    
    if default_quality_system is None:
        default_quality_system = QualityManagementSystem(config)
    
    return default_quality_system


# Export main components
__all__ = [
    'QualityManagementSystem',
    'get_quality_system',
    'ContentQualityValidator',
    'QualityMetricsCollector',
    'PerformanceMonitor',
    'ValidationEngine',
    'SEOQualityAnalyzer',
    'ComplianceChecker',
    'SecurityQualityAssessor',
    'MonetizationQualityValidator',
    'PlatformQualityValidator',
    'QualityAnalyticsEngine',
    'RevenueQualityAnalyzer',
    'MultiFormatContentQualityAnalyzer',
    'CollaborationQualityAnalyzer',
    'ContentProtectionQualityAnalyzer'
]
