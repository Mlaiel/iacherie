"""
Quality Agent Module Index - Advanced Quality Assessment System

Main index file for the Quality Agent module providing comprehensive quality control,
assessment, and enhancement capabilities for multi-format content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .quality_agent import QualityAgent, QualityAgentManager
from .quality_assessor import QualityAssessor, ContentScorer
from .quality_enhancer import QualityEnhancer, ImprovementEngine
from .standards_checker import StandardsChecker, ComplianceValidator
from .performance_analyzer import PerformanceAnalyzer, MetricsCalculator

# Main module interface
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export main classes
__all__ = [
    'QualityAgent',
    'QualityAgentManager', 
    'QualityAssessor',
    'ContentScorer',
    'QualityEnhancer',
    'ImprovementEngine',
    'StandardsChecker',
    'ComplianceValidator',
    'PerformanceAnalyzer',
    'MetricsCalculator'
]

# Module configuration
QUALITY_AGENT_CONFIG = {
    "version": __version__,
    "supported_formats": {
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "video": [".mp4", ".avi", ".mov", ".wmv", ".mkv"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "text": [".txt", ".md", ".html", ".docx"]
    },
    "quality_thresholds": {
        "poor": 0.3,
        "fair": 0.5,
        "good": 0.7,
        "excellent": 0.85,
        "professional": 0.95
    },
    "assessment_categories": [
        "technical",
        "creative", 
        "commercial",
        "compliance",
        "accessibility",
        "engagement"
    ]
}

def get_quality_agent(**kwargs):
    """
    Factory function to create a QualityAgent instance.
    
    Args:
        **kwargs: Configuration parameters for the agent
        
    Returns:
        QualityAgent: Configured quality agent instance
    """
    return QualityAgent(**kwargs)

def get_quality_assessor(**kwargs):
    """
    Factory function to create a QualityAssessor instance.
    
    Args:
        **kwargs: Configuration parameters for the assessor
        
    Returns:
        QualityAssessor: Configured quality assessor instance
    """
    return QualityAssessor(**kwargs)

def get_quality_enhancer(**kwargs):
    """
    Factory function to create a QualityEnhancer instance.
    
    Args:
        **kwargs: Configuration parameters for the enhancer
        
    Returns:
        QualityEnhancer: Configured quality enhancer instance
    """
    return QualityEnhancer(**kwargs)

def get_standards_checker(**kwargs):
    """
    Factory function to create a StandardsChecker instance.
    
    Args:
        **kwargs: Configuration parameters for the checker
        
    Returns:
        StandardsChecker: Configured standards checker instance
    """
    return StandardsChecker(**kwargs)

def get_performance_analyzer(**kwargs):
    """
    Factory function to create a PerformanceAnalyzer instance.
    
    Args:
        **kwargs: Configuration parameters for the analyzer
        
    Returns:
        PerformanceAnalyzer: Configured performance analyzer instance
    """
    return PerformanceAnalyzer(**kwargs)

# Module health check
async def module_health_check():
    """
    Perform health check on the quality agent module.
    
    Returns:
        Dict[str, Any]: Health status information
    """
    try:
        # Test basic functionality
        agent = QualityAgent()
        
        health_status = {
            "status": "healthy",
            "version": __version__,
            "components": {
                "quality_agent": True,
                "quality_assessor": True,
                "quality_enhancer": True,
                "standards_checker": True,
                "performance_analyzer": True
            },
            "capabilities": {
                "multi_format_support": True,
                "real_time_analysis": True,
                "ai_enhancement": True,
                "compliance_checking": True,
                "performance_monitoring": True
            }
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": __version__
        }

# Quality assessment pipeline
class QualityPipeline:
    """
    Complete quality assessment and enhancement pipeline.
    
    This class orchestrates the entire quality assessment process from
    initial analysis through enhancement recommendations and implementation.
    """
    
    def __init__(self, config=None):
        self.config = config or QUALITY_AGENT_CONFIG
        self.agent = QualityAgent(config=self.config)
        self.assessor = QualityAssessor(config=self.config)
        self.enhancer = QualityEnhancer(config=self.config)
        self.standards_checker = StandardsChecker(config=self.config)
        self.performance_analyzer = PerformanceAnalyzer(config=self.config)
        
    async def process_content(self, content_id, content_path, content_type, metadata=None):
        """
        Process content through complete quality pipeline.
        
        Args:
            content_id: Unique identifier for content
            content_path: Path to content file
            content_type: Type of content
            metadata: Additional content metadata
            
        Returns:
            Dict[str, Any]: Complete quality analysis and enhancement results
        """
        results = {}
        
        # Step 1: Quality Assessment
        quality_analysis = await self.agent.analyze_content_quality(
            content_id, content_path, content_type, metadata
        )
        results["quality_analysis"] = quality_analysis
        
        # Step 2: Detailed Assessment
        detailed_assessment = await self.assessor.assess_content_quality(
            content_id, content_path, content_type, metadata=metadata
        )
        results["detailed_assessment"] = detailed_assessment
        
        # Step 3: Standards Compliance Check
        compliance_results = await self.standards_checker.check_compliance(
            content_path, content_type
        )
        results["compliance"] = compliance_results
        
        # Step 4: Performance Analysis
        performance_metrics = await self.performance_analyzer.analyze_performance(
            content_path, content_type
        )
        results["performance"] = performance_metrics
        
        # Step 5: Enhancement Recommendations
        if quality_analysis.quality_score.overall_score < 0.8:
            enhancement_plan = await self.enhancer.generate_enhancement_plan(
                quality_analysis, detailed_assessment
            )
            results["enhancement_plan"] = enhancement_plan
        
        return results

# Export pipeline for easy access
def get_quality_pipeline(**kwargs):
    """
    Factory function to create a QualityPipeline instance.
    
    Args:
        **kwargs: Configuration parameters for the pipeline
        
    Returns:
        QualityPipeline: Configured quality pipeline instance
    """
    return QualityPipeline(**kwargs)
