"""
Image SEO Optimizer for Ainflue Platform
Advanced image optimization for search engines and visual platforms

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Tuple, Union, Set
import re
import json
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import base64
import math


@dataclass
class ImageMetadata:
    """Image metadata structure"""
    filename: str
    alt_text: str
    title: str
    caption: str
    file_size: int  # bytes
    dimensions: Tuple[int, int]  # width, height
    format: str  # jpg, png, webp, etc.
    context_url: str
    surrounding_text: str = ""
    structured_data: Dict = field(default_factory=dict)


@dataclass
class ImageOptimizationReport:
    """Image SEO optimization report"""
    image_url: str
    overall_score: float
    alt_text_score: float
    filename_score: float
    technical_score: float
    context_score: float
    accessibility_score: float
    recommendations: List[str]
    optimized_alt_text: str
    optimized_filename: str
    seo_opportunities: List[str]


class ImageSEOOptimizer:
    """
    Advanced Image SEO optimization engine
    Provides comprehensive image optimization for search engines and accessibility
    """
    
    def __init__(self) -> None:
        self.image_seo_factors = self._initialize_image_seo_factors()
        self.alt_text_patterns = self._load_alt_text_patterns()
        self.filename_conventions = self._load_filename_conventions()
        self.technical_guidelines = self._load_technical_guidelines()
        self.platform_requirements = self._load_platform_requirements()
        
    def _initialize_image_seo_factors(self) -> Dict[str, float]:
        """Initialize image SEO ranking factors"""
        return {
            # Alt text optimization (30%)
            'alt_text_quality': 0.15,
            'alt_text_keyword_relevance': 0.10,
            'alt_text_length_optimization': 0.05,
            
            # Filename optimization (20%)
            'filename_descriptiveness': 0.10,
            'filename_keyword_inclusion': 0.06,
            'filename_structure': 0.04,
            
            # Technical optimization (25%)
            'file_size_optimization': 0.08,
            'format_optimization': 0.06,
            'image_dimensions': 0.06,
            'lazy_loading': 0.03,
            'responsive_images': 0.02,
            
            # Context and relevance (15%)
            'surrounding_content_relevance': 0.08,
            'image_context_match': 0.04,
            'page_topic_alignment': 0.03,
            
            # Accessibility (10%)
            'accessibility_compliance': 0.06,
            'screen_reader_compatibility': 0.04
        }
        
    def _load_alt_text_patterns(self) -> Dict[str, List[str]]:
        """Load effective alt text patterns for different image types"""
        return {
            'photography': [
                "{subject} {action} in {location}",
                "{style} photograph of {subject}",
                "{subject} captured in {lighting} lighting",
                "Portrait of {person} {doing_what}",
                "{composition} showing {subject}"
            ],
            'product': [
                "{brand} {product_name} in {color}",
                "{product_type} featuring {key_feature}",
                "{product_name} {product_angle} view",
                "{product_name} with {accessories}",
                "{product_category} by {brand}"
            ],
            'infographic': [
                "Infographic showing {main_topic}",
                "Chart displaying {data_type}",
                "Visual guide to {process}",
                "Statistics about {subject}",
                "Diagram explaining {concept}"
            ],
            'artwork': [
                "{art_style} artwork titled {title}",
                "{medium} artwork by {artist}",
                "Digital art depicting {subject}",
                "{style} illustration of {subject}",
                "Creative artwork showing {theme}"
            ],
            'logo_brand': [
                "{company_name} logo",
                "{brand} official logo design",
                "{company} brand symbol",
                "Logo for {business_type}",
                "{brand_name} visual identity"
            ],
            'screenshot': [
                "Screenshot of {application} {feature}",
                "{software_name} interface showing {function}",
                "Mobile app screenshot of {feature}",
                "Website screenshot displaying {content}",
                "{platform} dashboard view"
            ]
        }
        
    def _load_filename_conventions(self) -> Dict[str, Dict]:
        """Load filename optimization conventions"""
        return {
            'structure': {
                'separator': '-',  # Use hyphens, not underscores
                'case': 'lowercase',
                'max_length': 50,
                'descriptive_words': 3,
                'avoid_characters': ['_', ' ', '&', '%', '#', '@']
            },
            'content_type_prefixes': {
                'product': 'product',
                'portrait': 'portrait',
                'landscape': 'landscape',
                'logo': 'logo',
                'screenshot': 'screenshot',
                'infographic': 'infographic',
                'artwork': 'art'
            },
            'seo_patterns': [
                "{content_type}-{main_keyword}-{descriptor}",
                "{brand}-{product}-{variation}",
                "{keyword}-{quality}-{format}",
                "{location}-{subject}-{style}"
            ]
        }
        
    def _load_technical_guidelines(self) -> Dict[str, Union[int, float, List]]:
        """Load technical optimization guidelines"""
        return {
            'file_size': {
                'hero_images': 150000,  # 150KB max
                'content_images': 100000,  # 100KB max
                'thumbnails': 30000,   # 30KB max
                'icons': 10000         # 10KB max
            },
            'dimensions': {
                'hero_minimum': (1200, 630),
                'content_optimal': (800, 600),
                'thumbnail_standard': (300, 200),
                'square_optimal': (600, 600)
            },
            'formats': {
                'photography': ['webp', 'jpg', 'jpeg'],
                'graphics': ['webp', 'png', 'svg'],
                'icons': ['svg', 'webp', 'png'],
                'screenshots': ['webp', 'png']
            },
            'compression_targets': {
                'webp': 0.8,  # 80% quality
                'jpg': 0.85,  # 85% quality
                'png': None   # Lossless
            }
        }
        
    def _load_platform_requirements(self) -> Dict[str, Dict]:
        """Load platform-specific image requirements"""
        return {
            'google_images': {
                'min_dimensions': (300, 200),
                'max_file_size': 5000000,  # 5MB
                'preferred_formats': ['webp', 'jpg', 'png'],
                'aspect_ratios': ['16:9', '4:3', '1:1'],
                'quality_score_factors': ['alt_text', 'filename', 'context']
            },
            'social_media': {
                'facebook': {'optimal_size': (1200, 630), 'max_size': 8000000},
                'instagram': {'optimal_size': (1080, 1080), 'max_size': 30000000},
                'twitter': {'optimal_size': (1024, 512), 'max_size': 5000000},
                'pinterest': {'optimal_size': (1000, 1500), 'max_size': 10000000}
            },
            'e_commerce': {
                'product_main': {'min_size': (800, 800), 'max_size': 2000000},
                'product_thumb': {'size': (300, 300), 'max_size': 50000},
                'zoom_images': {'min_size': (1600, 1600), 'max_size': 5000000}
            }
        }
        
    def optimize_alt_text(self, image_metadata: ImageMetadata, target_keywords: List[str],
                         image_type: str = None, context: str = "") -> Dict:
        """Optimize image alt text for SEO and accessibility"""
        
        optimization_report = {
            'original_alt_text': image_metadata.alt_text,
            'optimized_alt_text': image_metadata.alt_text,
            'score': 0,
            'improvements': [],
            'keyword_analysis': {},
            'accessibility_analysis': {},
            'length_analysis': {}
        }
        
        current_alt = image_metadata.alt_text or ""
        
        # Length optimization
        alt_length = len(current_alt)
        if alt_length == 0:
            optimization_report['improvements'].append("Add descriptive alt text for SEO and accessibility")
            optimization_report['score'] -= 30
        elif alt_length < 10:
            optimization_report['improvements'].append("Expand alt text to be more descriptive (10+ characters)")
            optimization_report['score'] -= 15
        elif alt_length > 125:
            optimization_report['improvements'].append("Shorten alt text to under 125 characters for screen readers")
            optimization_report['score'] -= 10
        else:
            optimization_report['score'] += 15
            
        optimization_report['length_analysis'] = {
            'current_length': alt_length,
            'optimal_range': '10-125 characters',
            'screen_reader_friendly': alt_length <= 125
        }
        
        # Keyword optimization
        alt_lower = current_alt.lower()
        keywords_found = []
        
        for keyword in target_keywords:
            if keyword.lower() in alt_lower:
                keywords_found.append(keyword)
                optimization_report['score'] += 8
                
        if not keywords_found and target_keywords:
            optimization_report['improvements'].append("Include relevant keywords in alt text naturally")
            optimization_report['score'] -= 15
            
        optimization_report['keyword_analysis'] = {
            'keywords_found': keywords_found,
            'keyword_density': len(keywords_found) / len(target_keywords) if target_keywords else 0
        }
        
        # Accessibility analysis
        accessibility_issues = []
        
        # Check for generic terms
        generic_terms = ['image', 'picture', 'photo', 'graphic', 'icon']
        if any(term in alt_lower for term in generic_terms):
            accessibility_issues.append("Avoid generic terms like 'image' or 'picture'")
            optimization_report['score'] -= 5
            
        # Check for redundancy
        if current_alt.lower().startswith(('image of', 'picture of', 'photo of')):
            accessibility_issues.append("Remove redundant phrases like 'image of'")
            optimization_report['score'] -= 3
            
        # Check for descriptiveness
        word_count = len(current_alt.split())
        if word_count < 3 and alt_length > 0:
            accessibility_issues.append("Use more descriptive language (3+ words)")
            optimization_report['score'] -= 8
        elif word_count >= 5:
            optimization_report['score'] += 8
            
        optimization_report['accessibility_analysis'] = {
            'issues': accessibility_issues,
            'word_count': word_count,
            'descriptiveness_score': min(10, word_count * 2)
        }
        
        # Generate optimized alt text if needed
        if optimization_report['score'] < 70:
            optimized_alt = self._generate_optimized_alt_text(
                image_metadata, target_keywords, image_type, context
            )
            optimization_report['optimized_alt_text'] = optimized_alt
            optimization_report['improvements'].append(f"Suggested alt text: {optimized_alt}")
            
        optimization_report['score'] = max(0, min(100, optimization_report['score']))
        
        return optimization_report
        
    def optimize_filename(self, filename: str, target_keywords: List[str],
                         image_type: str = None) -> Dict:
        """Optimize image filename for SEO"""
        
        optimization_report = {
            'original_filename': filename,
            'optimized_filename': filename,
            'score': 0,
            'improvements': [],
            'structure_analysis': {},
            'keyword_analysis': {}
        }
        
        # Extract filename without extension
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        extension = filename.rsplit('.', 1)[1] if '.' in filename else ''
        
        # Structure analysis
        conventions = self.filename_conventions['structure']
        
        # Check separator usage
        if '_' in name_without_ext:
            optimization_report['improvements'].append("Use hyphens (-) instead of underscores (_)")
            optimization_report['score'] -= 8
        elif '-' in name_without_ext:
            optimization_report['score'] += 5
            
        # Check case
        if name_without_ext != name_without_ext.lower():
            optimization_report['improvements'].append("Use lowercase for better SEO")
            optimization_report['score'] -= 5
        else:
            optimization_report['score'] += 5
            
        # Check length
        if len(name_without_ext) > conventions['max_length']:
            optimization_report['improvements'].append(f"Shorten filename to under {conventions['max_length']} characters")
            optimization_report['score'] -= 10
        elif len(name_without_ext) < 10:
            optimization_report['improvements'].append("Make filename more descriptive (10+ characters)")
            optimization_report['score'] -= 8
        else:
            optimization_report['score'] += 10
            
        # Check for avoid characters
        avoid_chars = conventions['avoid_characters']
        problematic_chars = [char for char in avoid_chars if char in name_without_ext]
        if problematic_chars:
            optimization_report['improvements'].append(f"Remove characters: {problematic_chars}")
            optimization_report['score'] -= 5 * len(problematic_chars)
            
        optimization_report['structure_analysis'] = {
            'uses_hyphens': '-' in name_without_ext,
            'is_lowercase': name_without_ext == name_without_ext.lower(),
            'appropriate_length': 10 <= len(name_without_ext) <= conventions['max_length'],
            'problematic_characters': problematic_chars
        }
        
        # Keyword analysis
        filename_lower = name_without_ext.lower()
        keywords_in_filename = []
        
        for keyword in target_keywords:
            keyword_clean = re.sub(r'[^a-zA-Z0-9]', '-', keyword.lower())
            if keyword_clean in filename_lower or keyword.lower().replace(' ', '-') in filename_lower:
                keywords_in_filename.append(keyword)
                optimization_report['score'] += 10
                
        if not keywords_in_filename and target_keywords:
            optimization_report['improvements'].append("Include target keywords in filename")
            optimization_report['score'] -= 15
            
        optimization_report['keyword_analysis'] = {
            'keywords_found': keywords_in_filename,
            'keyword_inclusion_rate': len(keywords_in_filename) / len(target_keywords) if target_keywords else 0
        }
        
        # Generate optimized filename if needed
        if optimization_report['score'] < 70:
            optimized_filename = self._generate_optimized_filename(
                name_without_ext, extension, target_keywords, image_type
            )
            optimization_report['optimized_filename'] = optimized_filename
            optimization_report['improvements'].append(f"Suggested filename: {optimized_filename}")
            
        optimization_report['score'] = max(0, min(100, optimization_report['score']))
        
        return optimization_report
        
    def analyze_technical_optimization(self, image_metadata: ImageMetadata,
                                     image_purpose: str = 'content') -> Dict:
        """Analyze technical image optimization"""
        
        analysis = {
            'file_size_analysis': {},
            'format_analysis': {},
            'dimensions_analysis': {},
            'compression_analysis': {},
            'score': 0,
            'recommendations': []
        }
        
        guidelines = self.technical_guidelines
        
        # File size analysis
        file_size = image_metadata.file_size
        size_targets = guidelines['file_size']
        target_size = size_targets.get(f'{image_purpose}_images', size_targets['content_images'])
        
        if file_size <= target_size:
            analysis['score'] += 20
        elif file_size <= target_size * 1.5:
            analysis['score'] += 10
            analysis['recommendations'].append(f"Consider reducing file size (current: {file_size//1000}KB, target: {target_size//1000}KB)")
        else:
            analysis['score'] -= 15
            analysis['recommendations'].append(f"File size too large (current: {file_size//1000}KB, target: {target_size//1000}KB)")
            
        analysis['file_size_analysis'] = {
            'current_size': file_size,
            'target_size': target_size,
            'size_ratio': file_size / target_size,
            'optimization_needed': file_size > target_size
        }
        
        # Format analysis
        image_format = image_metadata.format.lower()
        optimal_formats = self._get_optimal_formats_for_content(image_metadata)
        
        if image_format in optimal_formats:
            analysis['score'] += 15
        else:
            analysis['score'] -= 10
            analysis['recommendations'].append(f"Consider using {optimal_formats[0]} format for better optimization")
            
        analysis['format_analysis'] = {
            'current_format': image_format,
            'optimal_formats': optimal_formats,
            'is_optimal': image_format in optimal_formats
        }
        
        # Dimensions analysis
        width, height = image_metadata.dimensions
        dimension_guidelines = guidelines['dimensions']
        
        # Determine if dimensions are appropriate for purpose
        if image_purpose == 'hero':
            min_width, min_height = dimension_guidelines['hero_minimum']
            if width >= min_width and height >= min_height:
                analysis['score'] += 15
            else:
                analysis['score'] -= 10
                analysis['recommendations'].append(f"Increase dimensions for hero image (min: {min_width}x{min_height})")
        elif image_purpose == 'thumbnail':
            target_width, target_height = dimension_guidelines['thumbnail_standard']
            if abs(width - target_width) < 100 and abs(height - target_height) < 100:
                analysis['score'] += 15
            else:
                analysis['score'] -= 5
                analysis['recommendations'].append(f"Optimize dimensions for thumbnails (standard: {target_width}x{target_height})")
                
        # Aspect ratio analysis
        aspect_ratio = width / height if height > 0 else 1
        common_ratios = [16/9, 4/3, 1/1, 3/2]
        closest_ratio = min(common_ratios, key=lambda x: abs(x - aspect_ratio))
        
        if abs(aspect_ratio - closest_ratio) < 0.1:
            analysis['score'] += 5
        else:
            analysis['recommendations'].append(f"Consider standard aspect ratio (current: {aspect_ratio:.2f})")
            
        analysis['dimensions_analysis'] = {
            'current_dimensions': (width, height),
            'aspect_ratio': aspect_ratio,
            'closest_standard_ratio': closest_ratio,
            'dimensions_appropriate': True  # Simplified check
        }
        
        analysis['score'] = max(0, min(100, analysis['score']))
        
        return analysis
        
    def analyze_image_context(self, image_metadata: ImageMetadata,
                             target_keywords: List[str]) -> Dict:
        """Analyze image context and relevance"""
        
        analysis = {
            'relevance_score': 0,
            'context_analysis': {},
            'keyword_context': {},
            'recommendations': []
        }
        
        surrounding_text = image_metadata.surrounding_text or ""
        
        # Analyze surrounding content relevance
        if surrounding_text:
            text_lower = surrounding_text.lower()
            
            # Check keyword presence in surrounding text
            keywords_in_context = []
            for keyword in target_keywords:
                if keyword.lower() in text_lower:
                    keywords_in_context.append(keyword)
                    analysis['relevance_score'] += 10
                    
            # Analyze text relevance to image
            image_descriptors = [
                image_metadata.alt_text or "",
                image_metadata.caption or "",
                image_metadata.title or ""
            ]
            
            combined_descriptors = " ".join(image_descriptors).lower()
            descriptor_words = set(combined_descriptors.split())
            context_words = set(text_lower.split())
            
            word_overlap = len(descriptor_words & context_words)
            total_descriptor_words = len(descriptor_words)
            
            relevance_ratio = word_overlap / total_descriptor_words if total_descriptor_words > 0 else 0
            analysis['relevance_score'] += relevance_ratio * 20
            
            analysis['context_analysis'] = {
                'surrounding_text_length': len(surrounding_text),
                'word_overlap_ratio': relevance_ratio,
                'keywords_in_context': keywords_in_context
            }
        else:
            analysis['recommendations'].append("Add surrounding text context for better image SEO")
            analysis['relevance_score'] -= 10
            
        # Check image-text alignment
        image_alt = image_metadata.alt_text or ""
        image_title = image_metadata.title or ""
        
        if image_alt and image_title:
            # Check consistency between alt text and title
            alt_words = set(image_alt.lower().split())
            title_words = set(image_title.lower().split())
            
            consistency = len(alt_words & title_words) / len(alt_words | title_words) if alt_words | title_words else 0
            if consistency > 0.5:
                analysis['relevance_score'] += 10
            else:
                analysis['recommendations'].append("Improve consistency between alt text and title")
                
        analysis['relevance_score'] = max(0, min(100, analysis['relevance_score']))
        
        return analysis
        
    def generate_comprehensive_image_report(self, image_metadata: ImageMetadata,
                                          target_keywords: List[str],
                                          image_type: str = None,
                                          image_purpose: str = 'content') -> ImageOptimizationReport:
        """Generate comprehensive image SEO optimization report"""
        
        # Analyze individual components
        alt_text_analysis = self.optimize_alt_text(image_metadata, target_keywords, image_type)
        filename_analysis = self.optimize_filename(image_metadata.filename, target_keywords, image_type)
        technical_analysis = self.analyze_technical_optimization(image_metadata, image_purpose)
        context_analysis = self.analyze_image_context(image_metadata, target_keywords)
        
        # Calculate component scores
        alt_text_score = alt_text_analysis['score']
        filename_score = filename_analysis['score']
        technical_score = technical_analysis['score']
        context_score = context_analysis['relevance_score']
        
        # Calculate accessibility score
        accessibility_score = self._calculate_accessibility_score(image_metadata, alt_text_analysis)
        
        # Calculate overall score
        overall_score = (
            alt_text_score * 0.30 +
            filename_score * 0.20 +
            technical_score * 0.25 +
            context_score * 0.15 +
            accessibility_score * 0.10
        )
        
        # Compile recommendations
        recommendations = []
        recommendations.extend(alt_text_analysis.get('improvements', []))
        recommendations.extend(filename_analysis.get('improvements', []))
        recommendations.extend(technical_analysis.get('recommendations', []))
        recommendations.extend(context_analysis.get('recommendations', []))
        
        # Generate SEO opportunities
        seo_opportunities = self._identify_seo_opportunities(
            image_metadata, target_keywords, image_type
        )
        
        return ImageOptimizationReport(
            image_url=image_metadata.context_url,
            overall_score=round(overall_score, 1),
            alt_text_score=alt_text_score,
            filename_score=filename_score,
            technical_score=technical_score,
            context_score=context_score,
            accessibility_score=accessibility_score,
            recommendations=recommendations[:10],  # Top 10 recommendations
            optimized_alt_text=alt_text_analysis.get('optimized_alt_text', image_metadata.alt_text),
            optimized_filename=filename_analysis.get('optimized_filename', image_metadata.filename),
            seo_opportunities=seo_opportunities
        )
        
    # Utility methods
    def _generate_optimized_alt_text(self, image_metadata: ImageMetadata,
                                   target_keywords: List[str], image_type: str = None,
                                   context: str = "") -> str:
        """Generate optimized alt text"""
        
        if not target_keywords:
            return image_metadata.alt_text or "Descriptive image"
            
        primary_keyword = target_keywords[0]
        
        # Use type-specific patterns if available
        if image_type and image_type in self.alt_text_patterns:
            patterns = self.alt_text_patterns[image_type]
            # For this example, use a simple pattern
            if image_type == 'product':
                return f"{primary_keyword} showing key features"
            elif image_type == 'photography':
                return f"Professional photograph featuring {primary_keyword}"
            elif image_type == 'infographic':
                return f"Infographic displaying {primary_keyword} information"
                
        # Default optimization
        filename_base = image_metadata.filename.rsplit('.', 1)[0]
        descriptive_words = re.sub(r'[^a-zA-Z0-9\s]', ' ', filename_base).split()
        
        if len(descriptive_words) > 1:
            return f"{primary_keyword} {' '.join(descriptive_words[:3])}"
        else:
            return f"Image showing {primary_keyword}"
            
    def _generate_optimized_filename(self, current_name: str, extension: str,
                                   target_keywords: List[str], image_type: str = None) -> str:
        """Generate optimized filename"""
        
        if not target_keywords:
            return f"{current_name}.{extension}"
            
        primary_keyword = target_keywords[0]
        keyword_clean = re.sub(r'[^a-zA-Z0-9]', '-', primary_keyword.lower())
        
        # Add type prefix if specified
        prefix = ""
        if image_type and image_type in self.filename_conventions['content_type_prefixes']:
            prefix = self.filename_conventions['content_type_prefixes'][image_type] + "-"
            
        # Create descriptive suffix
        current_words = re.sub(r'[^a-zA-Z0-9]', '-', current_name.lower()).split('-')
        useful_words = [word for word in current_words if len(word) > 2 and word not in keyword_clean]
        
        suffix = ""
        if useful_words:
            suffix = "-" + useful_words[0]
            
        optimized_name = f"{prefix}{keyword_clean}{suffix}"
        
        # Ensure length limit
        max_length = self.filename_conventions['structure']['max_length']
        if len(optimized_name) > max_length:
            optimized_name = optimized_name[:max_length]
            
        return f"{optimized_name}.{extension}"
        
    def _get_optimal_formats_for_content(self, image_metadata: ImageMetadata) -> List[str]:
        """Get optimal image formats based on content type"""
        
        # Analyze image characteristics
        width, height = image_metadata.dimensions
        file_size = image_metadata.file_size
        current_format = image_metadata.format.lower()
        
        # Determine content type based on characteristics
        if file_size < 50000 and (width < 400 or height < 400):
            # Small images - icons, thumbnails
            return ['webp', 'png', 'svg']
        elif current_format in ['png'] and file_size > 200000:
            # Large PNG - likely needs compression
            return ['webp', 'jpg']
        elif width > 1200 or height > 1200:
            # Large images - photography
            return ['webp', 'jpg']
        else:
            # General content images
            return ['webp', 'jpg', 'png']
            
    def _calculate_accessibility_score(self, image_metadata: ImageMetadata,
                                     alt_text_analysis: Dict) -> float:
        """Calculate accessibility compliance score"""
        
        score = 50  # Base score
        
        # Alt text presence and quality
        if image_metadata.alt_text:
            score += 30
            
            # Check alt text quality
            accessibility_analysis = alt_text_analysis.get('accessibility_analysis', {})
            if not accessibility_analysis.get('issues', []):
                score += 15
            else:
                score -= len(accessibility_analysis['issues']) * 3
                
        else:
            score -= 40
            
        # Caption presence
        if image_metadata.caption:
            score += 5
            
        # Title presence
        if image_metadata.title:
            score += 5
            
        return max(0, min(100, score))
        
    def _identify_seo_opportunities(self, image_metadata: ImageMetadata,
                                  target_keywords: List[str], image_type: str = None) -> List[str]:
        """Identify additional SEO opportunities"""
        
        opportunities = []
        
        # Structured data opportunities
        if not image_metadata.structured_data:
            opportunities.append("Add structured data markup (ImageObject schema)")
            
        # Caption optimization
        if not image_metadata.caption:
            opportunities.append("Add descriptive caption for additional context")
        elif image_metadata.caption and not any(kw.lower() in image_metadata.caption.lower() for kw in target_keywords):
            opportunities.append("Include keywords in image caption")
            
        # Title optimization
        if not image_metadata.title:
            opportunities.append("Add image title attribute for hover text")
            
        # Social media optimization
        if image_metadata.dimensions[0] < 1200:
            opportunities.append("Create larger version for social media sharing")
            
        # Mobile optimization
        if image_metadata.file_size > 100000:
            opportunities.append("Create mobile-optimized version with smaller file size")
            
        # Platform-specific opportunities
        if image_type == 'product':
            opportunities.append("Consider multiple angles and zoom functionality")
        elif image_type == 'photography':
            opportunities.append("Add EXIF data optimization for photography portfolios")
            
        return opportunities[:8]  # Limit to top 8 opportunities


# Integration utilities
def create_ainflue_image_seo_optimizer() -> ImageSEOOptimizer:
    """Create configured image SEO optimizer for Ainflue"""
    return ImageSEOOptimizer()


if __name__ == "__main__":
    # Example usage
    optimizer = create_ainflue_image_seo_optimizer()
    
    # Sample image metadata
    image_metadata = ImageMetadata(
        filename="DSC_1234.jpg",
        alt_text="photo",
        title="",
        caption="",
        file_size=250000,  # 250KB
        dimensions=(1200, 800),
        format="jpg",
        context_url="https://ainflue.com/portfolio/photography",
        surrounding_text="This amazing landscape photo was taken during golden hour in the mountains."
    )
    
    target_keywords = ["landscape photography", "mountain sunset", "golden hour"]
    
    # Generate optimization report
    report = optimizer.generate_comprehensive_image_report(
        image_metadata, target_keywords, "photography", "content"
    )
    
    print(f"Image SEO Optimization Report")
    print(f"Overall Score: {report.overall_score}/100")
    print(f"Alt Text Score: {report.alt_text_score}/100")
    print(f"Filename Score: {report.filename_score}/100")
    print(f"Technical Score: {report.technical_score}/100")
    print(f"Context Score: {report.context_score}/100")
    print(f"Accessibility Score: {report.accessibility_score}/100")
    
    print(f"\nOptimized Alt Text: {report.optimized_alt_text}")
    print(f"Optimized Filename: {report.optimized_filename}")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(report.recommendations[:5], 1):
        print(f"{i}. {rec}")
        
    print("\nSEO Opportunities:")
    for opportunity in report.seo_opportunities[:5]:
        print(f"- {opportunity}")