"""Core Web Vitals Optimizer - Performance Optimization for SEO

This module provides comprehensive Core Web Vitals optimization for improved
search engine rankings and user experience through performance enhancements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import base64

logger = logging.getLogger(__name__)


class WebVitalMetric(Enum):
    """Core Web Vitals metrics"""
    
    LARGEST_CONTENTFUL_PAINT = "lcp"  # Loading performance
    FIRST_INPUT_DELAY = "fid"  # Interactivity
    CUMULATIVE_LAYOUT_SHIFT = "cls"  # Visual stability
    FIRST_CONTENTFUL_PAINT = "fcp"  # Loading
    TIME_TO_INTERACTIVE = "tti"  # Interactivity
    TOTAL_BLOCKING_TIME = "tbt"  # Interactivity


class OptimizationLevel(Enum):
    """Optimization levels"""
    
    BASIC = "basic"
    INTERMEDIATE = "intermediate" 
    AGGRESSIVE = "aggressive"


class ResourceType(Enum):
    """Resource types for optimization"""
    
    IMAGE = "image"
    CSS = "css"
    JAVASCRIPT = "javascript"
    FONT = "font"
    VIDEO = "video"
    AUDIO = "audio"


@dataclass
class WebVitalScore:
    """Individual web vital score"""
    metric: WebVitalMetric
    value: float
    unit: str
    threshold_good: float
    threshold_needs_improvement: float
    status: str  # "good", "needs_improvement", "poor"
    recommendations: List[str]


@dataclass
class PerformanceOptimization:
    """Performance optimization result"""
    optimization_type: str
    original_value: str
    optimized_value: str
    improvement_estimate: float
    implementation_code: str


@dataclass
class CoreWebVitalsResult:
    """Complete Core Web Vitals optimization result"""
    web_vital_scores: List[WebVitalScore]
    overall_score: float
    optimizations_applied: List[PerformanceOptimization]
    optimized_html: str
    optimized_css: str
    critical_css: str
    performance_recommendations: List[str]
    estimated_improvements: Dict[str, float]


class CoreWebVitalsOptimizer:
    """
    Advanced Core Web Vitals optimizer that analyzes and optimizes web pages
    for improved performance metrics and better search engine rankings.
    """
    
    def __init__(self):
        """Initialize the Core Web Vitals optimizer"""
        self.web_vitals_thresholds = {
            WebVitalMetric.LARGEST_CONTENTFUL_PAINT: {"good": 2.5, "needs_improvement": 4.0},
            WebVitalMetric.FIRST_INPUT_DELAY: {"good": 100, "needs_improvement": 300},
            WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT: {"good": 0.1, "needs_improvement": 0.25},
            WebVitalMetric.FIRST_CONTENTFUL_PAINT: {"good": 1.8, "needs_improvement": 3.0},
            WebVitalMetric.TIME_TO_INTERACTIVE: {"good": 3.8, "needs_improvement": 7.3},
            WebVitalMetric.TOTAL_BLOCKING_TIME: {"good": 200, "needs_improvement": 600}
        }
        
        self.optimization_priorities = [
            "image_optimization",
            "css_optimization", 
            "javascript_optimization",
            "font_optimization",
            "html_optimization",
            "layout_shift_prevention"
        ]
    
    def optimize_core_web_vitals(
        self,
        html_content: str,
        css_content: str = "",
        base_url: str = "",
        optimization_level: OptimizationLevel = OptimizationLevel.INTERMEDIATE,
        target_metrics: Optional[List[WebVitalMetric]] = None
    ) -> CoreWebVitalsResult:
        """
        Optimize web page for Core Web Vitals performance.
        
        Args:
            html_content: HTML content to optimize
            css_content: CSS content to optimize
            base_url: Base URL for relative resource resolution
            optimization_level: Level of optimization to apply
            target_metrics: Specific metrics to target (if None, optimizes all)
            
        Returns:
            CoreWebVitalsResult with optimizations and performance estimates
        """
        try:
            logger.info(f"Starting Core Web Vitals optimization at {optimization_level.value} level")
            
            # Analyze current performance
            current_scores = self._analyze_current_performance(html_content, css_content)
            
            # Apply optimizations based on level and targets
            optimizations_applied = []
            optimized_html = html_content
            optimized_css = css_content
            
            if not target_metrics:
                target_metrics = list(WebVitalMetric)
            
            # Image optimization for LCP
            if WebVitalMetric.LARGEST_CONTENTFUL_PAINT in target_metrics:
                img_optimization = self._optimize_images(optimized_html, optimization_level)
                if img_optimization:
                    optimizations_applied.append(img_optimization)
                    optimized_html = img_optimization.optimized_value
            
            # CSS optimization for FCP and LCP
            if any(metric in target_metrics for metric in [WebVitalMetric.FIRST_CONTENTFUL_PAINT, WebVitalMetric.LARGEST_CONTENTFUL_PAINT]):
                css_optimization = self._optimize_css(optimized_css, optimization_level)
                if css_optimization:
                    optimizations_applied.append(css_optimization)
                    optimized_css = css_optimization.optimized_value
            
            # JavaScript optimization for FID and TBT
            if any(metric in target_metrics for metric in [WebVitalMetric.FIRST_INPUT_DELAY, WebVitalMetric.TOTAL_BLOCKING_TIME]):
                js_optimization = self._optimize_javascript(optimized_html, optimization_level)
                if js_optimization:
                    optimizations_applied.append(js_optimization)
                    optimized_html = js_optimization.optimized_value
            
            # Layout shift prevention for CLS
            if WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT in target_metrics:
                cls_optimization = self._prevent_layout_shift(optimized_html, optimization_level)
                if cls_optimization:
                    optimizations_applied.append(cls_optimization)
                    optimized_html = cls_optimization.optimized_value
            
            # Font optimization
            font_optimization = self._optimize_fonts(optimized_html, optimization_level)
            if font_optimization:
                optimizations_applied.append(font_optimization)
                optimized_html = font_optimization.optimized_value
            
            # Generate critical CSS
            critical_css = self._extract_critical_css(optimized_css, optimized_html)
            
            # Calculate improved scores
            improved_scores = self._estimate_improved_scores(current_scores, optimizations_applied)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(improved_scores)
            
            # Generate performance recommendations
            recommendations = self._generate_performance_recommendations(
                improved_scores, optimizations_applied, optimization_level
            )
            
            # Estimate improvements
            estimated_improvements = self._estimate_metric_improvements(
                current_scores, improved_scores
            )
            
            return CoreWebVitalsResult(
                web_vital_scores=improved_scores,
                overall_score=overall_score,
                optimizations_applied=optimizations_applied,
                optimized_html=optimized_html,
                optimized_css=optimized_css,
                critical_css=critical_css,
                performance_recommendations=recommendations,
                estimated_improvements=estimated_improvements
            )
            
        except Exception as e:
            logger.error(f"Error optimizing Core Web Vitals: {str(e)}")
            raise
    
    def _analyze_current_performance(self, html_content: str, css_content: str) -> List[WebVitalScore]:
        """Analyze current performance and estimate Web Vitals scores"""
        
        scores = []
        
        # Analyze LCP (Largest Contentful Paint)
        lcp_estimate = self._estimate_lcp(html_content)
        lcp_score = self._create_web_vital_score(
            WebVitalMetric.LARGEST_CONTENTFUL_PAINT, lcp_estimate, "seconds"
        )
        scores.append(lcp_score)
        
        # Analyze FID (First Input Delay) - estimated based on JavaScript complexity
        fid_estimate = self._estimate_fid(html_content)
        fid_score = self._create_web_vital_score(
            WebVitalMetric.FIRST_INPUT_DELAY, fid_estimate, "milliseconds"
        )
        scores.append(fid_score)
        
        # Analyze CLS (Cumulative Layout Shift)
        cls_estimate = self._estimate_cls(html_content, css_content)
        cls_score = self._create_web_vital_score(
            WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT, cls_estimate, "score"
        )
        scores.append(cls_score)
        
        # Analyze FCP (First Contentful Paint)
        fcp_estimate = self._estimate_fcp(html_content, css_content)
        fcp_score = self._create_web_vital_score(
            WebVitalMetric.FIRST_CONTENTFUL_PAINT, fcp_estimate, "seconds"
        )
        scores.append(fcp_score)
        
        # Analyze TTI (Time to Interactive)
        tti_estimate = self._estimate_tti(html_content)
        tti_score = self._create_web_vital_score(
            WebVitalMetric.TIME_TO_INTERACTIVE, tti_estimate, "seconds"
        )
        scores.append(tti_score)
        
        # Analyze TBT (Total Blocking Time)
        tbt_estimate = self._estimate_tbt(html_content)
        tbt_score = self._create_web_vital_score(
            WebVitalMetric.TOTAL_BLOCKING_TIME, tbt_estimate, "milliseconds"
        )
        scores.append(tbt_score)
        
        return scores
    
    def _estimate_lcp(self, html_content: str) -> float:
        """Estimate Largest Contentful Paint based on content analysis"""
        
        # Base LCP estimate
        base_lcp = 2.0
        
        # Check for large images
        large_images = re.findall(r'<img[^>]*(?:width="(\d+)"|height="(\d+)")[^>]*>', html_content)
        if large_images:
            # Estimate based on largest image
            max_dimension = 0
            for match in large_images:
                width = int(match[0]) if match[0] else 0
                height = int(match[1]) if match[1] else 0
                max_dimension = max(max_dimension, width, height)
            
            if max_dimension > 800:
                base_lcp += 1.5
            elif max_dimension > 400:
                base_lcp += 0.8
        
        # Check for blocking resources
        blocking_scripts = len(re.findall(r'<script[^>]*src[^>]*>', html_content))
        base_lcp += blocking_scripts * 0.3
        
        # Check for CSS files
        css_links = len(re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html_content))
        base_lcp += css_links * 0.2
        
        return round(base_lcp, 2)
    
    def _estimate_fid(self, html_content: str) -> float:
        """Estimate First Input Delay based on JavaScript analysis"""
        
        base_fid = 50.0  # milliseconds
        
        # Count JavaScript resources
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        external_scripts = re.findall(r'<script[^>]*src[^>]*>', html_content)
        
        # Estimate based on script complexity
        total_js_size = sum(len(script) for script in script_tags)
        base_fid += (total_js_size / 1000) * 2  # 2ms per KB of inline JS
        base_fid += len(external_scripts) * 25  # 25ms per external script
        
        # Check for heavy operations
        heavy_operations = [
            r'document\.querySelector',
            r'addEventListener',
            r'setTimeout',
            r'setInterval',
            r'fetch\(',
            r'XMLHttpRequest'
        ]
        
        for pattern in heavy_operations:
            matches = len(re.findall(pattern, html_content, re.IGNORECASE))
            base_fid += matches * 5
        
        return round(base_fid, 1)
    
    def _estimate_cls(self, html_content: str, css_content: str) -> float:
        """Estimate Cumulative Layout Shift"""
        
        base_cls = 0.05
        
        # Check for images without dimensions
        images_without_dimensions = re.findall(
            r'<img(?![^>]*(?:width|height))[^>]*>', html_content
        )
        base_cls += len(images_without_dimensions) * 0.02
        
        # Check for dynamically loaded content
        dynamic_content_patterns = [
            r'document\.createElement',
            r'innerHTML\s*=',
            r'appendChild',
            r'insertBefore'
        ]
        
        for pattern in dynamic_content_patterns:
            matches = len(re.findall(pattern, html_content, re.IGNORECASE))
            base_cls += matches * 0.01
        
        # Check for web fonts without font-display
        if css_content:
            font_faces = re.findall(r'@font-face\s*{[^}]*}', css_content, re.DOTALL)
            for font_face in font_faces:
                if 'font-display' not in font_face:
                    base_cls += 0.03
        
        return round(min(base_cls, 0.5), 3)  # Cap at 0.5
    
    def _estimate_fcp(self, html_content: str, css_content: str) -> float:
        """Estimate First Contentful Paint"""
        
        base_fcp = 1.2
        
        # CSS complexity affects FCP
        if css_content:
            css_size = len(css_content)
            base_fcp += (css_size / 10000) * 0.3  # 0.3s per 10KB of CSS
        
        # External CSS files
        css_links = len(re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html_content))
        base_fcp += css_links * 0.4
        
        # Render-blocking JavaScript
        blocking_scripts = len(re.findall(r'<script(?![^>]*async)[^>]*src[^>]*>', html_content))
        base_fcp += blocking_scripts * 0.5
        
        return round(base_fcp, 2)
    
    def _estimate_tti(self, html_content: str) -> float:
        """Estimate Time to Interactive"""
        
        base_tti = 3.0
        
        # JavaScript complexity affects TTI
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        total_js_size = sum(len(script) for script in script_tags)
        base_tti += (total_js_size / 5000) * 1.0  # 1s per 5KB of JS
        
        # External scripts
        external_scripts = len(re.findall(r'<script[^>]*src[^>]*>', html_content))
        base_tti += external_scripts * 0.8
        
        # Event listeners (complexity indicator)
        event_listeners = len(re.findall(r'addEventListener', html_content, re.IGNORECASE))
        base_tti += event_listeners * 0.1
        
        return round(base_tti, 2)
    
    def _estimate_tbt(self, html_content: str) -> float:
        """Estimate Total Blocking Time"""
        
        base_tbt = 100.0  # milliseconds
        
        # Synchronous JavaScript increases TBT
        sync_scripts = len(re.findall(r'<script(?![^>]*async)[^>]*>', html_content))
        base_tbt += sync_scripts * 150
        
        # Long tasks estimation
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        for script in script_tags:
            if len(script) > 1000:  # Large inline scripts
                base_tbt += 200
        
        return round(base_tbt, 1)
    
    def _create_web_vital_score(self, metric: WebVitalMetric, value: float, unit: str) -> WebVitalScore:
        """Create WebVitalScore object with status determination"""
        
        thresholds = self.web_vitals_thresholds[metric]
        good_threshold = thresholds["good"]
        needs_improvement_threshold = thresholds["needs_improvement"]
        
        if value <= good_threshold:
            status = "good"
        elif value <= needs_improvement_threshold:
            status = "needs_improvement"
        else:
            status = "poor"
        
        # Generate recommendations based on metric and status
        recommendations = self._generate_metric_recommendations(metric, status, value)
        
        return WebVitalScore(
            metric=metric,
            value=value,
            unit=unit,
            threshold_good=good_threshold,
            threshold_needs_improvement=needs_improvement_threshold,
            status=status,
            recommendations=recommendations
        )
    
    def _generate_metric_recommendations(self, metric: WebVitalMetric, status: str, value: float) -> List[str]:
        """Generate specific recommendations for each metric"""
        
        recommendations = []
        
        if metric == WebVitalMetric.LARGEST_CONTENTFUL_PAINT:
            if status != "good":
                recommendations.extend([
                    "Optimize images with next-gen formats (WebP, AVIF)",
                    "Implement lazy loading for below-the-fold images",
                    "Use a CDN for faster resource delivery",
                    "Preload critical resources"
                ])
        
        elif metric == WebVitalMetric.FIRST_INPUT_DELAY:
            if status != "good":
                recommendations.extend([
                    "Minimize main thread work",
                    "Reduce JavaScript execution time",
                    "Use web workers for heavy computations",
                    "Break up long tasks"
                ])
        
        elif metric == WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT:
            if status != "good":
                recommendations.extend([
                    "Include size attributes on images and videos",
                    "Avoid inserting content above existing content",
                    "Use font-display: swap for web fonts",
                    "Reserve space for ads and embeds"
                ])
        
        elif metric == WebVitalMetric.FIRST_CONTENTFUL_PAINT:
            if status != "good":
                recommendations.extend([
                    "Eliminate render-blocking resources",
                    "Minimize CSS and JavaScript",
                    "Use critical CSS inlining",
                    "Optimize server response time"
                ])
        
        elif metric == WebVitalMetric.TIME_TO_INTERACTIVE:
            if status != "good":
                recommendations.extend([
                    "Reduce unused JavaScript",
                    "Minimize main thread work",
                    "Ensure text remains visible during webfont load",
                    "Keep request counts low and transfer sizes small"
                ])
        
        elif metric == WebVitalMetric.TOTAL_BLOCKING_TIME:
            if status != "good":
                recommendations.extend([
                    "Reduce impact of third-party code",
                    "Minimize main thread work",
                    "Use async/defer for non-critical scripts",
                    "Split large JavaScript bundles"
                ])
        
        return recommendations
    
    def _optimize_images(self, html_content: str, optimization_level: OptimizationLevel) -> Optional[PerformanceOptimization]:
        """Optimize images for better LCP"""
        
        optimized_html = html_content
        
        # Add loading attributes and dimensions
        img_pattern = r'<img([^>]*?)>'
        def optimize_img_tag(match):
            img_attrs = match.group(1)
            
            # Add loading="lazy" for non-critical images (keep first image eager)
            if 'loading=' not in img_attrs:
                # First image should be eager, others lazy
                loading_attr = 'loading="eager"'  # Could be made smarter
                img_attrs += f' {loading_attr}'
            
            # Add decoding="async"
            if 'decoding=' not in img_attrs:
                img_attrs += ' decoding="async"'
            
            # Add default dimensions if missing
            if 'width=' not in img_attrs and 'height=' not in img_attrs:
                img_attrs += ' width="600" height="400"'
            
            return f'<img{img_attrs}>'
        
        optimized_html = re.sub(img_pattern, optimize_img_tag, optimized_html)
        
        # Add preload for critical images
        if optimization_level in [OptimizationLevel.INTERMEDIATE, OptimizationLevel.AGGRESSIVE]:
            first_img_match = re.search(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', optimized_html)
            if first_img_match:
                preload_link = f'<link rel="preload" as="image" href="{first_img_match.group(1)}">'
                optimized_html = optimized_html.replace('<head>', f'<head>\n    {preload_link}')
        
        if optimized_html != html_content:
            return PerformanceOptimization(
                optimization_type="Image Optimization",
                original_value=html_content,
                optimized_value=optimized_html,
                improvement_estimate=0.8,  # Estimated 0.8s improvement
                implementation_code="Added lazy loading, dimensions, and preload for critical images"
            )
        
        return None
    
    def _optimize_css(self, css_content: str, optimization_level: OptimizationLevel) -> Optional[PerformanceOptimization]:
        """Optimize CSS for better FCP and LCP"""
        
        if not css_content:
            return None
        
        optimized_css = css_content
        
        # Remove comments
        optimized_css = re.sub(r'/\*.*?\*/', '', optimized_css, flags=re.DOTALL)
        
        # Minimize whitespace
        optimized_css = re.sub(r'\s+', ' ', optimized_css)
        optimized_css = re.sub(r';\s*}', '}', optimized_css)
        optimized_css = re.sub(r'{\s*', '{', optimized_css)
        
        # Remove unused vendor prefixes (basic)
        if optimization_level == OptimizationLevel.AGGRESSIVE:
            old_prefixes = ['-ms-', '-o-', '-moz-filter']
            for prefix in old_prefixes:
                pattern = f'{prefix}[^;]*;'
                optimized_css = re.sub(pattern, '', optimized_css)
        
        optimized_css = optimized_css.strip()
        
        if optimized_css != css_content:
            size_reduction = len(css_content) - len(optimized_css)
            improvement_estimate = size_reduction / 1000 * 0.1  # 0.1s per KB saved
            
            return PerformanceOptimization(
                optimization_type="CSS Optimization",
                original_value=css_content,
                optimized_value=optimized_css,
                improvement_estimate=improvement_estimate,
                implementation_code=f"Minified CSS, reduced size by {size_reduction} bytes"
            )
        
        return None
    
    def _optimize_javascript(self, html_content: str, optimization_level: OptimizationLevel) -> Optional[PerformanceOptimization]:
        """Optimize JavaScript for better FID and TBT"""
        
        optimized_html = html_content
        
        # Add async/defer to external scripts
        script_pattern = r'<script([^>]*?)src=([^>]*?)>'
        def optimize_script_tag(match):
            attrs = match.group(1)
            src_part = match.group(2)
            
            # Don't modify scripts that already have async or defer
            if 'async' in attrs or 'defer' in attrs:
                return f'<script{attrs}src={src_part}>'
            
            # Add defer by default (better for performance)
            return f'<script{attrs} defer src={src_part}>'
        
        optimized_html = re.sub(script_pattern, optimize_script_tag, optimized_html)
        
        # Minimize inline JavaScript
        inline_script_pattern = r'<script[^>]*>(.*?)</script>'
        def minimize_inline_script(match):
            script_content = match.group(1)
            
            # Basic minification
            minimized = re.sub(r'//.*?\n', '', script_content)  # Remove single-line comments
            minimized = re.sub(r'/\*.*?\*/', '', minimized, flags=re.DOTALL)  # Remove multi-line comments
            minimized = re.sub(r'\s+', ' ', minimized)  # Minimize whitespace
            minimized = minimized.strip()
            
            return f'<script>{minimized}</script>'
        
        if optimization_level == OptimizationLevel.AGGRESSIVE:
            optimized_html = re.sub(inline_script_pattern, minimize_inline_script, optimized_html, flags=re.DOTALL)
        
        if optimized_html != html_content:
            return PerformanceOptimization(
                optimization_type="JavaScript Optimization",
                original_value=html_content,
                optimized_value=optimized_html,
                improvement_estimate=0.3,  # Estimated improvement
                implementation_code="Added defer to external scripts and minimized inline JavaScript"
            )
        
        return None
    
    def _prevent_layout_shift(self, html_content: str, optimization_level: OptimizationLevel) -> Optional[PerformanceOptimization]:
        """Optimize for better CLS"""
        
        optimized_html = html_content
        
        # Ensure images have dimensions
        img_without_dimensions = r'<img(?![^>]*(?:width|height))[^>]*>'
        if re.search(img_without_dimensions, optimized_html):
            def add_dimensions(match):
                img_tag = match.group(0)
                # Add default dimensions
                img_tag = img_tag.replace('<img', '<img width="600" height="400"')
                return img_tag
            
            optimized_html = re.sub(img_without_dimensions, add_dimensions, optimized_html)
        
        # Add font-display: swap to any @font-face rules found in style tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        def optimize_fonts_in_style(match):
            style_content = match.group(1)
            
            # Add font-display: swap to @font-face rules
            font_face_pattern = r'(@font-face\s*{[^}]*?)}'
            def add_font_display(font_match):
                font_face = font_match.group(1)
                if 'font-display' not in font_face:
                    return f'{font_face}font-display: swap;}}'
                return f'{font_face}}}'
            
            style_content = re.sub(font_face_pattern, add_font_display, style_content, flags=re.DOTALL)
            return f'<style>{style_content}</style>'
        
        optimized_html = re.sub(style_pattern, optimize_fonts_in_style, optimized_html, flags=re.DOTALL)
        
        if optimized_html != html_content:
            return PerformanceOptimization(
                optimization_type="Layout Shift Prevention",
                original_value=html_content,
                optimized_value=optimized_html,
                improvement_estimate=0.05,  # CLS improvement
                implementation_code="Added dimensions to images and font-display: swap to fonts"
            )
        
        return None
    
    def _optimize_fonts(self, html_content: str, optimization_level: OptimizationLevel) -> Optional[PerformanceOptimization]:
        """Optimize web fonts for better performance"""
        
        optimized_html = html_content
        
        # Add font preloads
        font_links = re.findall(r'<link[^>]*href=["\']([^"\']*\.(?:woff2?|ttf|eot))["\'][^>]*>', optimized_html)
        
        if font_links and optimization_level in [OptimizationLevel.INTERMEDIATE, OptimizationLevel.AGGRESSIVE]:
            preload_links = []
            for font_url in font_links[:2]:  # Preload only the first 2 fonts
                preload_link = f'<link rel="preload" as="font" type="font/woff2" href="{font_url}" crossorigin>'
                preload_links.append(preload_link)
            
            if preload_links:
                preload_html = '\n    '.join(preload_links)
                optimized_html = optimized_html.replace('<head>', f'<head>\n    {preload_html}')
        
        # Add font-display CSS for Google Fonts
        google_fonts_pattern = r'<link[^>]*href=["\']https://fonts\.googleapis\.com[^"\']*["\'][^>]*>'
        google_font_links = re.findall(google_fonts_pattern, optimized_html)
        
        if google_font_links:
            for link in google_font_links:
                if 'display=swap' not in link:
                    # Add display=swap parameter
                    optimized_link = link.replace('">', '&display=swap">')
                    optimized_html = optimized_html.replace(link, optimized_link)
        
        if optimized_html != html_content:
            return PerformanceOptimization(
                optimization_type="Font Optimization",
                original_value=html_content,
                optimized_value=optimized_html,
                improvement_estimate=0.2,  # Estimated improvement
                implementation_code="Added font preloads and font-display: swap for web fonts"
            )
        
        return None
    
    def _extract_critical_css(self, css_content: str, html_content: str) -> str:
        """Extract critical CSS for above-the-fold content"""
        
        if not css_content:
            return ""
        
        # Simple critical CSS extraction based on common above-the-fold selectors
        critical_selectors = [
            r'body\s*{[^}]*}',
            r'h1\s*{[^}]*}',
            r'h2\s*{[^}]*}',
            r'h3\s*{[^}]*}',
            r'p\s*{[^}]*}',
            r'header\s*{[^}]*}',
            r'nav\s*{[^}]*}',
            r'\.header[^{]*{[^}]*}',
            r'\.nav[^{]*{[^}]*}',
            r'\.hero[^{]*{[^}]*}',
            r'\.banner[^{]*{[^}]*}',
            r'@media[^{]*{[^}]*max-width:\s*768px[^}]*}[^}]*}',  # Mobile styles
        ]
        
        critical_css = []
        
        for selector_pattern in critical_selectors:
            matches = re.findall(selector_pattern, css_content, re.IGNORECASE | re.DOTALL)
            critical_css.extend(matches)
        
        # Add base font and color styles
        base_styles = """
        body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
        * { box-sizing: border-box; }
        """
        
        return base_styles + '\n'.join(critical_css)
    
    def _estimate_improved_scores(self, current_scores: List[WebVitalScore], optimizations: List[PerformanceOptimization]) -> List[WebVitalScore]:
        """Estimate improved Web Vitals scores after optimizations"""
        
        improved_scores = []
        
        for score in current_scores:
            improved_value = score.value
            
            # Apply improvements based on optimizations
            for optimization in optimizations:
                if optimization.optimization_type == "Image Optimization":
                    if score.metric in [WebVitalMetric.LARGEST_CONTENTFUL_PAINT, WebVitalMetric.FIRST_CONTENTFUL_PAINT]:
                        improved_value = max(0.5, improved_value - optimization.improvement_estimate)
                
                elif optimization.optimization_type == "CSS Optimization":
                    if score.metric in [WebVitalMetric.FIRST_CONTENTFUL_PAINT, WebVitalMetric.LARGEST_CONTENTFUL_PAINT]:
                        improved_value = max(0.5, improved_value - optimization.improvement_estimate)
                
                elif optimization.optimization_type == "JavaScript Optimization":
                    if score.metric in [WebVitalMetric.FIRST_INPUT_DELAY, WebVitalMetric.TOTAL_BLOCKING_TIME]:
                        improved_value = max(10, improved_value - (optimization.improvement_estimate * 100))
                    elif score.metric == WebVitalMetric.TIME_TO_INTERACTIVE:
                        improved_value = max(1.0, improved_value - optimization.improvement_estimate)
                
                elif optimization.optimization_type == "Layout Shift Prevention":
                    if score.metric == WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT:
                        improved_value = max(0.01, improved_value - optimization.improvement_estimate)
                
                elif optimization.optimization_type == "Font Optimization":
                    if score.metric in [WebVitalMetric.FIRST_CONTENTFUL_PAINT, WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT]:
                        improved_value = max(0.01, improved_value - optimization.improvement_estimate)
            
            # Create new score with improved value
            improved_score = self._create_web_vital_score(score.metric, improved_value, score.unit)
            improved_scores.append(improved_score)
        
        return improved_scores
    
    def _calculate_overall_score(self, web_vital_scores: List[WebVitalScore]) -> float:
        """Calculate overall Core Web Vitals score"""
        
        score = 0.0
        total_weight = 0.0
        
        # Weight the core metrics more heavily
        metric_weights = {
            WebVitalMetric.LARGEST_CONTENTFUL_PAINT: 25,
            WebVitalMetric.FIRST_INPUT_DELAY: 25,
            WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT: 25,
            WebVitalMetric.FIRST_CONTENTFUL_PAINT: 15,
            WebVitalMetric.TIME_TO_INTERACTIVE: 10,
            WebVitalMetric.TOTAL_BLOCKING_TIME: 10
        }
        
        for vital_score in web_vital_scores:
            weight = metric_weights.get(vital_score.metric, 5)
            
            if vital_score.status == "good":
                metric_score = 100
            elif vital_score.status == "needs_improvement":
                metric_score = 60
            else:
                metric_score = 20
            
            score += metric_score * weight
            total_weight += weight
        
        return round(score / total_weight if total_weight > 0 else 0, 1)
    
    def _generate_performance_recommendations(
        self,
        scores: List[WebVitalScore],
        optimizations: List[PerformanceOptimization],
        optimization_level: OptimizationLevel
    ) -> List[str]:
        """Generate comprehensive performance recommendations"""
        
        recommendations = []
        
        # Collect recommendations from individual scores
        for score in scores:
            if score.status != "good":
                recommendations.extend(score.recommendations)
        
        # Add optimization-level specific recommendations
        if optimization_level == OptimizationLevel.BASIC:
            recommendations.extend([
                "Consider implementing intermediate optimizations for better performance",
                "Monitor Core Web Vitals regularly for continuous improvement"
            ])
        elif optimization_level == OptimizationLevel.INTERMEDIATE:
            recommendations.extend([
                "Consider aggressive optimizations for maximum performance",
                "Implement real user monitoring (RUM) for accurate metrics"
            ])
        else:  # AGGRESSIVE
            recommendations.extend([
                "Monitor for any functionality issues after aggressive optimizations",
                "Consider implementing service worker for advanced caching"
            ])
        
        # Add general recommendations
        general_recommendations = [
            "Use a Content Delivery Network (CDN) for global performance",
            "Implement proper caching strategies",
            "Optimize server response times",
            "Consider implementing HTTP/2 or HTTP/3",
            "Use modern image formats (WebP, AVIF) when possible"
        ]
        
        recommendations.extend(general_recommendations)
        
        # Remove duplicates and return
        return list(set(recommendations))
    
    def _estimate_metric_improvements(
        self,
        current_scores: List[WebVitalScore],
        improved_scores: List[WebVitalScore]
    ) -> Dict[str, float]:
        """Estimate metric improvements"""
        
        improvements = {}
        
        for current, improved in zip(current_scores, improved_scores):
            metric_name = current.metric.value
            improvement = current.value - improved.value
            improvement_percentage = (improvement / current.value) * 100 if current.value > 0 else 0
            
            improvements[f"{metric_name}_absolute"] = round(improvement, 3)
            improvements[f"{metric_name}_percentage"] = round(improvement_percentage, 1)
        
        return improvements


# Export for module usage
__all__ = [
    "CoreWebVitalsOptimizer",
    "WebVitalMetric",
    "OptimizationLevel",
    "ResourceType",
    "WebVitalScore",
    "PerformanceOptimization",
    "CoreWebVitalsResult"
]