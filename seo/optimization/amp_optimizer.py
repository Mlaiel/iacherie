"""AMP Optimizer - Accelerated Mobile Pages Generation and Optimization

This module provides comprehensive AMP (Accelerated Mobile Pages) generation
and optimization for mobile-first content delivery and improved mobile SEO performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from urllib.parse import urlparse
import base64

logger = logging.getLogger(__name__)


class AMPComponentType(Enum):
    """AMP component types"""
    
    IMAGE = "amp-img"
    VIDEO = "amp-video"
    AUDIO = "amp-audio"
    IFRAME = "amp-iframe"
    SOCIAL = "amp-social-share"
    ANALYTICS = "amp-analytics"
    FORM = "amp-form"
    CAROUSEL = "amp-carousel"
    ACCORDION = "amp-accordion"
    SIDEBAR = "amp-sidebar"


class ContentType(Enum):
    """Content types for AMP optimization"""
    
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    PRODUCT = "product"
    VIDEO = "video"
    GALLERY = "gallery"
    NEWS = "news"
    RECIPE = "recipe"
    EVENT = "event"


@dataclass
class AMPValidationResult:
    """AMP validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    performance_score: float
    recommendations: List[str]


@dataclass
class AMPPageResult:
    """Complete AMP page generation result"""
    amp_html: str
    amp_css: str
    amp_js_components: List[str]
    structured_data: Dict[str, Any]
    validation_result: AMPValidationResult
    performance_metrics: Dict[str, float]
    mobile_usability_score: float


class AMPOptimizer:
    """
    Advanced AMP (Accelerated Mobile Pages) optimizer that generates
    mobile-optimized pages for improved performance and mobile SEO.
    """
    
    def __init__(self):
        """Initialize the AMP optimizer"""
        self.amp_version = "2.0"
        self.required_scripts = {
            "amp-runtime": "https://cdn.ampproject.org/v0.js"
        }
        self.max_amp_css_size = 75000  # 75KB limit for AMP CSS
        self.amp_boilerplate = self._get_amp_boilerplate()
        
    def generate_amp_page(
        self,
        content: str,
        title: str,
        meta_description: str,
        canonical_url: str,
        content_type: ContentType = ContentType.ARTICLE,
        author: str = "",
        published_date: str = "",
        image_url: str = "",
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> AMPPageResult:
        """
        Generate complete AMP page with optimization.
        
        Args:
            content: Main content to convert to AMP
            title: Page title
            meta_description: Meta description
            canonical_url: Original page URL
            content_type: Type of content
            author: Content author
            published_date: Publication date (ISO format)
            image_url: Featured image URL
            additional_metadata: Additional metadata
            
        Returns:
            AMPPageResult with complete AMP page and validation
        """
        try:
            logger.info(f"Generating AMP page for {content_type.value} content")
            
            # Convert HTML content to AMP-compatible format
            amp_content = self._convert_to_amp_html(content)
            
            # Generate AMP CSS
            amp_css = self._generate_amp_css(content_type)
            
            # Identify required AMP components
            required_components = self._identify_amp_components(content)
            
            # Generate structured data
            structured_data = self._generate_amp_structured_data(
                title, meta_description, canonical_url, content_type,
                author, published_date, image_url, additional_metadata
            )
            
            # Build complete AMP HTML
            amp_html = self._build_amp_html(
                amp_content, title, meta_description, canonical_url,
                amp_css, required_components, structured_data
            )
            
            # Validate AMP
            validation_result = self._validate_amp_html(amp_html)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_amp_performance_metrics(
                amp_html, amp_css, required_components
            )
            
            # Calculate mobile usability score
            mobile_usability_score = self._calculate_mobile_usability_score(
                amp_html, validation_result
            )
            
            return AMPPageResult(
                amp_html=amp_html,
                amp_css=amp_css,
                amp_js_components=required_components,
                structured_data=structured_data,
                validation_result=validation_result,
                performance_metrics=performance_metrics,
                mobile_usability_score=mobile_usability_score
            )
            
        except Exception as e:
            logger.error(f"Error generating AMP page: {str(e)}")
            raise
    
    def _convert_to_amp_html(self, content: str) -> str:
        """Convert regular HTML content to AMP-compatible HTML"""
        
        amp_content = content
        
        # Replace img tags with amp-img
        img_pattern = r'<img([^>]*?)src=["\']([^"\']*?)["\']([^>]*?)>'
        def replace_img(match):
            attrs_before = match.group(1)
            src = match.group(2)
            attrs_after = match.group(3)
            
            # Extract width and height or set defaults
            width_match = re.search(r'width=["\'](\d+)["\']', attrs_before + attrs_after)
            height_match = re.search(r'height=["\'](\d+)["\']', attrs_before + attrs_after)
            
            width = width_match.group(1) if width_match else "600"
            height = height_match.group(1) if height_match else "400"
            
            # Extract alt text
            alt_match = re.search(r'alt=["\']([^"\']*?)["\']', attrs_before + attrs_after)
            alt = alt_match.group(1) if alt_match else ""
            
            return f'<amp-img src="{src}" width="{width}" height="{height}" alt="{alt}" layout="responsive"></amp-img>'
        
        amp_content = re.sub(img_pattern, replace_img, amp_content)
        
        # Replace video tags with amp-video
        video_pattern = r'<video([^>]*?)src=["\']([^"\']*?)["\']([^>]*?)>.*?</video>'
        def replace_video(match):
            src = match.group(2)
            return f'<amp-video src="{src}" width="640" height="360" layout="responsive" controls></amp-video>'
        
        amp_content = re.sub(video_pattern, replace_video, amp_content, flags=re.DOTALL)
        
        # Replace iframe with amp-iframe
        iframe_pattern = r'<iframe([^>]*?)src=["\']([^"\']*?)["\']([^>]*?)>.*?</iframe>'
        def replace_iframe(match):
            src = match.group(2)
            return f'<amp-iframe src="{src}" width="600" height="400" layout="responsive" sandbox="allow-scripts allow-same-origin"></amp-iframe>'
        
        amp_content = re.sub(iframe_pattern, replace_iframe, amp_content, flags=re.DOTALL)
        
        # Remove disallowed tags and attributes
        disallowed_tags = ['script', 'style', 'link[rel="stylesheet"]', 'base', 'frame', 'frameset']
        for tag in disallowed_tags:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            amp_content = re.sub(pattern, '', amp_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove disallowed attributes
        disallowed_attrs = ['onclick', 'onload', 'onerror', 'style']
        for attr in disallowed_attrs:
            pattern = f'{attr}=["\'][^"\']*?["\']'
            amp_content = re.sub(pattern, '', amp_content, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        amp_content = re.sub(r'\s+', ' ', amp_content)
        
        return amp_content.strip()
    
    def _generate_amp_css(self, content_type: ContentType) -> str:
        """Generate optimized AMP CSS"""
        
        base_css = """
        /* AMP Base Styles */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #fff;
        }
        
        .amp-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.2;
        }
        
        h1 { font-size: 2.5em; }
        h2 { font-size: 2em; }
        h3 { font-size: 1.5em; }
        
        p {
            margin-bottom: 1.2em;
            font-size: 1.1em;
        }
        
        amp-img {
            margin: 1em 0;
            border-radius: 8px;
        }
        
        .meta-info {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 2em;
            padding-bottom: 1em;
            border-bottom: 1px solid #eee;
        }
        
        .content-wrapper {
            font-size: 1.1em;
            line-height: 1.7;
        }
        
        .amp-social-share {
            margin: 0.5em;
        }
        
        .amp-sidebar {
            background: #f8f9fa;
            padding: 20px;
        }
        
        /* Mobile Optimizations */
        @media (max-width: 768px) {
            .amp-container {
                padding: 15px;
            }
            
            h1 { font-size: 2em; }
            h2 { font-size: 1.7em; }
            h3 { font-size: 1.3em; }
            
            p {
                font-size: 1em;
            }
        }
        """
        
        # Add content-type specific styles
        content_specific_css = {
            ContentType.ARTICLE: """
            .article-header {
                text-align: center;
                margin-bottom: 2em;
            }
            
            .article-meta {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 1em;
            }
            """,
            
            ContentType.BLOG_POST: """
            .blog-post {
                background: #f9f9f9;
                padding: 2em;
                border-radius: 10px;
                margin-bottom: 2em;
            }
            """,
            
            ContentType.PRODUCT: """
            .product-info {
                background: #fff;
                border: 1px solid #ddd;
                padding: 20px;
                border-radius: 8px;
            }
            
            .price {
                font-size: 1.5em;
                color: #e74c3c;
                font-weight: bold;
            }
            """,
            
            ContentType.VIDEO: """
            .video-container {
                position: relative;
                margin: 2em 0;
            }
            
            .video-description {
                padding: 1em;
                background: #f8f9fa;
                border-radius: 0 0 8px 8px;
            }
            """
        }
        
        css = base_css + content_specific_css.get(content_type, "")
        
        # Ensure CSS doesn't exceed AMP limit
        if len(css.encode('utf-8')) > self.max_amp_css_size:
            # Minimize CSS by removing comments and extra whitespace
            css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
            css = re.sub(r'\s+', ' ', css)
            css = css.strip()
        
        return css
    
    def _identify_amp_components(self, content: str) -> List[str]:
        """Identify required AMP components based on content"""
        
        components = []
        
        # Always include runtime
        components.append("https://cdn.ampproject.org/v0.js")
        
        # Check for images
        if re.search(r'<amp-img', content, re.IGNORECASE):
            # amp-img is built-in, no additional script needed
            pass
        
        # Check for videos
        if re.search(r'<amp-video', content, re.IGNORECASE):
            components.append("https://cdn.ampproject.org/v0/amp-video-0.1.js")
        
        # Check for audio
        if re.search(r'<amp-audio', content, re.IGNORECASE):
            components.append("https://cdn.ampproject.org/v0/amp-audio-0.1.js")
        
        # Check for iframes
        if re.search(r'<amp-iframe', content, re.IGNORECASE):
            components.append("https://cdn.ampproject.org/v0/amp-iframe-0.1.js")
        
        # Check for social sharing
        if re.search(r'<amp-social-share', content, re.IGNORECASE):
            components.append("https://cdn.ampproject.org/v0/amp-social-share-0.1.js")
        
        # Check for forms
        if re.search(r'<form', content, re.IGNORECASE):
            components.append("https://cdn.ampproject.org/v0/amp-form-0.1.js")
        
        # Add analytics component by default for tracking
        components.append("https://cdn.ampproject.org/v0/amp-analytics-0.1.js")
        
        return list(set(components))  # Remove duplicates
    
    def _generate_amp_structured_data(
        self,
        title: str,
        description: str,
        canonical_url: str,
        content_type: ContentType,
        author: str,
        published_date: str,
        image_url: str,
        additional_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate structured data for AMP page"""
        
        base_structured_data = {
            "@context": "https://schema.org",
            "@type": self._get_schema_type_for_content(content_type),
            "headline": title,
            "description": description,
            "url": canonical_url,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": canonical_url
            }
        }
        
        # Add author information
        if author:
            base_structured_data["author"] = {
                "@type": "Person",
                "name": author
            }
        
        # Add publication date
        if published_date:
            base_structured_data["datePublished"] = published_date
            base_structured_data["dateModified"] = published_date
        
        # Add image
        if image_url:
            base_structured_data["image"] = {
                "@type": "ImageObject",
                "url": image_url,
                "width": 1200,
                "height": 630
            }
        
        # Add content-specific structured data
        if content_type == ContentType.ARTICLE:
            base_structured_data["@type"] = "Article"
            base_structured_data["publisher"] = {
                "@type": "Organization",
                "name": "Ainflue Platform",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://ainflue.com/logo.png"
                }
            }
        
        elif content_type == ContentType.PRODUCT:
            base_structured_data["@type"] = "Product"
            if additional_metadata:
                if "price" in additional_metadata:
                    base_structured_data["offers"] = {
                        "@type": "Offer",
                        "price": additional_metadata["price"],
                        "priceCurrency": additional_metadata.get("currency", "USD"),
                        "availability": "https://schema.org/InStock"
                    }
        
        elif content_type == ContentType.VIDEO:
            base_structured_data["@type"] = "VideoObject"
            if additional_metadata:
                if "duration" in additional_metadata:
                    base_structured_data["duration"] = additional_metadata["duration"]
                if "video_url" in additional_metadata:
                    base_structured_data["contentUrl"] = additional_metadata["video_url"]
        
        return base_structured_data
    
    def _build_amp_html(
        self,
        content: str,
        title: str,
        meta_description: str,
        canonical_url: str,
        amp_css: str,
        required_components: List[str],
        structured_data: Dict[str, Any]
    ) -> str:
        """Build complete AMP HTML document"""
        
        # Generate component script tags
        component_scripts = []
        for component_url in required_components:
            if "v0.js" in component_url:
                component_scripts.append(f'<script async src="{component_url}"></script>')
            else:
                component_scripts.append(f'<script async custom-element="{self._extract_component_name(component_url)}" src="{component_url}"></script>')
        
        # Build AMP HTML
        amp_html = f"""<!doctype html>
<html ⚡ lang="en">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="canonical" href="{canonical_url}">
    <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
    <meta name="description" content="{meta_description}">
    
    <!-- AMP Runtime -->
    {chr(10).join(component_scripts)}
    
    <!-- AMP Boilerplate -->
    {self.amp_boilerplate}
    
    <!-- Custom AMP CSS -->
    <style amp-custom>
    {amp_css}
    </style>
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(structured_data, indent=2)}
    </script>
    
    <!-- AMP Analytics -->
    <amp-analytics type="googleanalytics">
        <script type="application/json">
        {{
            "vars": {{
                "account": "UA-XXXXX-Y"
            }},
            "triggers": {{
                "trackPageview": {{
                    "on": "visible",
                    "request": "pageview"
                }}
            }}
        }}
        </script>
    </amp-analytics>
</head>
<body>
    <div class="amp-container">
        <header class="amp-header">
            <h1>{title}</h1>
            <div class="meta-info">
                <span>Published on Ainflue Platform</span>
            </div>
        </header>
        
        <main class="content-wrapper">
            {content}
        </main>
        
        <footer class="amp-footer">
            <amp-social-share type="twitter" width="45" height="33"></amp-social-share>
            <amp-social-share type="facebook" width="45" height="33"></amp-social-share>
            <amp-social-share type="linkedin" width="45" height="33"></amp-social-share>
        </footer>
    </div>
</body>
</html>"""
        
        return amp_html
    
    def _validate_amp_html(self, amp_html: str) -> AMPValidationResult:
        """Validate AMP HTML for compliance"""
        
        errors = []
        warnings = []
        
        # Check for required AMP attributes
        if '⚡' not in amp_html and 'amp' not in amp_html:
            errors.append("Missing AMP attribute on html tag")
        
        # Check for required meta tags
        if 'charset="utf-8"' not in amp_html:
            errors.append("Missing charset meta tag")
        
        if 'name="viewport"' not in amp_html:
            errors.append("Missing viewport meta tag")
        
        if 'rel="canonical"' not in amp_html:
            errors.append("Missing canonical link")
        
        # Check for AMP boilerplate
        if 'amp-boilerplate' not in amp_html:
            errors.append("Missing AMP boilerplate")
        
        # Check for disallowed elements
        disallowed_patterns = [
            r'<script(?![^>]*(?:type="application/(?:ld\+)?json"|src="https://cdn\.ampproject\.org/))[^>]*>',
            r'<link[^>]*rel="stylesheet"[^>]*>',
            r'<style(?![^>]*amp-)',
            r'onclick=',
            r'onload=',
        ]
        
        for pattern in disallowed_patterns:
            if re.search(pattern, amp_html, re.IGNORECASE):
                errors.append(f"Disallowed element or attribute found: {pattern}")
        
        # Check CSS size limit
        css_match = re.search(r'<style amp-custom>(.*?)</style>', amp_html, re.DOTALL)
        if css_match:
            css_size = len(css_match.group(1).encode('utf-8'))
            if css_size > self.max_amp_css_size:
                errors.append(f"CSS size ({css_size} bytes) exceeds AMP limit ({self.max_amp_css_size} bytes)")
        
        # Performance warnings
        if len(amp_html.encode('utf-8')) > 500000:  # 500KB
            warnings.append("HTML size is large, may impact performance")
        
        # Calculate performance score
        performance_score = 100.0
        performance_score -= len(errors) * 20  # 20 points per error
        performance_score -= len(warnings) * 5  # 5 points per warning
        performance_score = max(0, performance_score)
        
        # Generate recommendations
        recommendations = []
        if errors:
            recommendations.append("Fix AMP validation errors to ensure proper functionality")
        if warnings:
            recommendations.append("Address warnings to improve performance")
        if performance_score < 80:
            recommendations.append("Optimize content size and complexity for better mobile performance")
        
        is_valid = len(errors) == 0
        
        return AMPValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            performance_score=performance_score,
            recommendations=recommendations
        )
    
    def _calculate_amp_performance_metrics(
        self,
        amp_html: str,
        amp_css: str,
        required_components: List[str]
    ) -> Dict[str, float]:
        """Calculate AMP performance metrics"""
        
        # Calculate sizes
        html_size = len(amp_html.encode('utf-8'))
        css_size = len(amp_css.encode('utf-8'))
        
        # Estimate load time based on sizes and complexity
        base_load_time = 0.5  # AMP runtime load time
        html_load_time = html_size / 1000000  # 1MB/s assumption
        css_load_time = css_size / 1000000
        component_load_time = len(required_components) * 0.1
        
        total_load_time = base_load_time + html_load_time + css_load_time + component_load_time
        
        # Calculate First Contentful Paint estimate
        fcp_estimate = total_load_time * 0.7
        
        # Calculate Largest Contentful Paint estimate
        lcp_estimate = total_load_time * 0.9
        
        # Calculate Cumulative Layout Shift (lower is better)
        cls_estimate = 0.05 if html_size < 100000 else 0.1
        
        # Calculate Time to Interactive
        tti_estimate = total_load_time * 1.2
        
        return {
            "html_size_kb": html_size / 1024,
            "css_size_kb": css_size / 1024,
            "estimated_load_time_ms": total_load_time * 1000,
            "first_contentful_paint_ms": fcp_estimate * 1000,
            "largest_contentful_paint_ms": lcp_estimate * 1000,
            "cumulative_layout_shift": cls_estimate,
            "time_to_interactive_ms": tti_estimate * 1000,
            "component_count": len(required_components)
        }
    
    def _calculate_mobile_usability_score(
        self,
        amp_html: str,
        validation_result: AMPValidationResult
    ) -> float:
        """Calculate mobile usability score"""
        
        score = 100.0
        
        # Deduct for validation errors
        score -= len(validation_result.errors) * 15
        score -= len(validation_result.warnings) * 5
        
        # Check for mobile-friendly elements
        mobile_friendly_checks = [
            (r'viewport.*width=device-width', 10, "Responsive viewport"),
            (r'<amp-img[^>]*layout="responsive"', 10, "Responsive images"),
            (r'font-size:\s*1\.[0-9]+em', 5, "Readable font sizes"),
            (r'touch-action:', 5, "Touch-friendly interactions"),
            (r'@media[^{]*max-width', 10, "Mobile CSS media queries")
        ]
        
        for pattern, points, description in mobile_friendly_checks:
            if re.search(pattern, amp_html, re.IGNORECASE):
                # Points already included in base score
                pass
            else:
                score -= points
        
        # Bonus for AMP optimizations
        if validation_result.is_valid:
            score += 10  # Bonus for valid AMP
        
        return max(0, min(100, score))
    
    def _get_amp_boilerplate(self) -> str:
        """Get standard AMP boilerplate code"""
        return """<style amp-boilerplate>body{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}@-webkit-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-moz-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-ms-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-o-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}</style><noscript><style amp-boilerplate>body{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}</style></noscript>"""
    
    def _extract_component_name(self, component_url: str) -> str:
        """Extract component name from URL"""
        match = re.search(r'/(amp-[^-]+)', component_url)
        return match.group(1) if match else "amp-component"
    
    def _get_schema_type_for_content(self, content_type: ContentType) -> str:
        """Get appropriate Schema.org type for content"""
        mapping = {
            ContentType.ARTICLE: "Article",
            ContentType.BLOG_POST: "BlogPosting",
            ContentType.PRODUCT: "Product",
            ContentType.VIDEO: "VideoObject",
            ContentType.GALLERY: "ImageGallery",
            ContentType.NEWS: "NewsArticle",
            ContentType.RECIPE: "Recipe",
            ContentType.EVENT: "Event"
        }
        return mapping.get(content_type, "WebPage")
    
    def optimize_amp_for_mobile(self, amp_result: AMPPageResult) -> AMPPageResult:
        """Further optimize AMP page for mobile performance"""
        
        optimized_html = amp_result.amp_html
        
        # Add preconnect for faster resource loading
        preconnect_links = """
        <link rel="preconnect" href="https://cdn.ampproject.org">
        <link rel="preconnect" href="https://www.google-analytics.com">
        """
        
        optimized_html = optimized_html.replace(
            '<meta name="viewport"',
            preconnect_links + '\n    <meta name="viewport"'
        )
        
        # Add critical CSS inlining hints
        critical_css_hint = '/* Above-the-fold styles */'
        optimized_css = critical_css_hint + amp_result.amp_css
        
        # Update performance metrics
        updated_metrics = amp_result.performance_metrics.copy()
        updated_metrics["mobile_optimization_applied"] = 1.0
        
        return AMPPageResult(
            amp_html=optimized_html,
            amp_css=optimized_css,
            amp_js_components=amp_result.amp_js_components,
            structured_data=amp_result.structured_data,
            validation_result=amp_result.validation_result,
            performance_metrics=updated_metrics,
            mobile_usability_score=min(100, amp_result.mobile_usability_score + 5)
        )


# Export for module usage
__all__ = [
    "AMPOptimizer",
    "AMPComponentType",
    "ContentType",
    "AMPValidationResult",
    "AMPPageResult"
]