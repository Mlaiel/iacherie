"""
Mobile SEO Optimizer for Ainflue Platform
Advanced mobile-first SEO optimization and mobile search optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Tuple, Union, Set
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class MobileOptimizationIssue:
    """Mobile optimization issue representation"""
    issue_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    recommendation: str
    affected_elements: List[str] = field(default_factory=list)
    impact_score: float = 0.0


@dataclass
class MobileMetrics:
    """Mobile performance metrics"""
    mobile_friendly_score: float
    mobile_speed_score: float
    mobile_usability_score: float
    viewport_configuration: bool
    touch_optimization: float
    mobile_core_web_vitals: Dict[str, float]


@dataclass
class MobileOptimizationReport:
    """Comprehensive mobile optimization report"""
    url: str
    overall_score: float
    metrics: MobileMetrics
    issues: List[MobileOptimizationIssue]
    recommendations: List[str]
    mobile_vs_desktop_comparison: Dict[str, float]


class MobileSEOOptimizer:
    """
    Advanced mobile SEO optimization engine
    Provides mobile-first indexing optimization and mobile user experience improvements
    """
    
    def __init__(self):
        self.mobile_ranking_factors = self._initialize_mobile_ranking_factors()
        self.viewport_configurations = self._load_viewport_configurations()
        self.touch_target_guidelines = self._load_touch_guidelines()
        self.mobile_content_guidelines = self._load_content_guidelines()
        
    def _initialize_mobile_ranking_factors(self) -> Dict[str, float]:
        """Initialize mobile-specific ranking factors with weights"""
        return {
            # Core mobile factors
            'mobile_friendliness': 0.25,
            'page_loading_speed': 0.20,
            'core_web_vitals_mobile': 0.15,
            'viewport_configuration': 0.10,
            'touch_optimization': 0.08,
            'mobile_content_readability': 0.07,
            'mobile_navigation': 0.05,
            'mobile_search_features': 0.05,
            'amp_implementation': 0.03,
            'progressive_web_app': 0.02
        }
        
    def _load_viewport_configurations(self) -> Dict[str, Dict]:
        """Load optimal viewport configurations for different content types"""
        return {
            'default': {
                'width': 'device-width',
                'initial_scale': 1.0,
                'minimum_scale': 1.0,
                'maximum_scale': 5.0,
                'user_scalable': True
            },
            'photography': {
                'width': 'device-width',
                'initial_scale': 1.0,
                'minimum_scale': 0.5,
                'maximum_scale': 10.0,
                'user_scalable': True
            },
            'video': {
                'width': 'device-width',
                'initial_scale': 1.0,
                'minimum_scale': 1.0,
                'maximum_scale': 3.0,
                'user_scalable': True
            },
            'audio': {
                'width': 'device-width',
                'initial_scale': 1.0,
                'minimum_scale': 1.0,
                'maximum_scale': 2.0,
                'user_scalable': True
            }
        }
        
    def _load_touch_guidelines(self) -> Dict[str, Union[int, float]]:
        """Load touch target size and spacing guidelines"""
        return {
            'minimum_touch_target_size': 44,  # pixels
            'recommended_touch_target_size': 48,  # pixels
            'minimum_spacing': 8,  # pixels between touch targets
            'recommended_spacing': 16,  # pixels between touch targets
            'thumb_zone_height': 160,  # pixels from bottom
            'comfortable_reach_width': 320  # pixels from edges
        }
        
    def _load_content_guidelines(self) -> Dict[str, Union[str, int, float]]:
        """Load mobile content optimization guidelines"""
        return {
            'max_line_length': 50,  # characters per line
            'optimal_font_size': 16,  # pixels
            'minimum_font_size': 14,  # pixels
            'line_height_ratio': 1.4,  # ratio to font size
            'paragraph_spacing': 1.5,  # em units
            'heading_hierarchy': True,
            'max_tap_targets_per_screen': 7
        }
        
    def analyze_mobile_optimization(self, page_data: Dict, content_type: str = None) -> MobileOptimizationReport:
        """Comprehensive mobile optimization analysis"""
        
        # Extract mobile metrics
        metrics = self._extract_mobile_metrics(page_data)
        
        # Identify optimization issues
        issues = self._identify_mobile_issues(page_data, content_type)
        
        # Calculate overall mobile score
        overall_score = self._calculate_mobile_score(metrics, issues)
        
        # Generate recommendations
        recommendations = self._generate_mobile_recommendations(issues, metrics, content_type)
        
        # Compare mobile vs desktop performance
        comparison = self._compare_mobile_vs_desktop(page_data)
        
        return MobileOptimizationReport(
            url=page_data.get('url', ''),
            overall_score=overall_score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            mobile_vs_desktop_comparison=comparison
        )
        
    def _extract_mobile_metrics(self, page_data: Dict) -> MobileMetrics:
        """Extract mobile-specific performance metrics"""
        
        # Mobile friendliness
        mobile_friendly = page_data.get('mobile_friendly', False)
        mobile_friendly_score = 100 if mobile_friendly else 0
        
        # Mobile speed metrics
        mobile_speed = page_data.get('mobile_page_speed', {})
        mobile_speed_score = self._calculate_mobile_speed_score(mobile_speed)
        
        # Mobile usability
        usability_score = self._calculate_mobile_usability_score(page_data)
        
        # Viewport configuration
        viewport_meta = page_data.get('viewport_meta', '')
        viewport_configured = self._check_viewport_configuration(viewport_meta)
        
        # Touch optimization
        touch_score = self._calculate_touch_optimization_score(page_data)
        
        # Mobile Core Web Vitals
        mobile_cwv = self._extract_mobile_core_web_vitals(page_data)
        
        return MobileMetrics(
            mobile_friendly_score=mobile_friendly_score,
            mobile_speed_score=mobile_speed_score,
            mobile_usability_score=usability_score,
            viewport_configuration=viewport_configured,
            touch_optimization=touch_score,
            mobile_core_web_vitals=mobile_cwv
        )
        
    def _identify_mobile_issues(self, page_data: Dict, content_type: str = None) -> List[MobileOptimizationIssue]:
        """Identify mobile optimization issues"""
        
        issues = []
        
        # Check viewport configuration
        viewport_issues = self._check_viewport_issues(page_data, content_type)
        issues.extend(viewport_issues)
        
        # Check touch target optimization
        touch_issues = self._check_touch_target_issues(page_data)
        issues.extend(touch_issues)
        
        # Check mobile speed issues
        speed_issues = self._check_mobile_speed_issues(page_data)
        issues.extend(speed_issues)
        
        # Check content readability issues
        readability_issues = self._check_mobile_readability_issues(page_data)
        issues.extend(readability_issues)
        
        # Check mobile navigation issues
        navigation_issues = self._check_mobile_navigation_issues(page_data)
        issues.extend(navigation_issues)
        
        # Check Core Web Vitals issues
        cwv_issues = self._check_mobile_cwv_issues(page_data)
        issues.extend(cwv_issues)
        
        # Platform-specific issues
        if content_type:
            platform_issues = self._check_platform_specific_issues(page_data, content_type)
            issues.extend(platform_issues)
            
        return sorted(issues, key=lambda x: x.impact_score, reverse=True)
        
    def _check_viewport_issues(self, page_data: Dict, content_type: str = None) -> List[MobileOptimizationIssue]:
        """Check viewport configuration issues"""
        
        issues = []
        viewport_meta = page_data.get('viewport_meta', '')
        
        if not viewport_meta:
            issues.append(MobileOptimizationIssue(
                issue_type='viewport_missing',
                severity='critical',
                description='No viewport meta tag found',
                recommendation='Add viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1.0">',
                impact_score=9.0
            ))
        else:
            # Check specific viewport configurations
            optimal_config = self.viewport_configurations.get(content_type, self.viewport_configurations['default'])
            
            if 'width=device-width' not in viewport_meta:
                issues.append(MobileOptimizationIssue(
                    issue_type='viewport_width',
                    severity='high',
                    description='Viewport width not set to device-width',
                    recommendation='Set viewport width to device-width for responsive design',
                    impact_score=8.0
                ))
                
            if 'initial-scale=1' not in viewport_meta:
                issues.append(MobileOptimizationIssue(
                    issue_type='viewport_scale',
                    severity='medium',
                    description='Initial scale not set to 1.0',
                    recommendation='Set initial-scale=1.0 for proper mobile rendering',
                    impact_score=6.0
                ))
                
            if 'user-scalable=no' in viewport_meta:
                issues.append(MobileOptimizationIssue(
                    issue_type='viewport_scalable',
                    severity='medium',
                    description='User scaling disabled',
                    recommendation='Allow user scaling for accessibility (remove user-scalable=no)',
                    impact_score=5.0
                ))
                
        return issues
        
    def _check_touch_target_issues(self, page_data: Dict) -> List[MobileOptimizationIssue]:
        """Check touch target optimization issues"""
        
        issues = []
        touch_targets = page_data.get('touch_targets', [])
        
        if not touch_targets:
            issues.append(MobileOptimizationIssue(
                issue_type='touch_targets_not_analyzed',
                severity='low',
                description='Touch targets not analyzed',
                recommendation='Analyze touch target sizes and spacing for mobile optimization',
                impact_score=3.0
            ))
            return issues
            
        guidelines = self.touch_target_guidelines
        small_targets = []
        close_targets = []
        
        for target in touch_targets:
            # Check size
            width = target.get('width', 0)
            height = target.get('height', 0)
            min_dimension = min(width, height)
            
            if min_dimension < guidelines['minimum_touch_target_size']:
                small_targets.append(target.get('selector', 'unknown'))
                
            # Check spacing (simplified)
            spacing = target.get('spacing', 0)
            if spacing < guidelines['minimum_spacing']:
                close_targets.append(target.get('selector', 'unknown'))
                
        if small_targets:
            issues.append(MobileOptimizationIssue(
                issue_type='small_touch_targets',
                severity='high',
                description=f'{len(small_targets)} touch targets are too small',
                recommendation=f'Increase touch target size to at least {guidelines["minimum_touch_target_size"]}px',
                affected_elements=small_targets,
                impact_score=7.5
            ))
            
        if close_targets:
            issues.append(MobileOptimizationIssue(
                issue_type='close_touch_targets',
                severity='medium',
                description=f'{len(close_targets)} touch targets are too close together',
                recommendation=f'Add at least {guidelines["minimum_spacing"]}px spacing between touch targets',
                affected_elements=close_targets,
                impact_score=6.0
            ))
            
        return issues
        
    def _check_mobile_speed_issues(self, page_data: Dict) -> List[MobileOptimizationIssue]:
        """Check mobile speed optimization issues"""
        
        issues = []
        mobile_speed = page_data.get('mobile_page_speed', {})
        
        # Page load time
        load_time = mobile_speed.get('load_time', 5.0)
        if load_time > 3.0:
            severity = 'critical' if load_time > 5.0 else 'high'
            issues.append(MobileOptimizationIssue(
                issue_type='slow_mobile_loading',
                severity=severity,
                description=f'Mobile page load time is {load_time:.1f} seconds',
                recommendation='Optimize mobile loading speed to under 3 seconds',
                impact_score=8.5
            ))
            
        # First Contentful Paint
        fcp = mobile_speed.get('first_contentful_paint', 3.0)
        if fcp > 1.8:
            issues.append(MobileOptimizationIssue(
                issue_type='slow_fcp_mobile',
                severity='high',
                description=f'Mobile First Contentful Paint is {fcp:.1f} seconds',
                recommendation='Optimize FCP to under 1.8 seconds on mobile',
                impact_score=7.0
            ))
            
        # Mobile-specific optimizations
        has_amp = page_data.get('amp_version', False)
        is_pwa = page_data.get('progressive_web_app', False)
        
        if not has_amp and not is_pwa:
            issues.append(MobileOptimizationIssue(
                issue_type='no_mobile_acceleration',
                severity='medium',
                description='No mobile acceleration technologies implemented',
                recommendation='Consider implementing AMP or PWA for faster mobile experience',
                impact_score=5.0
            ))
            
        return issues
        
    def _check_mobile_readability_issues(self, page_data: Dict) -> List[MobileOptimizationIssue]:
        """Check mobile content readability issues"""
        
        issues = []
        content_analysis = page_data.get('mobile_content_analysis', {})
        
        # Font size
        min_font_size = content_analysis.get('minimum_font_size', 16)
        if min_font_size < 14:
            issues.append(MobileOptimizationIssue(
                issue_type='small_mobile_fonts',
                severity='high',
                description=f'Minimum font size is {min_font_size}px',
                recommendation='Use minimum 14px font size for mobile readability',
                impact_score=7.0
            ))
            
        # Line length
        max_line_length = content_analysis.get('max_line_length', 50)
        if max_line_length > 60:
            issues.append(MobileOptimizationIssue(
                issue_type='long_mobile_lines',
                severity='medium',
                description=f'Maximum line length is {max_line_length} characters',
                recommendation='Limit line length to 50-60 characters on mobile',
                impact_score=5.0
            ))
            
        # Text contrast
        contrast_ratio = content_analysis.get('text_contrast_ratio', 4.5)
        if contrast_ratio < 4.5:
            issues.append(MobileOptimizationIssue(
                issue_type='poor_mobile_contrast',
                severity='high',
                description=f'Text contrast ratio is {contrast_ratio:.1f}:1',
                recommendation='Ensure text contrast ratio is at least 4.5:1 for mobile readability',
                impact_score=6.5
            ))
            
        return issues
        
    def _check_mobile_navigation_issues(self, page_data: Dict) -> List[MobileOptimizationIssue]:
        """Check mobile navigation optimization issues"""
        
        issues = []
        navigation = page_data.get('mobile_navigation', {})
        
        # Navigation type
        nav_type = navigation.get('type', 'unknown')
        if nav_type not in ['hamburger', 'bottom_tabs', 'swipe']:
            issues.append(MobileOptimizationIssue(
                issue_type='non_mobile_navigation',
                severity='medium',
                description='Navigation not optimized for mobile',
                recommendation='Implement mobile-friendly navigation (hamburger menu, bottom tabs)',
                impact_score=6.0
            ))
            
        # Navigation item count
        nav_items = navigation.get('item_count', 0)
        if nav_items > 7:
            issues.append(MobileOptimizationIssue(
                issue_type='too_many_nav_items',
                severity='medium',
                description=f'Navigation has {nav_items} items',
                recommendation='Limit navigation items to 7 or fewer on mobile',
                impact_score=5.0
            ))
            
        # Search functionality
        has_mobile_search = navigation.get('mobile_search', False)
        if not has_mobile_search:
            issues.append(MobileOptimizationIssue(
                issue_type='no_mobile_search',
                severity='low',
                description='No mobile-optimized search functionality',
                recommendation='Add mobile-friendly search interface',
                impact_score=4.0
            ))
            
        return issues
        
    def _check_mobile_cwv_issues(self, page_data: Dict) -> List[MobileOptimizationIssue]:
        """Check mobile Core Web Vitals issues"""
        
        issues = []
        mobile_cwv = page_data.get('mobile_core_web_vitals', {})
        
        # Largest Contentful Paint (Mobile)
        lcp = mobile_cwv.get('largest_contentful_paint', 3.0)
        if lcp > 2.5:
            severity = 'critical' if lcp > 4.0 else 'high'
            issues.append(MobileOptimizationIssue(
                issue_type='poor_mobile_lcp',
                severity=severity,
                description=f'Mobile LCP is {lcp:.1f} seconds',
                recommendation='Optimize mobile LCP to under 2.5 seconds',
                impact_score=8.0
            ))
            
        # First Input Delay (Mobile)
        fid = mobile_cwv.get('first_input_delay', 150)
        if fid > 100:
            issues.append(MobileOptimizationIssue(
                issue_type='poor_mobile_fid',
                severity='high',
                description=f'Mobile FID is {fid}ms',
                recommendation='Optimize mobile FID to under 100ms',
                impact_score=7.0
            ))
            
        # Cumulative Layout Shift (Mobile)
        cls = mobile_cwv.get('cumulative_layout_shift', 0.1)
        if cls > 0.1:
            issues.append(MobileOptimizationIssue(
                issue_type='poor_mobile_cls',
                severity='medium',
                description=f'Mobile CLS is {cls:.2f}',
                recommendation='Optimize mobile CLS to under 0.1',
                impact_score=6.0
            ))
            
        return issues
        
    def _check_platform_specific_issues(self, page_data: Dict, content_type: str) -> List[MobileOptimizationIssue]:
        """Check platform-specific mobile optimization issues"""
        
        issues = []
        
        if content_type == 'music':
            # Audio player mobile optimization
            audio_player = page_data.get('audio_player', {})
            if not audio_player.get('mobile_optimized', False):
                issues.append(MobileOptimizationIssue(
                    issue_type='audio_player_not_mobile_optimized',
                    severity='medium',
                    description='Audio player not optimized for mobile',
                    recommendation='Implement mobile-friendly audio controls and interface',
                    impact_score=6.0
                ))
                
        elif content_type == 'photography':
            # Image gallery mobile optimization
            gallery = page_data.get('image_gallery', {})
            if not gallery.get('mobile_swipe', False):
                issues.append(MobileOptimizationIssue(
                    issue_type='gallery_no_mobile_swipe',
                    severity='medium',
                    description='Image gallery lacks mobile swipe navigation',
                    recommendation='Add swipe navigation for mobile image galleries',
                    impact_score=5.5
                ))
                
            # Image loading optimization
            if not gallery.get('lazy_loading', False):
                issues.append(MobileOptimizationIssue(
                    issue_type='no_mobile_image_lazy_loading',
                    severity='high',
                    description='Images not using lazy loading on mobile',
                    recommendation='Implement lazy loading for mobile image optimization',
                    impact_score=7.5
                ))
                
        elif content_type == 'video':
            # Video player mobile optimization
            video_player = page_data.get('video_player', {})
            if not video_player.get('mobile_controls', False):
                issues.append(MobileOptimizationIssue(
                    issue_type='video_player_mobile_controls',
                    severity='high',
                    description='Video player lacks mobile-optimized controls',
                    recommendation='Implement touch-friendly video controls for mobile',
                    impact_score=7.0
                ))
                
        return issues
        
    def _calculate_mobile_score(self, metrics: MobileMetrics, issues: List[MobileOptimizationIssue]) -> float:
        """Calculate overall mobile optimization score"""
        
        # Base score from metrics
        base_score = (
            metrics.mobile_friendly_score * 0.3 +
            metrics.mobile_speed_score * 0.25 +
            metrics.mobile_usability_score * 0.2 +
            (100 if metrics.viewport_configuration else 0) * 0.1 +
            metrics.touch_optimization * 0.15
        )
        
        # Penalty for issues
        issue_penalty = 0
        for issue in issues:
            if issue.severity == 'critical':
                issue_penalty += 15
            elif issue.severity == 'high':
                issue_penalty += 10
            elif issue.severity == 'medium':
                issue_penalty += 5
            elif issue.severity == 'low':
                issue_penalty += 2
                
        final_score = max(0, base_score - issue_penalty)
        return round(final_score, 1)
        
    def _generate_mobile_recommendations(self, issues: List[MobileOptimizationIssue], 
                                       metrics: MobileMetrics, content_type: str = None) -> List[str]:
        """Generate mobile optimization recommendations"""
        
        recommendations = []
        
        # Priority recommendations based on issues
        critical_issues = [issue for issue in issues if issue.severity == 'critical']
        high_issues = [issue for issue in issues if issue.severity == 'high']
        
        if critical_issues:
            recommendations.append("CRITICAL: Address viewport and mobile friendliness issues immediately")
            
        if high_issues:
            recommendations.append("HIGH PRIORITY: Optimize mobile speed and touch targets")
            
        # Specific recommendations
        if metrics.mobile_speed_score < 70:
            recommendations.append("Implement mobile speed optimizations (image compression, minification, caching)")
            
        if metrics.touch_optimization < 70:
            recommendations.append("Improve touch target sizes and spacing for better mobile usability")
            
        if not metrics.viewport_configuration:
            recommendations.append("Add proper viewport meta tag for responsive design")
            
        # Core Web Vitals recommendations
        cwv_scores = list(metrics.mobile_core_web_vitals.values())
        if cwv_scores and any(score > 2.5 for score in cwv_scores):
            recommendations.append("Optimize mobile Core Web Vitals (LCP, FID, CLS)")
            
        # Content-type specific recommendations
        if content_type == 'music':
            recommendations.append("Optimize audio player for mobile touch controls and streaming")
        elif content_type == 'photography':
            recommendations.append("Implement mobile-optimized image gallery with swipe navigation")
        elif content_type == 'video':
            recommendations.append("Add mobile-friendly video controls and adaptive streaming")
            
        # General mobile SEO recommendations
        recommendations.extend([
            "Ensure mobile-first content strategy with concise, scannable text",
            "Implement structured data for mobile rich snippets",
            "Optimize for local mobile search if applicable",
            "Consider AMP or PWA implementation for enhanced mobile performance"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
        
    def _compare_mobile_vs_desktop(self, page_data: Dict) -> Dict[str, float]:
        """Compare mobile vs desktop performance"""
        
        mobile_metrics = page_data.get('mobile_metrics', {})
        desktop_metrics = page_data.get('desktop_metrics', {})
        
        comparison = {}
        
        # Speed comparison
        mobile_speed = mobile_metrics.get('page_speed', 5.0)
        desktop_speed = desktop_metrics.get('page_speed', 3.0)
        comparison['speed_ratio'] = mobile_speed / desktop_speed if desktop_speed > 0 else 1.0
        
        # Core Web Vitals comparison
        mobile_lcp = mobile_metrics.get('lcp', 3.0)
        desktop_lcp = desktop_metrics.get('lcp', 2.0)
        comparison['lcp_ratio'] = mobile_lcp / desktop_lcp if desktop_lcp > 0 else 1.0
        
        # User engagement comparison
        mobile_bounce = mobile_metrics.get('bounce_rate', 0.6)
        desktop_bounce = desktop_metrics.get('bounce_rate', 0.4)
        comparison['bounce_rate_ratio'] = mobile_bounce / desktop_bounce if desktop_bounce > 0 else 1.0
        
        return comparison
        
    # Utility calculation methods
    def _calculate_mobile_speed_score(self, mobile_speed: Dict) -> float:
        """Calculate mobile speed score"""
        load_time = mobile_speed.get('load_time', 5.0)
        fcp = mobile_speed.get('first_contentful_paint', 3.0)
        
        # Score based on Google's mobile speed guidelines
        load_score = max(0, 100 - (load_time - 1) * 25)
        fcp_score = max(0, 100 - (fcp - 1) * 40)
        
        return (load_score + fcp_score) / 2
        
    def _calculate_mobile_usability_score(self, page_data: Dict) -> float:
        """Calculate mobile usability score"""
        usability_factors = page_data.get('mobile_usability', {})
        
        score = 0
        max_score = 0
        
        # Text readability
        if 'text_readable' in usability_factors:
            score += 25 if usability_factors['text_readable'] else 0
        max_score += 25
        
        # Touch targets
        if 'touch_targets_appropriate' in usability_factors:
            score += 25 if usability_factors['touch_targets_appropriate'] else 0
        max_score += 25
        
        # Content sizing
        if 'content_sized_to_viewport' in usability_factors:
            score += 25 if usability_factors['content_sized_to_viewport'] else 0
        max_score += 25
        
        # Navigation
        if 'mobile_navigation' in usability_factors:
            score += 25 if usability_factors['mobile_navigation'] else 0
        max_score += 25
        
        return (score / max_score) * 100 if max_score > 0 else 50
        
    def _check_viewport_configuration(self, viewport_meta: str) -> bool:
        """Check if viewport is properly configured"""
        if not viewport_meta:
            return False
            
        required_elements = ['width=device-width', 'initial-scale=1']
        return all(element in viewport_meta for element in required_elements)
        
    def _calculate_touch_optimization_score(self, page_data: Dict) -> float:
        """Calculate touch optimization score"""
        touch_data = page_data.get('touch_analysis', {})
        
        if not touch_data:
            return 50  # Neutral score if no data
            
        # Touch target size compliance
        adequate_size_ratio = touch_data.get('adequate_size_ratio', 0.5)
        
        # Touch target spacing compliance
        adequate_spacing_ratio = touch_data.get('adequate_spacing_ratio', 0.5)
        
        # Thumb-friendly placement
        thumb_friendly_ratio = touch_data.get('thumb_friendly_ratio', 0.5)
        
        score = (adequate_size_ratio * 40 + adequate_spacing_ratio * 30 + thumb_friendly_ratio * 30)
        
        return min(100, score * 100)
        
    def _extract_mobile_core_web_vitals(self, page_data: Dict) -> Dict[str, float]:
        """Extract mobile Core Web Vitals"""
        mobile_cwv = page_data.get('mobile_core_web_vitals', {})
        
        return {
            'largest_contentful_paint': mobile_cwv.get('lcp', 3.0),
            'first_input_delay': mobile_cwv.get('fid', 150),
            'cumulative_layout_shift': mobile_cwv.get('cls', 0.1)
        }
        
    def optimize_for_mobile_first_indexing(self, page_data: Dict) -> Dict[str, Union[str, List[str]]]:
        """Generate mobile-first indexing optimization recommendations"""
        
        optimization_plan = {
            'content_strategy': [],
            'technical_optimizations': [],
            'user_experience': [],
            'structured_data': []
        }
        
        # Content strategy for mobile-first
        optimization_plan['content_strategy'].extend([
            "Create concise, scannable content with clear headings",
            "Place most important content above the fold on mobile",
            "Use bullet points and short paragraphs for mobile readability",
            "Optimize images with proper alt text and mobile dimensions"
        ])
        
        # Technical optimizations
        optimization_plan['technical_optimizations'].extend([
            "Ensure mobile and desktop content parity for indexing",
            "Implement responsive design with mobile-first CSS",
            "Optimize mobile page speed and Core Web Vitals",
            "Use proper viewport meta tag configuration"
        ])
        
        # User experience improvements
        optimization_plan['user_experience'].extend([
            "Design touch-friendly navigation and buttons",
            "Implement mobile-specific features (swipe, pull-to-refresh)",
            "Ensure fast mobile loading with progressive enhancement",
            "Add mobile-specific call-to-action placements"
        ])
        
        # Structured data optimization
        optimization_plan['structured_data'].extend([
            "Implement mobile-specific structured data markup",
            "Use JSON-LD for better mobile page performance",
            "Add relevant schema.org markup for content type",
            "Ensure structured data consistency across devices"
        ])
        
        return optimization_plan


# Integration utilities
def create_ainflue_mobile_seo_optimizer() -> MobileSEOOptimizer:
    """Create configured mobile SEO optimizer for Ainflue"""
    return MobileSEOOptimizer()


if __name__ == "__main__":
    # Example usage
    optimizer = create_ainflue_mobile_seo_optimizer()
    
    # Sample page data
    page_data = {
        'url': 'https://ainflue.com/creator/musician-profile',
        'mobile_friendly': True,
        'viewport_meta': 'width=device-width, initial-scale=1.0',
        'mobile_page_speed': {
            'load_time': 3.5,
            'first_contentful_paint': 2.1
        },
        'mobile_core_web_vitals': {
            'lcp': 2.8,
            'fid': 120,
            'cls': 0.12
        },
        'touch_targets': [
            {'selector': '.play-button', 'width': 40, 'height': 40, 'spacing': 5},
            {'selector': '.nav-item', 'width': 48, 'height': 48, 'spacing': 12}
        ],
        'mobile_usability': {
            'text_readable': True,
            'touch_targets_appropriate': False,
            'content_sized_to_viewport': True,
            'mobile_navigation': True
        }
    }
    
    # Analyze mobile optimization
    report = optimizer.analyze_mobile_optimization(page_data, 'music')
    
    print(f"Mobile Optimization Report for {report.url}")
    print(f"Overall Score: {report.overall_score}/100")
    print(f"Mobile Friendly Score: {report.metrics.mobile_friendly_score}/100")
    print(f"Mobile Speed Score: {report.metrics.mobile_speed_score}/100")
    print(f"Touch Optimization: {report.metrics.touch_optimization}/100")
    
    print("\nCritical Issues:")
    critical_issues = [issue for issue in report.issues if issue.severity == 'critical']
    for issue in critical_issues:
        print(f"- {issue.description}")
        print(f"  Recommendation: {issue.recommendation}")
        
    print("\nTop Recommendations:")
    for i, rec in enumerate(report.recommendations[:5], 1):
        print(f"{i}. {rec}")
        
    # Mobile-first optimization plan
    optimization_plan = optimizer.optimize_for_mobile_first_indexing(page_data)
    print("\nMobile-First Optimization Plan:")
    for category, recommendations in optimization_plan.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for rec in recommendations[:3]:
            print(f"- {rec}")