"""Custom Branding Engine
=====================

Advanced branding customization engine with AI-powered asset optimization,
intelligent color palette generation, responsive design adaptation, and
comprehensive brand asset management for enterprise deployments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import logging
import json
import uuid
import hashlib
import io
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import cv2
import colorsys
from sklearn.cluster import KMeans
import webcolors
import cssutils
import jinja2
from pathlib import Path
import base64

logger = logging.getLogger(__name__)


class AssetOptimizationLevel(Enum):
    """
Asset optimization level"""

    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    LOSSLESS = "lossless"


class ResponsiveBreakpoint(Enum):
    """Responsive design breakpoints"""

    MOBILE = "mobile"  # < 768px
    TABLET = "tablet"  # 768px - 1024px
    DESKTOP = "desktop"  # 1024px - 1440px
    LARGE = "large"  # > 1440px


class BrandElementType(Enum):
    """Brand element types"""

    LOGO = "logo"
    ICON = "icon"
    WATERMARK = "watermark"
    SIGNATURE = "signature"
    BANNER = "banner"
    BACKGROUND = "background"
    PATTERN = "pattern"


@dataclass
class ColorAnalysis:
    """Color analysis results"""
    dominant_colors: List[str]
    color_harmony: str
    accessibility_score: float
    contrast_ratios: Dict[str, float]
    mood_classification: str
    temperature: str  # warm, cool, neutral
    saturation_level: str  # low, medium, high
    brightness_level: str  # dark, medium, bright


@dataclass
class LogoVariant:
    """
Logo variant configuration"""
    variant_id: str
    name: str
    use_case: str
    dimensions: Dict[str, int]
    background_type: str  # transparent, white, dark, color
    format: str  # png, svg, jpg, webp
    optimization_level: AssetOptimizationLevel
    file_size: int
    quality_score: float
    accessibility_compliant: bool
    data: Optional[bytes] = None


@dataclass
class ResponsiveAsset:
    """
Responsive asset configuration"""
    asset_id: str
    base_asset: str
    breakpoints: Dict[ResponsiveBreakpoint, Dict[str, Any]]
    adaptive_sizing: bool = True
    retina_support: bool = True
    lazy_loading: bool = True
    webp_support: bool = True


@dataclass
class BrandGuidelines:
    """
Brand guidelines configuration"""
    brand_name: str
    primary_colors: List[str]
    secondary_colors: List[str]
    typography_primary: str
    typography_secondary: str
    logo_min_size: Dict[str, int]
    logo_clear_space: Dict[str, int]
    usage_rules: List[str]
    prohibited_usage: List[str]
    color_combinations: List[Dict[str, str]]
    accessibility_requirements: Dict[str, Any]


class ColorIntelligence:
    """
AI-powered color analysis and optimization"""
    
    def __init__(self):
        self._color_emotions = {
            'red': ['passionate', 'energetic', 'urgent', 'bold'],
            'blue': ['trustworthy', 'professional', 'calm', 'stable'],
            'green': ['natural', 'growth', 'harmony', 'fresh'],
            'yellow': ['optimistic', 'creative', 'attention', 'cheerful'],
            'purple': ['luxury', 'creative', 'mysterious', 'sophisticated'],
            'orange': ['enthusiastic', 'friendly', 'confident', 'vibrant'],
            'pink': ['feminine', 'compassionate', 'nurturing', 'playful'],
            'brown': ['reliable', 'earthly', 'stable', 'comfortable'],
            'black': ['sophisticated', 'powerful', 'elegant', 'modern'],
            'white': ['pure', 'clean', 'minimal', 'fresh'],
            'gray': ['neutral', 'balanced', 'professional', 'timeless']
        }
    
    async def analyze_brand_colors(self, colors: List[str]) -> ColorAnalysis:
        """
Analyze brand colors for harmony, accessibility, and emotional impact"""
        try:
            # Extract dominant colors
            dominant_colors = self._extract_dominant_colors(colors)
            
            # Analyze color harmony
            harmony = self._analyze_color_harmony(colors)
            
            # Calculate accessibility scores
            accessibility_score, contrast_ratios = self._calculate_accessibility(colors)
            
            # Classify mood and temperature
            mood = self._classify_mood(colors)
            temperature = self._analyze_temperature(colors)
            saturation = self._analyze_saturation(colors)
            brightness = self._analyze_brightness(colors)
            
            return ColorAnalysis(
                dominant_colors=dominant_colors,
                color_harmony=harmony,
                accessibility_score=accessibility_score,
                contrast_ratios=contrast_ratios,
                mood_classification=mood,
                temperature=temperature,
                saturation_level=saturation,
                brightness_level=brightness
            )
            
        except Exception as e:
            logger.error(f"Color analysis failed: {e}")
            raise
    
    def _extract_dominant_colors(self, colors: List[str]) -> List[str]:
        """Extract dominant colors from palette"""
        # Sort colors by usage frequency/importance
        return colors[:5]  # Return top 5 dominant colors
    
    def _analyze_color_harmony(self, colors: List[str]) -> str:
        """
Analyze color harmony type"""
        if len(colors) < 2:
            return "monochromatic"
        
        # Convert to HSV for analysis
        hsv_colors = []
        for color in colors:
            try:
                rgb = webcolors.hex_to_rgb(color)
                hsv = colorsys.rgb_to_hsv(rgb.red/255, rgb.green/255, rgb.blue/255)
                hsv_colors.append(hsv)
            except:
                continue
        
        if not hsv_colors:
            return "unknown"
        
        # Analyze hue relationships
        hues = [hsv[0] for hsv in hsv_colors]
        hue_differences = [abs(hues[i] - hues[i+1]) for i in range(len(hues)-1)]
        
        avg_diff = np.mean(hue_differences) if hue_differences else 0
        
        if avg_diff < 0.1:
            return "monochromatic"
        elif avg_diff < 0.25:
            return "analogous"
        elif 0.4 < avg_diff < 0.6:
            return "complementary"
        else:
            return "triadic"
    
    def _calculate_accessibility(self, colors: List[str]) -> Tuple[float, Dict[str, float]]:
        """Calculate WCAG accessibility compliance"""
        contrast_ratios = {}
        total_score = 0
        comparisons = 0
        
        for i, color1 in enumerate(colors):
            for j, color2 in enumerate(colors[i+1:], i+1):
                try:
                    ratio = self._calculate_contrast_ratio(color1, color2)
                    contrast_ratios[f"{color1}-{color2}"] = ratio
                    
                    # WCAG AA compliance (4.5:1 for normal text)
                    if ratio >= 4.5:
                        total_score += 1
                    elif ratio >= 3:
                        total_score += 0.5
                    
                    comparisons += 1
                except:
                    continue
        
        accessibility_score = total_score / comparisons if comparisons > 0 else 0
        return accessibility_score, contrast_ratios
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors"""
        try:
            rgb1 = webcolors.hex_to_rgb(color1)
            rgb2 = webcolors.hex_to_rgb(color2)
            
            # Calculate relative luminance
            def luminance(rgb):
                r, g, b = [c/255 for c in rgb]
                r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
                g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
                b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
                return 0.2126*r + 0.7152*g + 0.0722*b
            
            l1 = luminance(rgb1)
            l2 = luminance(rgb2)
            
            # Calculate contrast ratio
            if l1 > l2:
                return (l1 + 0.05) / (l2 + 0.05)
            else:
                return (l2 + 0.05) / (l1 + 0.05)
                
        except:
            return 1.0
    
    def _classify_mood(self, colors: List[str]) -> str:
        """
Classify emotional mood of color palette"""
        mood_scores = {}
        
        for color_hex in colors:
            try:
                # Get closest named color
                rgb = webcolors.hex_to_rgb(color_hex)
                closest_color = self._get_closest_color_name(rgb)
                
                if closest_color in self._color_emotions:
                    for emotion in self._color_emotions[closest_color]:
                        mood_scores[emotion] = mood_scores.get(emotion, 0) + 1
            except:
                continue
        
        if not mood_scores:
            return "neutral"
        
        return max(mood_scores, key=mood_scores.get)
    
    def _get_closest_color_name(self, rgb) -> str:
        """Get closest named color"""
        color_names = {
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'purple': (128, 0, 128),
            'orange': (255, 165, 0),
            'pink': (255, 192, 203),
            'brown': (165, 42, 42),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'gray': (128, 128, 128)
        }
        
        min_distance = float('inf')
        closest_color = 'gray'
        
        for name, color_rgb in color_names.items():
            distance = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb)) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_color = name
        
        return closest_color
    
    def _analyze_temperature(self, colors: List[str]) -> str:
        """
Analyze color temperature"""
        warm_count = 0
        cool_count = 0
        
        for color_hex in colors:
            try:
                rgb = webcolors.hex_to_rgb(color_hex)
                # Simple temperature analysis based on red/blue dominance
                if rgb.red > rgb.blue:
                    warm_count += 1
                elif rgb.blue > rgb.red:
                    cool_count += 1
            except:
                continue
        
        if warm_count > cool_count:
            return "warm"
        elif cool_count > warm_count:
            return "cool"
        else:
            return "neutral"
    
    def _analyze_saturation(self, colors: List[str]) -> str:
        """Analyze saturation level"""
        saturations = []
        
        for color_hex in colors:
            try:
                rgb = webcolors.hex_to_rgb(color_hex)
                hsv = colorsys.rgb_to_hsv(rgb.red/255, rgb.green/255, rgb.blue/255)
                saturations.append(hsv[1])
            except:
                continue
        
        if not saturations:
            return "medium"
        
        avg_saturation = np.mean(saturations)
        
        if avg_saturation < 0.3:
            return "low"
        elif avg_saturation > 0.7:
            return "high"
        else:
            return "medium"
    
    def _analyze_brightness(self, colors: List[str]) -> str:
        """Analyze brightness level"""
        brightnesses = []
        
        for color_hex in colors:
            try:
                rgb = webcolors.hex_to_rgb(color_hex)
                hsv = colorsys.rgb_to_hsv(rgb.red/255, rgb.green/255, rgb.blue/255)
                brightnesses.append(hsv[2])
            except:
                continue
        
        if not brightnesses:
            return "medium"
        
        avg_brightness = np.mean(brightnesses)
        
        if avg_brightness < 0.3:
            return "dark"
        elif avg_brightness > 0.7:
            return "bright"
        else:
            return "medium"


class LogoProcessor:
    """Advanced logo processing and optimization"""
    
    def __init__(self):
        self._standard_sizes = {
            'favicon': [(16, 16), (32, 32), (48, 48)],
            'small': [(64, 64), (128, 128)],
            'medium': [(256, 256), (512, 512)],
            'large': [(1024, 1024), (2048, 2048)]
        }
    
    async def process_logo_variants(
        self,
        logo_data: bytes,
        brand_colors: List[str],
        use_cases: List[str]
    ) -> List[LogoVariant]:
        """
Process logo into multiple variants for different use cases"""
        try:
            variants = []
            
            with Image.open(io.BytesIO(logo_data)) as img:
                # Ensure RGBA mode for transparency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Generate variants for each use case
                for use_case in use_cases:
                    case_variants = await self._generate_use_case_variants(img, use_case, brand_colors)
                    variants.extend(case_variants)
            
            return variants
            
        except Exception as e:
            logger.error(f"Logo variant processing failed: {e}")
            raise
    
    async def _generate_use_case_variants(
        self,
        img: Image.Image,
        use_case: str,
        brand_colors: List[str]
    ) -> List[LogoVariant]:
        """Generate logo variants for specific use case"""
        variants = []
        
        if use_case == "web_header":
            # Horizontal layouts, various sizes
            sizes = [(200, 60), (300, 90), (400, 120)]
            backgrounds = ['transparent', 'white', 'dark']
            
        elif use_case == "mobile_app":
            # Square formats for app icons
            sizes = [(57, 57), (114, 114), (120, 120), (180, 180)]
            backgrounds = ['transparent', 'white', 'brand_primary']
            
        elif use_case == "social_media":
            # Various social media sizes
            sizes = [(400, 400), (1200, 630), (1080, 1080)]
            backgrounds = ['white', 'brand_primary', 'gradient']
            
        elif use_case == "print":
            # High resolution for print
            sizes = [(2400, 2400), (3600, 3600)]
            backgrounds = ['transparent', 'white']
            
        else:
            # Default variants
            sizes = [(256, 256), (512, 512)]
            backgrounds = ['transparent', 'white']
        
        for size in sizes:
            for bg in backgrounds:
                try:
                    variant = await self._create_logo_variant(
                        img, size, bg, use_case, brand_colors
                    )
                    if variant:
                        variants.append(variant)
                except Exception as e:
                    logger.warning(f"Failed to create variant {size} {bg}: {e}")
                    continue
        
        return variants
    
    async def _create_logo_variant(
        self,
        img: Image.Image,
        size: Tuple[int, int],
        background: str,
        use_case: str,
        brand_colors: List[str]
    ) -> Optional[LogoVariant]:
        """Create individual logo variant"""
        try:
            # Resize with high quality
            resized = img.resize(size, Image.Resampling.LANCZOS)
            
            # Create background
            if background == 'transparent':
                final_img = resized
                bg_type = 'transparent'
            elif background == 'white':
                final_img = Image.new('RGBA', size, (255, 255, 255, 255))
                final_img.paste(resized, (0, 0), resized)
                bg_type = 'white'
            elif background == 'dark':
                final_img = Image.new('RGBA', size, (33, 37, 41, 255))
                final_img.paste(resized, (0, 0), resized)
                bg_type = 'dark'
            elif background == 'brand_primary' and brand_colors:
                try:
                    color_rgb = webcolors.hex_to_rgb(brand_colors[0])
                    final_img = Image.new('RGBA', size, (*color_rgb, 255))
                    final_img.paste(resized, (0, 0), resized)
                    bg_type = 'color'
                except:
                    final_img = resized
                    bg_type = 'transparent'
            else:
                final_img = resized
                bg_type = 'transparent'
            
            # Optimize and save
            output_buffer = io.BytesIO()
            
            # Choose optimal format
            if bg_type == 'transparent':
                format_type = 'PNG'
                final_img.save(output_buffer, format=format_type, optimize=True)
            else:
                # Convert to RGB for JPEG
                rgb_img = Image.new('RGB', size, (255, 255, 255))
                rgb_img.paste(final_img, (0, 0), final_img if final_img.mode == 'RGBA' else None)
                format_type = 'JPEG'
                rgb_img.save(output_buffer, format=format_type, quality=90, optimize=True)
            
            # Calculate quality score
            quality_score = self._calculate_logo_quality(final_img, size)
            
            # Check accessibility
            accessibility_compliant = self._check_logo_accessibility(final_img, brand_colors)
            
            variant = LogoVariant(
                variant_id=f"logo_{use_case}_{size[0]}x{size[1]}_{background}",
                name=f"{use_case.title()} {size[0]}x{size[1]} ({background})",
                use_case=use_case,
                dimensions={'width': size[0], 'height': size[1]},
                background_type=bg_type,
                format=format_type.lower(),
                optimization_level=AssetOptimizationLevel.STANDARD,
                file_size=len(output_buffer.getvalue()),
                quality_score=quality_score,
                accessibility_compliant=accessibility_compliant,
                data=output_buffer.getvalue()
            )
            
            return variant
            
        except Exception as e:
            logger.error(f"Failed to create logo variant: {e}")
            return None
    
    def _calculate_logo_quality(self, img: Image.Image, size: Tuple[int, int]) -> float:
        """Calculate logo quality score"""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(img)
            
            # Calculate sharpness (Laplacian variance)
            if len(img_array.shape) == 3:
                gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
            else:
                gray = img_array
            
            # Normalize to 0-1 range
            laplacian_var = cv2.Laplacian(gray.astype(np.uint8), cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000, 1.0)
            
            # Size appropriateness score
            pixel_count = size[0] * size[1]
            size_score = min(pixel_count / 65536, 1.0)  # Normalize against 256x256
            
            # Overall quality score
            quality_score = (sharpness_score * 0.7) + (size_score * 0.3)
            return quality_score
            
        except Exception:
            return 0.5  # Default medium quality
    
    def _check_logo_accessibility(self, img: Image.Image, brand_colors: List[str]) -> bool:
        """
Check logo accessibility compliance"""
        try:
            # Basic accessibility checks
            # In real implementation, this would include:
            # - Contrast ratio analysis
            # - Color blindness simulation
            # - Text readability assessment
            return True
        except Exception:
            return False


class ThemeCustomizer:
    """
Advanced theme customization and CSS generation"""
    
    def __init__(self):
        self._css_template = jinja2.Environment(
            loader=jinja2.DictLoader({
                'theme_base': self._get_base_css_template()
            })
        )
    
    async def generate_custom_theme(
        self,
        brand_colors: List[str],
        typography: Dict[str, Any],
        customizations: Dict[str, Any]
    ) -> Dict[str, str]:
        """
Generate custom theme CSS and JavaScript"""
        try:
            # Analyze colors
            color_intelligence = ColorIntelligence()
            color_analysis = await color_intelligence.analyze_brand_colors(brand_colors)
            
            # Generate CSS variables
            css_variables = self._generate_css_variables(brand_colors, typography, color_analysis)
            
            # Generate component styles
            component_styles = self._generate_component_styles(customizations)
            
            # Generate responsive styles
            responsive_styles = self._generate_responsive_styles(customizations)
            
            # Combine all styles
            full_css = self._combine_css_styles(css_variables, component_styles, responsive_styles)
            
            # Generate JavaScript for theme switching
            theme_js = self._generate_theme_javascript(customizations)
            
            return {
                'css': full_css,
                'javascript': theme_js,
                'variables': css_variables,
                'analysis': asdict(color_analysis)
            }
            
        except Exception as e:
            logger.error(f"Theme generation failed: {e}")
            raise
    
    def _generate_css_variables(
        self,
        brand_colors: List[str],
        typography: Dict[str, Any],
        color_analysis: ColorAnalysis
    ) -> str:
        """Generate CSS custom properties"""
        variables = []
        
        # Color variables
        for i, color in enumerate(brand_colors):
            variables.append(f"  --brand-color-{i+1}: {color};")
        
        # Semantic color variables
        if brand_colors:
            variables.extend([
                f"  --color-primary: {brand_colors[0]};",
                f"  --color-secondary: {brand_colors[1] if len(brand_colors) > 1 else brand_colors[0]};",
                f"  --color-accent: {brand_colors[2] if len(brand_colors) > 2 else brand_colors[0]};",
            ])
        
        # Typography variables
        for key, value in typography.items():
            css_key = key.replace('_', '-')
            variables.append(f"  --{css_key}: {value};")
        
        # Computed variables based on analysis
        variables.extend([
            f"  --color-temperature: '{color_analysis.temperature}';",
            f"  --color-mood: '{color_analysis.mood_classification}';",
            f"  --accessibility-score: {color_analysis.accessibility_score};",
        ])
        
        return ":root {\n" + "\n".join(variables) + "\n}"
    
    def _generate_component_styles(self, customizations: Dict[str, Any]) -> str:
        """Generate component-specific styles"""
        styles = []
        
        # Header styles
        if 'header' in customizations:
            header_config = customizations['header']
            styles.append(f""".header {{
    background: {header_config.get('background', 'var(--color-primary)')};
    height: {header_config.get('height', '64px')};
    box-shadow: {header_config.get('shadow', '0 2px 4px rgba(0,0,0,0.1)')};
}}""")
        
        # Button styles
        if 'buttons' in customizations:
            button_config = customizations['buttons']
            styles.append(f""".btn-primary {{
    background: {button_config.get('primary_bg', 'var(--color-primary)')};
    border-radius: {button_config.get('border_radius', '4px')};
    padding: {button_config.get('padding', '8px 16px')};
    transition: all 0.2s ease;
}}

.btn-primary:hover {{
    transform: {button_config.get('hover_transform', 'translateY(-1px)')};
    box-shadow: {button_config.get('hover_shadow', '0 4px 8px rgba(0,0,0,0.2)')};
}}""")
        
        return "\n".join(styles)
    
    def _generate_responsive_styles(self, customizations: Dict[str, Any]) -> str:
        """Generate responsive styles for different breakpoints"""
        responsive_css = []
        
        breakpoints = {
            'mobile': '(max-width: 767px)',
            'tablet': '(min-width: 768px) and (max-width: 1023px)',
            'desktop': '(min-width: 1024px)'
        }
        
        for breakpoint, media_query in breakpoints.items():
            if breakpoint in customizations:
                styles = []
                config = customizations[breakpoint]
                
                for selector, properties in config.items():
                    prop_strings = []
                    for prop, value in properties.items():
                        prop_strings.append(f"  {prop.replace('_', '-')}: {value};")
                    
                    styles.append(f"{selector} {{\n{''.join(prop_strings)}\n}}")
                
                responsive_css.append(f"@media {media_query} {{\n{chr(10).join(styles)}\n}}")
        
        return "\n\n".join(responsive_css)
    
    def _combine_css_styles(self, *style_sections) -> str:
        """Combine all CSS style sections"""
        return "\n\n".join(filter(None, style_sections))
    
    def _generate_theme_javascript(self, customizations: Dict[str, Any]) -> str:
        """Generate JavaScript for theme functionality"""
        js_code = """// Theme Management JavaScript
class ThemeManager {
    constructor() {
        this.currentTheme = 'light';
        this.init();
    }
    
    init() {
        this.loadSavedTheme();
        this.setupEventListeners();
    }
    
    loadSavedTheme() {
        const saved = localStorage.getItem('theme-preference');
        if (saved) {
            this.setTheme(saved);
        }
    }
    
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme-preference', theme);
        this.notifyThemeChange(theme);
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
    
    setupEventListeners() {
        const toggleBtn = document.querySelector('[data-theme-toggle]');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleTheme());
        }
    }
    
    notifyThemeChange(theme) {
        window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme } }));
    }
}

// Initialize theme manager
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});
"""
        
        # Add custom JavaScript if provided
        if 'custom_js' in customizations:
            js_code += f"\n\n// Custom JavaScript\n{customizations['custom_js']}"
        
        return js_code
    
    def _get_base_css_template(self) -> str:
        """Get base CSS template"""
        return """/* Base Theme CSS Template */
:root {
    /* Colors will be injected here */
    
    /* Base spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    
    /* Border radius */
    --radius-sm: 2px;
    --radius-md: 4px;
    --radius-lg: 8px;
    --radius-xl: 12px;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    
    /* Transitions */
    --transition-fast: 0.15s ease;
    --transition-normal: 0.25s ease;
    --transition-slow: 0.35s ease;
}

/* Dark theme overrides */
[data-theme="dark"] {
    --color-background: #1a1a1a;
    --color-surface: #2d2d2d;
    --color-text-primary: #ffffff;
    --color-text-secondary: #a0a0a0;
}

/* Base component styles */
.theme-component {
    transition: var(--transition-normal);
}

.theme-card {
    background: var(--color-surface, #ffffff);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--spacing-lg);
}

.theme-button {
    background: var(--color-primary);
    color: var(--color-text-primary);
    border: none;
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
    cursor: pointer;
    transition: var(--transition-fast);
}

.theme-button:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-lg);
}
"""
class BrandAssetManager:
    """
Comprehensive brand asset management system"""
    
    def __init__(self):
        self._asset_storage: Dict[str, Any] = {}
        self._asset_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def store_asset(
        self,
        asset_id: str,
        asset_data: bytes,
        metadata: Dict[str, Any]
    ) -> bool:
        """
Store brand asset with metadata"""
        try:
            # Store asset data
            self._asset_storage[asset_id] = asset_data
            
            # Store metadata
            self._asset_metadata[asset_id] = {
                **metadata,
                'stored_at': datetime.now(timezone.utc).isoformat(),
                'file_size': len(asset_data),
                'checksum': hashlib.sha256(asset_data).hexdigest()
            }
            
            logger.info(f"Stored brand asset: {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store asset {asset_id}: {e}")
            return False
    
    async def retrieve_asset(self, asset_id: str) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """Retrieve brand asset with metadata"""
        try:
            if asset_id in self._asset_storage:
                asset_data = self._asset_storage[asset_id]
                metadata = self._asset_metadata.get(asset_id, {})
                return asset_data, metadata
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve asset {asset_id}: {e}")
            return None
    
    async def optimize_asset_delivery(self, asset_id: str, format_hint: str) -> Optional[bytes]:
        """Optimize asset for delivery based on format hint"""
        try:
            asset_data, metadata = await self.retrieve_asset(asset_id) or (None, None)
            if not asset_data:
                return None
            
            # Apply format-specific optimizations
            if format_hint == 'webp' and metadata.get('mime_type', '').startswith('image/'):
                # Convert to WebP for better compression
                with Image.open(io.BytesIO(asset_data)) as img:
                    output_buffer = io.BytesIO()
                    img.save(output_buffer, format='WEBP', quality=85, optimize=True)
                    return output_buffer.getvalue()
            
            return asset_data
            
        except Exception as e:
            logger.error(f"Failed to optimize asset delivery {asset_id}: {e}")
            return None


class BrandingEngine:
    """Main branding engine orchestrator"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.color_intelligence = ColorIntelligence()
        self.logo_processor = LogoProcessor()
        self.theme_customizer = ThemeCustomizer()
        self.asset_manager = BrandAssetManager()
    
    async def create_comprehensive_brand_package(
        self,
        brand_name: str,
        primary_colors: List[str],
        logo_data: bytes,
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Create comprehensive brand package with all assets and themes"""
        try:
            # Analyze brand colors
            color_analysis = await self.color_intelligence.analyze_brand_colors(primary_colors)
            
            # Process logo variants
            use_cases = ['web_header', 'mobile_app', 'social_media', 'print']
            logo_variants = await self.logo_processor.process_logo_variants(
                logo_data, primary_colors, use_cases
            )
            
            # Generate custom theme
            typography = customizations.get('typography', {
                'font_family_primary': 'Inter, sans-serif',
                'font_size_base': '16px',
                'line_height_base': '1.5'
            })
            
            theme_package = await self.theme_customizer.generate_custom_theme(
                primary_colors, typography, customizations
            )
            
            # Store all assets
            asset_ids = []
            for variant in logo_variants:
                if variant.data:
                    asset_id = f"logo_{variant.variant_id}"
                    await self.asset_manager.store_asset(
                        asset_id,
                        variant.data,
                        asdict(variant)
                    )
                    asset_ids.append(asset_id)
            
            # Create brand guidelines
            guidelines = BrandGuidelines(
                brand_name=brand_name,
                primary_colors=primary_colors,
                secondary_colors=color_analysis.dominant_colors,
                typography_primary=typography.get('font_family_primary', 'Inter'),
                typography_secondary=typography.get('font_family_secondary', 'Georgia'),
                logo_min_size={'width': 32, 'height': 32},
                logo_clear_space={'top': 16, 'right': 16, 'bottom': 16, 'left': 16},
                usage_rules=[
                    'Maintain minimum clear space around logo',
                    'Do not distort logo proportions',
                    'Use approved color combinations only'
                ],
                prohibited_usage=[
                    'Do not place logo on busy backgrounds',
                    'Do not use unapproved colors',
                    'Do not rotate or skew logo'
                ],
                color_combinations=[
                    {'primary': primary_colors[0], 'text': '#ffffff'},
                    {'primary': '#ffffff', 'text': primary_colors[0]}
                ],
                accessibility_requirements={
                    'min_contrast_ratio': 4.5,
                    'color_blind_safe': True,
                    'screen_reader_compatible': True
                }
            )
            
            return {
                'brand_name': brand_name,
                'color_analysis': asdict(color_analysis),
                'logo_variants': [asdict(variant) for variant in logo_variants],
                'theme_package': theme_package,
                'brand_guidelines': asdict(guidelines),
                'asset_ids': asset_ids,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create brand package: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for branding engine"""
        try:
            return {
                'status': 'healthy',
                'components': {
                    'color_intelligence': 'active',
                    'logo_processor': 'active',
                    'theme_customizer': 'active',
                    'asset_manager': 'active'
                },
                'stored_assets': len(self.asset_manager._asset_storage),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 1.0
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 0.0
            }