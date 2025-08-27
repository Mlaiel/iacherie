"""
Content Service - Business logic layer for content generation

Professional service layer that orchestrates content generation workflows,
manages business rules, and provides high-level API for content operations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import uuid
from dataclasses import asdict

from .generation_manager import GenerationManager
from .quality_enhancer import QualityEnhancer
from .format_optimizer import FormatOptimizer
from .seo_optimizer import SEOOptimizer
from .performance_tracker import PerformanceTracker
from .quality_metrics import QualityMetrics
from .social_templates import SocialMediaTemplates
from .blog_templates import BlogTemplates
from .marketing_templates import MarketingTemplates


class ContentService:
    """
    High-level content service that provides:
    
    - Unified content generation API
    - Business rule enforcement
    - Quality assurance workflows
    - Performance monitoring integration
    - Template-based content creation
    - Multi-platform optimization
    - Automated content enhancement
    - Analytics and reporting
    """
    
    def __init__(self):
        """Initialize content service"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize core components
        manager_config = {
            "max_concurrent_requests": 10,
            "queue_size_limit": 100,
            "default_timeout": 300,
            "retry_attempts": 3,
            "enable_caching": True,
            "cache_ttl": 3600,
            "enable_monitoring": True,
            "resource_monitoring": True,
            "performance_tracking": True
        }
        self.generation_manager = GenerationManager(config=manager_config)
        self.quality_enhancer = QualityEnhancer()
        self.format_optimizer = FormatOptimizer()
        self.seo_optimizer = SEOOptimizer()
        self.performance_tracker = PerformanceTracker()
        self.quality_metrics = QualityMetrics()
        
        # Initialize template engines
        self.social_templates = SocialMediaTemplates()
        self.blog_templates = BlogTemplates()
        self.marketing_templates = MarketingTemplates()
        
        # Content workflow configurations
        self.workflow_configs = {
            'social_media': {
                'steps': ['generate', 'optimize_format', 'enhance_quality', 'track_performance'],
                'quality_threshold': 0.7,
                'auto_publish': False
            },
            'blog_post': {
                'steps': ['generate', 'enhance_quality', 'optimize_seo', 'track_performance'],
                'quality_threshold': 0.8,
                'auto_publish': False
            },
            'marketing_email': {
                'steps': ['generate', 'optimize_format', 'enhance_quality', 'a_b_test'],
                'quality_threshold': 0.75,
                'auto_publish': False
            },
            'product_description': {
                'steps': ['generate', 'optimize_seo', 'enhance_quality'],
                'quality_threshold': 0.8,
                'auto_publish': True
            }
        }
        
        # Business rules
        self.business_rules = {
            'max_content_length': {
                'social_post': 2200,
                'blog_post': 10000,
                'email': 2000,
                'product_description': 1000
            },
            'min_quality_score': 0.6,
            'required_seo_score': 0.5,
            'brand_voice_compliance': 0.7
        }
    
    async def create_content(
        self,
        content_type: str,
        request_data: Dict[str, Any],
        workflow: Optional[str] = None,
        auto_enhance: bool = True
    ) -> Dict[str, Any]:
        """
        Create content using specified workflow.
        
        Args:
            content_type: Type of content to create
            request_data: Content creation parameters
            workflow: Workflow to use (auto-detected if None)
            auto_enhance: Whether to apply automatic enhancements
            
        Returns:
            Complete content creation result
        """
        try:
            # Generate unique content ID
            content_id = str(uuid.uuid4())
            
            # Determine workflow
            if not workflow:
                workflow = self._determine_workflow(content_type)
            
            # Get workflow configuration
            workflow_config = self.workflow_configs.get(workflow, self.workflow_configs['social_media'])
            
            # Initialize result
            result = {
                'content_id': content_id,
                'content_type': content_type,
                'workflow': workflow,
                'status': 'in_progress',
                'created_at': datetime.now().isoformat(),
                'steps_completed': [],
                'quality_scores': {},
                'enhancements_applied': [],
                'final_content': None,
                'metadata': {}
            }
            
            # Execute workflow steps
            current_content = None
            
            for step in workflow_config['steps']:
                try:
                    step_result = await self._execute_workflow_step(
                        step, content_type, request_data, current_content
                    )
                    
                    if step == 'generate':
                        current_content = step_result.get('content')
                        result['original_content'] = current_content
                    elif step in ['optimize_format', 'enhance_quality', 'optimize_seo']:
                        if 'optimized_content' in step_result:
                            current_content = step_result['optimized_content']
                        elif 'enhanced_content' in step_result:
                            current_content = step_result['enhanced_content']
                    
                    # Store step results
                    result[f'{step}_result'] = step_result
                    result['steps_completed'].append(step)
                    
                    self.logger.info(f"Completed step: {step} for content {content_id}")
                    
                except Exception as e:
                    self.logger.error(f"Step {step} failed for content {content_id}: {str(e)}")
                    result['error'] = f"Step {step} failed: {str(e)}"
                    break
            
            # Set final content
            result['final_content'] = current_content
            
            # Validate against business rules
            validation_result = await self._validate_business_rules(
                current_content, content_type, result
            )
            result['validation'] = validation_result
            
            # Determine final status
            if validation_result.get('passed', False):
                result['status'] = 'completed'
            else:
                result['status'] = 'needs_review'
            
            # Auto-publish if configured and validation passed
            if (workflow_config.get('auto_publish', False) and 
                validation_result.get('passed', False)):
                result['status'] = 'published'
                result['published_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Content creation completed: {content_id} - Status: {result['status']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content creation failed: {str(e)}")
            return {
                'content_id': content_id,
                'status': 'failed',
                'error': str(e),
                'created_at': datetime.now().isoformat()
            }
    
    async def create_from_template(
        self,
        template_type: str,
        template_category: str,
        template_data: Dict[str, Any],
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create content from template.
        
        Args:
            template_type: Type of template (social, blog, marketing)
            template_category: Specific template category
            template_data: Data to fill template
            platform: Target platform for optimization
            
        Returns:
            Template-based content result
        """
        try:
            content_id = str(uuid.uuid4())
            
            # Get appropriate template engine
            if template_type == 'social':
                template_engine = self.social_templates
            elif template_type == 'blog':
                template_engine = self.blog_templates
            elif template_type == 'marketing':
                template_engine = self.marketing_templates
            else:
                raise ValueError(f"Unknown template type: {template_type}")
            
            # Fill template
            filled_content = template_engine.fill_template(
                template_category, template_type, template_data
            )
            
            # Create content creation request
            request_data = {
                'content': filled_content,
                'platform': platform,
                'template_based': True,
                **template_data
            }
            
            # Use template-optimized workflow
            workflow = 'social_media' if template_type == 'social' else template_type
            
            # Create content using standard workflow
            result = await self.create_content(
                content_type=f"{template_type}_from_template",
                request_data=request_data,
                workflow=workflow
            )
            
            # Add template metadata
            result['template_info'] = {
                'template_type': template_type,
                'template_category': template_category,
                'template_engine': template_engine.__class__.__name__
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Template-based content creation failed: {str(e)}")
            return {
                'content_id': str(uuid.uuid4()),
                'status': 'failed',
                'error': str(e),
                'template_info': {
                    'template_type': template_type,
                    'template_category': template_category
                }
            }
    
    async def optimize_existing_content(
        self,
        content: str,
        optimization_type: str,
        target_platform: Optional[str] = None,
        optimization_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize existing content.
        
        Args:
            content: Content to optimize
            optimization_type: Type of optimization (quality, seo, format)
            target_platform: Platform to optimize for
            optimization_params: Optimization parameters
            
        Returns:
            Optimization result
        """
        try:
            content_id = str(uuid.uuid4())
            params = optimization_params or {}
            
            result = {
                'content_id': content_id,
                'optimization_type': optimization_type,
                'original_content': content,
                'optimized_content': content,
                'optimizations_applied': [],
                'performance_improvement': {}
            }
            
            if optimization_type == 'quality':
                enhancement_result = await self.quality_enhancer.enhance_content(
                    content, 'general', params
                )
                result['optimized_content'] = enhancement_result['enhanced_content']
                result['optimizations_applied'] = enhancement_result['enhancements_applied']
                result['quality_improvement'] = enhancement_result['improvement_score']
                
            elif optimization_type == 'seo':
                seo_result = await self.seo_optimizer.optimize_content(
                    content, params.get('keywords', []), params
                )
                result['optimized_content'] = seo_result['optimized_content']
                result['seo_score'] = seo_result['seo_score']
                result['optimizations_applied'] = seo_result['optimizations_applied']
                
            elif optimization_type == 'format' and target_platform:
                format_result = await self.format_optimizer.optimize_format(
                    content, target_platform, params
                )
                result['optimized_content'] = format_result['optimized_content']
                result['format_changes'] = format_result['format_changes']
                result['optimization_metrics'] = format_result['optimization_metrics']
                
            else:
                raise ValueError(f"Unknown optimization type: {optimization_type}")
            
            # Analyze quality improvement
            if optimization_type != 'seo':  # SEO has its own scoring
                original_quality = await self.quality_metrics.analyze_content_quality(
                    content, 'general'
                )
                optimized_quality = await self.quality_metrics.analyze_content_quality(
                    result['optimized_content'], 'general'
                )
                
                result['performance_improvement'] = {
                    'original_score': original_quality.overall_score,
                    'optimized_score': optimized_quality.overall_score,
                    'improvement': optimized_quality.overall_score - original_quality.overall_score
                }
            
            result['status'] = 'completed'
            return result
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            return {
                'content_id': str(uuid.uuid4()),
                'status': 'failed',
                'error': str(e)
            }
    
    async def analyze_content_performance(
        self,
        content_id: str,
        platform_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze content performance and generate insights.
        
        Args:
            content_id: Content identifier
            platform_metrics: Metrics from platform APIs
            
        Returns:
            Performance analysis with insights
        """
        try:
            # Extract platform and content type from metrics
            platform = platform_metrics.get('platform', 'unknown')
            content_type = platform_metrics.get('content_type', 'post')
            
            # Track performance
            performance_metrics = await self.performance_tracker.track_content_performance(
                content_id, content_type, platform, platform_metrics
            )
            
            # Generate insights
            insights = await self.performance_tracker.generate_insights([content_id])
            
            # Get performance summary
            summary = await self.performance_tracker.get_performance_summary([content_id])
            
            return {
                'content_id': content_id,
                'performance_metrics': asdict(performance_metrics),
                'insights': [asdict(insight) for insight in insights],
                'summary': summary,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {str(e)}")
            return {
                'content_id': content_id,
                'status': 'failed',
                'error': str(e)
            }
    
    async def get_content_recommendations(
        self,
        content_type: str,
        target_audience: Optional[str] = None,
        platform: Optional[str] = None,
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get content recommendations based on performance data and best practices.
        
        Args:
            content_type: Type of content
            target_audience: Target audience
            platform: Target platform
            performance_data: Historical performance data
            
        Returns:
            Content recommendations
        """
        try:
            recommendations = {
                'content_type': content_type,
                'target_audience': target_audience,
                'platform': platform,
                'recommendations': [],
                'best_practices': [],
                'template_suggestions': [],
                'optimization_tips': []
            }
            
            # Get platform-specific recommendations
            if platform:
                platform_recommendations = await self._get_platform_recommendations(
                    platform, content_type
                )
                recommendations['recommendations'].extend(platform_recommendations)
            
            # Get content type best practices
            best_practices = await self._get_content_best_practices(content_type)
            recommendations['best_practices'] = best_practices
            
            # Get template suggestions
            if platform in ['instagram', 'twitter', 'linkedin']:
                template_suggestions = self.social_templates.get_available_templates(platform)
                recommendations['template_suggestions'] = template_suggestions
            elif content_type == 'blog':
                template_suggestions = self.blog_templates.get_all_categories()
                recommendations['template_suggestions'] = template_suggestions
            
            # Analyze performance data for insights
            if performance_data:
                performance_recommendations = await self._analyze_performance_for_recommendations(
                    performance_data, content_type, platform
                )
                recommendations['optimization_tips'] = performance_recommendations
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {str(e)}")
            return {
                'content_type': content_type,
                'error': str(e),
                'recommendations': []
            }
    
    def _determine_workflow(self, content_type: str) -> str:
        """Determine workflow based on content type"""
        workflow_mapping = {
            'instagram_post': 'social_media',
            'twitter_post': 'social_media', 
            'linkedin_post': 'social_media',
            'tiktok_caption': 'social_media',
            'blog_post': 'blog_post',
            'article': 'blog_post',
            'email_marketing': 'marketing_email',
            'newsletter': 'marketing_email',
            'product_description': 'product_description',
            'sales_page': 'marketing_email'
        }
        
        return workflow_mapping.get(content_type, 'social_media')
    
    async def _execute_workflow_step(
        self,
        step: str,
        content_type: str,
        request_data: Dict[str, Any],
        current_content: Optional[str]
    ) -> Dict[str, Any]:
        """Execute a specific workflow step"""
        
        if step == 'generate':
            # Use generation manager for initial content creation
            return await self.generation_manager.generate_content(request_data)
            
        elif step == 'enhance_quality':
            # Use quality enhancer
            return await self.quality_enhancer.enhance_content(
                current_content, content_type, request_data
            )
            
        elif step == 'optimize_format':
            # Use format optimizer
            platform = request_data.get('platform', 'general')
            return await self.format_optimizer.optimize_format(
                current_content, platform, request_data
            )
            
        elif step == 'optimize_seo':
            # Use SEO optimizer
            keywords = request_data.get('keywords', [])
            return await self.seo_optimizer.optimize_content(
                current_content, keywords, request_data
            )
            
        elif step == 'track_performance':
            # Initialize performance tracking
            return {
                'tracking_initialized': True,
                'content_id': request_data.get('content_id'),
                'tracking_setup': 'ready'
            }
            
        elif step == 'a_b_test':
            # Set up A/B testing (placeholder)
            return {
                'ab_test_setup': True,
                'variants': ['original', 'optimized']
            }
        
        else:
            raise ValueError(f"Unknown workflow step: {step}")
    
    async def _validate_business_rules(
        self,
        content: str,
        content_type: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate content against business rules"""
        validation = {
            'passed': True,
            'violations': [],
            'warnings': []
        }
        
        # Check content length
        max_length = self.business_rules['max_content_length'].get(content_type, 5000)
        if len(content) > max_length:
            validation['violations'].append(f"Content exceeds maximum length ({max_length} chars)")
            validation['passed'] = False
        
        # Check quality score
        if 'enhance_quality_result' in result:
            quality_data = result['enhance_quality_result']
            if 'enhanced_quality' in quality_data:
                overall_score = quality_data['enhanced_quality'].get('overall_score', 0)
                if overall_score < self.business_rules['min_quality_score']:
                    validation['violations'].append(f"Quality score too low: {overall_score:.2f}")
                    validation['passed'] = False
        
        # Check SEO score
        if 'optimize_seo_result' in result:
            seo_score = result['optimize_seo_result'].get('seo_score', 0)
            if seo_score < self.business_rules['required_seo_score']:
                validation['warnings'].append(f"SEO score below recommended: {seo_score:.2f}")
        
        return validation
    
    async def _get_platform_recommendations(
        self,
        platform: str,
        content_type: str
    ) -> List[str]:
        """Get platform-specific recommendations"""
        recommendations = {
            'instagram': [
                "Use high-quality visuals",
                "Include relevant hashtags (5-30)",
                "Post during peak hours (6-9 PM)",
                "Use Instagram Stories for behind-the-scenes content",
                "Maintain consistent aesthetic"
            ],
            'twitter': [
                "Keep posts under 280 characters",
                "Use 1-2 relevant hashtags",
                "Engage with trending topics",
                "Post 3-5 times daily",
                "Use threads for longer content"
            ],
            'linkedin': [
                "Focus on professional value",
                "Share industry insights",
                "Use professional tone",
                "Include relevant business hashtags",
                "Post during business hours"
            ],
            'tiktok': [
                "Create engaging first 3 seconds",
                "Use trending sounds and effects",
                "Keep videos under 60 seconds",
                "Post 1-3 times daily",
                "Participate in challenges"
            ]
        }
        
        return recommendations.get(platform, [])
    
    async def _get_content_best_practices(self, content_type: str) -> List[str]:
        """Get content type best practices"""
        practices = {
            'blog_post': [
                "Use clear headings and subheadings",
                "Include actionable tips",
                "Add relevant images",
                "Write compelling meta descriptions",
                "Use internal and external links"
            ],
            'social_post': [
                "Start with a strong hook",
                "Include a call-to-action",
                "Use platform-appropriate hashtags",
                "Post at optimal times",
                "Engage with comments promptly"
            ],
            'email_marketing': [
                "Write compelling subject lines",
                "Personalize content",
                "Include clear call-to-action",
                "Optimize for mobile",
                "Test send times"
            ]
        }
        
        return practices.get(content_type, [])
    
    async def _analyze_performance_for_recommendations(
        self,
        performance_data: Dict[str, Any],
        content_type: str,
        platform: Optional[str]
    ) -> List[str]:
        """Analyze performance data to generate optimization tips"""
        tips = []
        
        # Analyze engagement rate
        engagement_rate = performance_data.get('engagement_rate', 0)
        if engagement_rate < 0.02:  # Less than 2%
            tips.append("Engagement is low - try adding more questions and calls-to-action")
            tips.append("Consider posting at different times to reach your audience")
        
        # Analyze reach
        reach = performance_data.get('reach', 0)
        impressions = performance_data.get('impressions', 0)
        
        if reach > 0 and impressions > 0:
            reach_rate = reach / impressions
            if reach_rate < 0.1:  # Less than 10%
                tips.append("Low reach rate - consider using more relevant hashtags")
        
        # Platform-specific analysis
        if platform == 'instagram':
            saves = performance_data.get('saves', 0)
            if saves == 0:
                tips.append("No saves detected - create more valuable, reference-worthy content")
        
        elif platform == 'twitter':
            retweets = performance_data.get('retweets', 0)
            if retweets == 0:
                tips.append("No retweets - make content more shareable with quotes or insights")
        
        return tips
