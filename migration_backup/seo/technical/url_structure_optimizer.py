"""URL Structure Optimizer
Advanced URL structure optimization system for SEO and user experience.

Features:
- SEO-friendly URL generation and validation
- URL parameter management and optimization
- Redirect chain optimization and detection
- URL canonicalization automation
- Slug optimization for creators and content
- Category structure enhancement
- Breadcrumb implementation support
- Navigation structure optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior + DevOps expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)

class URLType(Enum):
    """Types of URLs in the system."""
    HOMEPAGE = "homepage"
    CATEGORY = "category"
    CREATOR_PROFILE = "creator_profile"
    CREATOR_CONTENT = "creator_content"
    PRODUCT = "product"
    SERVICE = "service"
    BLOG_POST = "blog_post"
    STATIC_PAGE = "static_page"
    SEARCH_RESULTS = "search_results"
    API_ENDPOINT = "api_endpoint"

class RedirectType(Enum):
    """Types of redirects."""
    PERMANENT_301 = "301"
    TEMPORARY_302 = "302"
    SEE_OTHER_303 = "303"
    TEMPORARY_307 = "307"
    PERMANENT_308 = "308"

class URLStructurePattern(Enum):
    """URL structure patterns."""
    HIERARCHICAL = "hierarchical"  # /category/subcategory/item
    FLAT = "flat"  # /item-name
    PARAMETRIC = "parametric"  # /page?param=value
    HYBRID = "hybrid"  # Mix of patterns
    CREATOR_CENTRIC = "creator_centric"  # /creator/content-type/item

@dataclass
class URLAnalysis:
    """URL structure analysis results."""
    url: str
    url_type: URLType
    is_seo_friendly: bool
    seo_score: int
    structure_issues: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    redirect_chain: List[str] = field(default_factory=list)
    parameters: Dict[str, str] = field(default_factory=dict)
    creator_id: Optional[str] = None

@dataclass
class SlugOptimization:
    """Slug optimization configuration."""
    max_length: int = 60
    include_keywords: bool = True
    remove_stop_words: bool = True
    use_hyphens: bool = True
    lowercase_only: bool = True
    remove_special_chars: bool = True
    include_creator_name: bool = False
    include_content_type: bool = False

@dataclass
class URLRedirect:
    """URL redirect configuration."""
    source_url: str
    target_url: str
    redirect_type: RedirectType
    is_permanent: bool
    created_at: datetime
    reason: str = ""
    creator_id: Optional[str] = None
    is_active: bool = True

@dataclass
class BreadcrumbStructure:
    """Breadcrumb navigation structure."""
    levels: List[Dict[str, str]] = field(default_factory=list)
    schema_markup: Dict[str, Any] = field(default_factory=dict)
    is_seo_optimized: bool = False

class URLStructureOptimizer:
    """
    Enterprise URL structure optimization system for SEO and UX enhancement.
    Provides comprehensive URL management for creator economy platform.
    """
    
    def __init__(self, 
                 base_domain: str,
                 structure_pattern: URLStructurePattern = URLStructurePattern.HIERARCHICAL):
        self.base_domain = base_domain.rstrip('/')
        self.structure_pattern = structure_pattern
        self.url_analyses: List[URLAnalysis] = []
        self.redirect_rules: List[URLRedirect] = []
        self.slug_config = SlugOptimization()
        self.reserved_words = {'admin', 'api', 'www', 'mail', 'ftp', 'blog', 'help', 'support'}
        
    async def analyze_url_structure(self, 
                                  url: str,
                                  url_type: URLType = URLType.STATIC_PAGE,
                                  creator_id: Optional[str] = None) -> URLAnalysis:
        """
        Analyze URL structure for SEO and usability.
        
        Args:
            url: URL to analyze
            url_type: Type of URL
            creator_id: Associated creator ID
            
        Returns:
            URL analysis results
        """
        try:
            analysis = URLAnalysis(
                url=url,
                url_type=url_type,
                is_seo_friendly=False,
                seo_score=0,
                creator_id=creator_id
            )
            
            # Parse URL components
            parsed_url = urlparse(url)
            analysis.parameters = parse_qs(parsed_url.query)
            
            # Analyze URL structure
            structure_score = await self._analyze_url_structure_quality(url, url_type)
            analysis.seo_score = structure_score['score']
            analysis.structure_issues = structure_score['issues']
            analysis.optimization_suggestions = structure_score['suggestions']
            
            # Check SEO friendliness
            analysis.is_seo_friendly = analysis.seo_score >= 80
            
            # Detect redirect chains
            analysis.redirect_chain = await self._detect_redirect_chain(url)
            
            # Generate canonical URL
            analysis.canonical_url = await self._generate_canonical_url(url, url_type)
            
            # Store analysis
            self.url_analyses.append(analysis)
            
            logger.info(f"URL analysis completed for {url}: Score {analysis.seo_score}/100")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing URL structure for {url}: {str(e)}")
            raise
    
    async def optimize_url_structure(self,
                                   current_url: str,
                                   target_type: URLType,
                                   content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize URL structure for SEO and user experience.
        
        Args:
            current_url: Current URL to optimize
            target_type: Target URL type
            content_data: Content metadata for optimization
            
        Returns:
            URL optimization results
        """
        try:
            optimization_results = {
                'current_url': current_url,
                'optimized_url': '',
                'optimization_type': target_type.value,
                'improvements': [],
                'redirect_needed': False,
                'redirect_config': {},
                'seo_impact': {},
                'implementation_steps': []
            }
            
            # Generate optimized URL
            optimized_url = await self._generate_optimized_url(
                current_url, target_type, content_data
            )
            optimization_results['optimized_url'] = optimized_url
            
            # Compare URLs
            if current_url != optimized_url:
                optimization_results['redirect_needed'] = True
                
                # Create redirect configuration
                redirect_config = await self._create_redirect_configuration(
                    current_url, optimized_url, target_type
                )
                optimization_results['redirect_config'] = redirect_config
                
                # Calculate SEO impact
                seo_impact = await self._calculate_seo_impact(
                    current_url, optimized_url, target_type
                )
                optimization_results['seo_impact'] = seo_impact
            
            # Generate implementation steps
            optimization_results['implementation_steps'] = self._generate_implementation_steps(
                optimization_results
            )
            
            # Track improvements
            optimization_results['improvements'] = await self._identify_url_improvements(
                current_url, optimized_url, target_type
            )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing URL structure for {current_url}: {str(e)}")
            raise
    
    async def generate_creator_url_structure(self,
                                           creator_id: str,
                                           creator_data: Dict[str, Any],
                                           content_types: List[str]) -> Dict[str, Any]:
        """
        Generate optimized URL structure for creator and their content.
        
        Args:
            creator_id: Creator identifier
            creator_data: Creator metadata
            content_types: Types of content to structure
            
        Returns:
            Creator URL structure plan
        """
        try:
            url_structure = {
                'creator_id': creator_id,
                'base_structure': {},
                'content_structures': {},
                'navigation_hierarchy': {},
                'breadcrumb_configs': {},
                'seo_optimizations': {}
            }
            
            # Generate base creator structure
            creator_username = creator_data.get('username', creator_id)
            creator_slug = self._generate_seo_slug(creator_username)
            
            base_structure = {
                'profile_url': f"{self.base_domain}/creator/{creator_slug}",
                'content_base': f"{self.base_domain}/creator/{creator_slug}",
                'public_api': f"{self.base_domain}/api/creator/{creator_slug}"
            }
            url_structure['base_structure'] = base_structure
            
            # Generate content type structures
            for content_type in content_types:
                content_structure = await self._generate_content_type_structure(
                    creator_slug, content_type, creator_data
                )
                url_structure['content_structures'][content_type] = content_structure
            
            # Create navigation hierarchy
            url_structure['navigation_hierarchy'] = await self._create_navigation_hierarchy(
                creator_slug, content_types, creator_data
            )
            
            # Generate breadcrumb configurations
            url_structure['breadcrumb_configs'] = await self._generate_breadcrumb_configs(
                creator_slug, content_types
            )
            
            # Apply SEO optimizations
            url_structure['seo_optimizations'] = await self._apply_creator_seo_optimizations(
                creator_id, url_structure
            )
            
            return url_structure
            
        except Exception as e:
            logger.error(f"Error generating creator URL structure for {creator_id}: {str(e)}")
            raise
    
    async def optimize_site_navigation_structure(self,
                                               site_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize entire site navigation structure.
        
        Args:
            site_structure: Current site structure
            
        Returns:
            Optimized navigation structure
        """
        try:
            optimization_results = {
                'current_structure': site_structure,
                'optimized_structure': {},
                'navigation_improvements': [],
                'url_consolidations': [],
                'redirect_recommendations': [],
                'seo_enhancements': {}
            }
            
            # Analyze current structure
            structure_analysis = await self._analyze_site_structure(site_structure)
            
            # Optimize navigation hierarchy
            optimized_nav = await self._optimize_navigation_hierarchy(
                site_structure, structure_analysis
            )
            optimization_results['optimized_structure'] = optimized_nav
            
            # Identify URL consolidation opportunities
            consolidations = await self._identify_url_consolidations(site_structure)
            optimization_results['url_consolidations'] = consolidations
            
            # Generate redirect recommendations
            redirect_recommendations = await self._generate_redirect_recommendations(
                site_structure, optimized_nav
            )
            optimization_results['redirect_recommendations'] = redirect_recommendations
            
            # Apply SEO enhancements
            seo_enhancements = await self._apply_site_seo_enhancements(optimized_nav)
            optimization_results['seo_enhancements'] = seo_enhancements
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing site navigation structure: {str(e)}")
            raise
    
    async def manage_url_redirects(self,
                                 redirect_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manage URL redirects for SEO and user experience.
        
        Args:
            redirect_rules: List of redirect rules to implement
            
        Returns:
            Redirect management results
        """
        try:
            management_results = {
                'total_redirects': len(redirect_rules),
                'redirects_processed': 0,
                'redirect_chains_resolved': 0,
                'seo_improvements': {},
                'implementation_config': {},
                'monitoring_setup': {}
            }
            
            processed_redirects = []
            
            for rule_data in redirect_rules:
                try:
                    # Create redirect rule
                    redirect = URLRedirect(
                        source_url=rule_data['source'],
                        target_url=rule_data['target'],
                        redirect_type=RedirectType(rule_data.get('type', '301')),
                        is_permanent=rule_data.get('permanent', True),
                        created_at=datetime.now(),
                        reason=rule_data.get('reason', 'URL optimization'),
                        creator_id=rule_data.get('creator_id')
                    )
                    
                    # Validate redirect
                    validation_result = await self._validate_redirect_rule(redirect)
                    
                    if validation_result['valid']:
                        self.redirect_rules.append(redirect)
                        processed_redirects.append(redirect)
                        management_results['redirects_processed'] += 1
                    else:
                        logger.warning(f"Invalid redirect rule: {validation_result['reason']}")
                
                except Exception as e:
                    logger.error(f"Error processing redirect rule: {str(e)}")
                    continue
            
            # Resolve redirect chains
            chain_resolutions = await self._resolve_redirect_chains(processed_redirects)
            management_results['redirect_chains_resolved'] = chain_resolutions['resolved_chains']
            
            # Calculate SEO improvements
            seo_improvements = await self._calculate_redirect_seo_improvements(processed_redirects)
            management_results['seo_improvements'] = seo_improvements
            
            # Generate implementation configuration
            implementation_config = self._generate_redirect_implementation_config(processed_redirects)
            management_results['implementation_config'] = implementation_config
            
            # Setup monitoring
            monitoring_config = self._setup_redirect_monitoring(processed_redirects)
            management_results['monitoring_setup'] = monitoring_config
            
            return management_results
            
        except Exception as e:
            logger.error(f"Error managing URL redirects: {str(e)}")
            raise
    
    async def generate_breadcrumb_navigation(self,
                                           url: str,
                                           page_data: Dict[str, Any]) -> BreadcrumbStructure:
        """
        Generate SEO-optimized breadcrumb navigation.
        
        Args:
            url: Current page URL
            page_data: Page metadata
            
        Returns:
            Breadcrumb structure with schema markup
        """
        try:
            # Parse URL to determine hierarchy
            parsed_url = urlparse(url)
            path_segments = [seg for seg in parsed_url.path.strip('/').split('/') if seg]
            
            breadcrumb = BreadcrumbStructure()
            
            # Build breadcrumb levels
            current_path = ''
            for i, segment in enumerate(path_segments):
                current_path += f'/{segment}'
                
                # Generate human-readable name
                breadcrumb_name = self._generate_breadcrumb_name(segment, i, page_data)
                breadcrumb_url = f"{self.base_domain}{current_path}"
                
                breadcrumb.levels.append({
                    'name': breadcrumb_name,
                    'url': breadcrumb_url,
                    'position': i + 2  # Start from 2 (home is 1)
                })
            
            # Add home as first level
            breadcrumb.levels.insert(0, {
                'name': 'Home',
                'url': self.base_domain,
                'position': 1
            })
            
            # Generate schema markup
            breadcrumb.schema_markup = self._generate_breadcrumb_schema_markup(breadcrumb.levels)
            
            # Mark as SEO optimized
            breadcrumb.is_seo_optimized = True
            
            return breadcrumb
            
        except Exception as e:
            logger.error(f"Error generating breadcrumb navigation for {url}: {str(e)}")
            return BreadcrumbStructure()
    
    async def _analyze_url_structure_quality(self,
                                           url: str,
                                           url_type: URLType) -> Dict[str, Any]:
        """Analyze URL structure quality and generate recommendations."""
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        score = 100
        issues = []
        suggestions = []
        
        # Check URL length
        if len(url) > 255:
            score -= 20
            issues.append('URL too long (>255 characters)')
            suggestions.append('Shorten URL length for better usability')
        elif len(url) > 100:
            score -= 10
            issues.append('URL moderately long (>100 characters)')
            suggestions.append('Consider shortening URL for better readability')
        
        # Check for SEO-friendly structure
        if not re.match(r'^[a-zA-Z0-9\-_/.]+$', path):
            score -= 15
            issues.append('URL contains non-SEO-friendly characters')
            suggestions.append('Use only letters, numbers, hyphens, and underscores')
        
        # Check for keyword presence
        if url_type in [URLType.CREATOR_CONTENT, URLType.BLOG_POST]:
            if len(path.split('/')) < 3:
                score -= 10
                issues.append('URL structure lacks depth for content classification')
                suggestions.append('Add category/subcategory structure')
        
        # Check for parameters
        if parsed_url.query:
            params = parse_qs(parsed_url.query)
            if len(params) > 3:
                score -= 15
                issues.append('Too many URL parameters')
                suggestions.append('Reduce URL parameters or use clean URLs')
        
        # Check for trailing slash consistency
        if path.endswith('/') and url_type not in [URLType.CATEGORY, URLType.HOMEPAGE]:
            score -= 5
            issues.append('Inconsistent trailing slash usage')
            suggestions.append('Standardize trailing slash usage')
        
        # Check for reserved words
        path_segments = path.strip('/').split('/')
        for segment in path_segments:
            if segment.lower() in self.reserved_words:
                score -= 10
                issues.append(f'URL uses reserved word: {segment}')
                suggestions.append(f'Avoid using reserved word "{segment}" in URLs')
        
        # Creator-specific checks
        if url_type == URLType.CREATOR_PROFILE:
            if 'creator' not in path.lower() and 'profile' not in path.lower():
                score -= 10
                issues.append('Creator profile URL lacks clear identification')
                suggestions.append('Include "creator" or "profile" in URL structure')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions
        }
    
    async def _detect_redirect_chain(self, url: str) -> List[str]:
        """Detect redirect chains for URL."""
        # Simulate redirect chain detection
        # In real implementation, follow redirects to detect chains
        
        redirect_chain = [url]
        
        # Check if URL is in redirect rules
        for redirect in self.redirect_rules:
            if redirect.source_url == url and redirect.is_active:
                redirect_chain.append(redirect.target_url)
                # Recursively check for further redirects
                further_redirects = await self._detect_redirect_chain(redirect.target_url)
                redirect_chain.extend(further_redirects[1:])  # Exclude duplicate
                break
        
        return redirect_chain
    
    async def _generate_canonical_url(self, url: str, url_type: URLType) -> str:
        """Generate canonical URL for given URL."""
        parsed_url = urlparse(url)
        
        # Remove common parameter variations
        clean_path = parsed_url.path.rstrip('/')
        
        # Remove session and tracking parameters
        query_params = parse_qs(parsed_url.query)
        clean_params = {k: v for k, v in query_params.items() 
                       if k not in ['utm_source', 'utm_medium', 'utm_campaign', 'sessionid', 'fbclid']}
        
        clean_query = urlencode(clean_params, doseq=True) if clean_params else ''
        
        canonical_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            clean_path,
            parsed_url.params,
            clean_query,
            ''  # Remove fragment
        ))
        
        return canonical_url
    
    async def _generate_optimized_url(self,
                                    current_url: str,
                                    target_type: URLType,
                                    content_data: Dict[str, Any]) -> str:
        """Generate optimized URL based on type and content."""
        if target_type == URLType.CREATOR_PROFILE:
            creator_name = content_data.get('name', content_data.get('username', 'creator'))
            slug = self._generate_seo_slug(creator_name)
            return f"{self.base_domain}/creator/{slug}"
        
        elif target_type == URLType.CREATOR_CONTENT:
            creator_slug = self._generate_seo_slug(content_data.get('creator', 'creator'))
            content_slug = self._generate_seo_slug(content_data.get('title', 'content'))
            content_type = content_data.get('type', 'content')
            return f"{self.base_domain}/creator/{creator_slug}/{content_type}/{content_slug}"
        
        elif target_type == URLType.CATEGORY:
            category_name = content_data.get('name', 'category')
            slug = self._generate_seo_slug(category_name)
            return f"{self.base_domain}/category/{slug}"
        
        elif target_type == URLType.BLOG_POST:
            title = content_data.get('title', 'post')
            slug = self._generate_seo_slug(title)
            return f"{self.base_domain}/blog/{slug}"
        
        else:
            # Default optimization
            parsed_url = urlparse(current_url)
            path_segments = [seg for seg in parsed_url.path.strip('/').split('/') if seg]
            optimized_segments = [self._generate_seo_slug(seg) for seg in path_segments]
            return f"{self.base_domain}/{'/'.join(optimized_segments)}"
    
    def _generate_seo_slug(self, text: str) -> str:
        """Generate SEO-friendly slug from text."""
        if not text:
            return ''
        
        # Convert to lowercase
        slug = text.lower()
        
        # Remove special characters
        if self.slug_config.remove_special_chars:
            slug = re.sub(r'[^\w\s-]', '', slug)
        
        # Replace spaces with hyphens
        if self.slug_config.use_hyphens:
            slug = re.sub(r'[\s_]+', '-', slug)
        
        # Remove stop words
        if self.slug_config.remove_stop_words:
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those'}
            words = slug.split('-')
            words = [word for word in words if word not in stop_words or len(words) <= 2]
            slug = '-'.join(words)
        
        # Trim to max length
        if len(slug) > self.slug_config.max_length:
            slug = slug[:self.slug_config.max_length].rstrip('-')
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug or 'content'
    
    async def _create_redirect_configuration(self,
                                           source_url: str,
                                           target_url: str,
                                           url_type: URLType) -> Dict[str, Any]:
        """Create redirect configuration."""
        return {
            'source': source_url,
            'target': target_url,
            'type': '301',  # Permanent redirect for SEO
            'reason': f'URL optimization for {url_type.value}',
            'implementation_methods': {
                'htaccess': f'Redirect 301 {urlparse(source_url).path} {target_url}',
                'nginx': f'rewrite ^{urlparse(source_url).path}$ {target_url} permanent;',
                'apache': f'RedirectMatch 301 ^{urlparse(source_url).path}$ {target_url}'
            },
            'seo_considerations': [
                'Preserves link equity',
                'Maintains search rankings',
                'Improves user experience'
            ]
        }
    
    async def _calculate_seo_impact(self,
                                  current_url: str,
                                  optimized_url: str,
                                  url_type: URLType) -> Dict[str, Any]:
        """Calculate SEO impact of URL optimization."""
        current_analysis = await self._analyze_url_structure_quality(current_url, url_type)
        optimized_analysis = await self._analyze_url_structure_quality(optimized_url, url_type)
        
        score_improvement = optimized_analysis['score'] - current_analysis['score']
        
        return {
            'current_score': current_analysis['score'],
            'optimized_score': optimized_analysis['score'],
            'improvement': score_improvement,
            'impact_level': 'high' if score_improvement > 20 else 'medium' if score_improvement > 10 else 'low',
            'benefits': [
                'Improved search engine crawlability',
                'Better user experience',
                'Enhanced keyword relevance',
                'Reduced bounce rate potential'
            ] if score_improvement > 0 else ['Minimal impact expected']
        }
    
    def _generate_implementation_steps(self, optimization_results: Dict[str, Any]) -> List[str]:
        """Generate implementation steps for URL optimization."""
        steps = []
        
        if optimization_results['redirect_needed']:
            steps.extend([
                'Create 301 redirect from old URL to new URL',
                'Update internal links to point to new URL',
                'Update sitemap with new URL structure',
                'Monitor traffic and rankings after implementation'
            ])
        
        steps.extend([
            'Validate new URL structure in testing environment',
            'Update canonical tags if applicable',
            'Update social media sharing URLs',
            'Inform search engines of URL changes via Search Console'
        ])
        
        return steps
    
    async def _identify_url_improvements(self,
                                       current_url: str,
                                       optimized_url: str,
                                       url_type: URLType) -> List[str]:
        """Identify specific improvements in URL optimization."""
        improvements = []
        
        current_parsed = urlparse(current_url)
        optimized_parsed = urlparse(optimized_url)
        
        # Path improvements
        if len(optimized_parsed.path) < len(current_parsed.path):
            improvements.append('Shortened URL path for better readability')
        
        if '-' in optimized_parsed.path and '_' in current_parsed.path:
            improvements.append('Replaced underscores with SEO-friendly hyphens')
        
        if optimized_parsed.path.lower() == optimized_parsed.path and current_parsed.path != current_parsed.path.lower():
            improvements.append('Standardized to lowercase for consistency')
        
        # Parameter improvements
        current_params = parse_qs(current_parsed.query)
        optimized_params = parse_qs(optimized_parsed.query)
        
        if len(optimized_params) < len(current_params):
            improvements.append('Reduced URL parameters for cleaner structure')
        
        # Structure improvements
        if url_type == URLType.CREATOR_CONTENT:
            if '/creator/' in optimized_url and '/creator/' not in current_url:
                improvements.append('Added creator identification to URL structure')
        
        return improvements
    
    async def _generate_content_type_structure(self,
                                             creator_slug: str,
                                             content_type: str,
                                             creator_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate URL structure for specific content type."""
        base_path = f"/creator/{creator_slug}/{content_type}"
        
        return {
            'list_url': f"{self.base_domain}{base_path}",
            'item_url_pattern': f"{self.base_domain}{base_path}/{{slug}}",
            'category_url_pattern': f"{self.base_domain}{base_path}/category/{{category}}",
            'tag_url_pattern': f"{self.base_domain}{base_path}/tag/{{tag}}",
            'archive_url_pattern': f"{self.base_domain}{base_path}/archive/{{date}}"
        }
    
    async def _create_navigation_hierarchy(self,
                                         creator_slug: str,
                                         content_types: List[str],
                                         creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create navigation hierarchy for creator."""
        hierarchy = {
            'root': f"/creator/{creator_slug}",
            'levels': [
                {
                    'name': 'Creator Profile',
                    'url': f"/creator/{creator_slug}",
                    'level': 1
                }
            ]
        }
        
        # Add content type levels
        for i, content_type in enumerate(content_types):
            hierarchy['levels'].append({
                'name': content_type.title(),
                'url': f"/creator/{creator_slug}/{content_type}",
                'level': 2,
                'parent': f"/creator/{creator_slug}"
            })
        
        return hierarchy
    
    async def _generate_breadcrumb_configs(self,
                                         creator_slug: str,
                                         content_types: List[str]) -> Dict[str, Any]:
        """Generate breadcrumb configurations for creator pages."""
        configs = {}
        
        # Profile breadcrumb
        configs['profile'] = {
            'pattern': 'Home > Creators > {creator_name}',
            'schema_type': 'BreadcrumbList',
            'levels': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Creators', 'url': '/creators'},
                {'name': '{creator_name}', 'url': f'/creator/{creator_slug}'}
            ]
        }
        
        # Content type breadcrumbs
        for content_type in content_types:
            configs[content_type] = {
                'pattern': f'Home > Creators > {{creator_name}} > {content_type.title()}',
                'schema_type': 'BreadcrumbList',
                'levels': [
                    {'name': 'Home', 'url': '/'},
                    {'name': 'Creators', 'url': '/creators'},
                    {'name': '{creator_name}', 'url': f'/creator/{creator_slug}'},
                    {'name': content_type.title(), 'url': f'/creator/{creator_slug}/{content_type}'}
                ]
            }
        
        return configs
    
    async def _apply_creator_seo_optimizations(self,
                                             creator_id: str,
                                             url_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply SEO optimizations to creator URL structure."""
        return {
            'canonical_urls': {
                structure_type: self._generate_canonical_for_structure(urls)
                for structure_type, urls in url_structure['content_structures'].items()
            },
            'meta_tags': {
                'profile': {
                    'title_pattern': '{creator_name} - Creator Profile | IA Chéries',
                    'description_pattern': 'Discover content from {creator_name} on IA Chéries. {creator_bio}',
                    'keywords_pattern': '{creator_name}, creator, {content_types}'
                }
            },
            'structured_data': {
                'person_schema': True,
                'creator_schema': True,
                'breadcrumb_schema': True
            },
            'social_sharing': {
                'og_url_pattern': '{base_url}/creator/{creator_slug}',
                'twitter_url_pattern': '{base_url}/creator/{creator_slug}'
            }
        }
    
    def _generate_canonical_for_structure(self, structure_urls: Dict[str, str]) -> Dict[str, str]:
        """Generate canonical URLs for structure."""
        canonical_urls = {}
        
        for url_type, url_pattern in structure_urls.items():
            # Remove parameters and ensure trailing slash consistency
            canonical_urls[url_type] = url_pattern.split('?')[0].rstrip('/')
        
        return canonical_urls
    
    async def _analyze_site_structure(self, site_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current site structure for optimization opportunities."""
        analysis = {
            'depth_analysis': {},
            'url_patterns': {},
            'duplicate_content_risks': [],
            'navigation_issues': [],
            'seo_opportunities': []
        }
        
        # Analyze URL depth
        urls = site_structure.get('urls', [])
        depth_counts = defaultdict(int)
        
        for url in urls:
            depth = len(urlparse(url).path.strip('/').split('/'))
            depth_counts[depth] += 1
        
        analysis['depth_analysis'] = dict(depth_counts)
        
        # Identify navigation issues
        if depth_counts.get(5, 0) > depth_counts.get(2, 0):
            analysis['navigation_issues'].append('Too many deep-level pages')
        
        # SEO opportunities
        if depth_counts.get(1, 0) < 5:
            analysis['seo_opportunities'].append('Add more top-level category pages')
        
        return analysis
    
    async def _optimize_navigation_hierarchy(self,
                                           current_structure: Dict[str, Any],
                                           analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize navigation hierarchy based on analysis."""
        optimized_structure = current_structure.copy()
        
        # Restructure based on analysis
        if 'Too many deep-level pages' in analysis['navigation_issues']:
            # Flatten deep hierarchies
            optimized_structure['max_depth'] = 4
            optimized_structure['restructuring_needed'] = True
        
        # Add missing category levels
        if 'Add more top-level category pages' in analysis['seo_opportunities']:
            optimized_structure['add_categories'] = [
                'Popular Creators',
                'Content Categories',
                'Trending Topics'
            ]
        
        return optimized_structure
    
    async def _identify_url_consolidations(self, site_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for URL consolidation."""
        consolidations = []
        
        # Simulate finding duplicate or similar content URLs
        urls = site_structure.get('urls', [])
        
        # Group similar URLs
        url_groups = defaultdict(list)
        for url in urls:
            parsed = urlparse(url)
            path_segments = parsed.path.strip('/').split('/')
            
            if len(path_segments) >= 2:
                base_pattern = '/'.join(path_segments[:2])
                url_groups[base_pattern].append(url)
        
        # Find groups with multiple URLs that could be consolidated
        for pattern, group_urls in url_groups.items():
            if len(group_urls) > 3:
                consolidations.append({
                    'pattern': pattern,
                    'urls': group_urls,
                    'recommendation': f'Consider consolidating {len(group_urls)} URLs under pattern /{pattern}',
                    'priority': 'medium'
                })
        
        return consolidations
    
    async def _generate_redirect_recommendations(self,
                                               current_structure: Dict[str, Any],
                                               optimized_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate redirect recommendations for structure optimization."""
        recommendations = []
        
        # Check if restructuring is needed
        if optimized_structure.get('restructuring_needed'):
            recommendations.append({
                'type': 'bulk_redirect',
                'reason': 'Flatten deep URL hierarchy',
                'pattern': '/category/subcategory/subsubcategory/* -> /category/*',
                'estimated_redirects': 100,
                'priority': 'high'
            })
        
        # Check for new categories
        if optimized_structure.get('add_categories'):
            recommendations.append({
                'type': 'new_structure',
                'reason': 'Add missing category pages',
                'action': 'Create new category URLs and redirect related content',
                'estimated_impact': 'medium',
                'priority': 'medium'
            })
        
        return recommendations
    
    async def _apply_site_seo_enhancements(self, optimized_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply SEO enhancements to optimized site structure."""
        return {
            'url_templates': {
                'category': '/category/{slug}',
                'creator': '/creator/{slug}',
                'content': '/creator/{creator_slug}/{content_type}/{slug}'
            },
            'canonical_strategy': 'parameter_removal',
            'breadcrumb_implementation': 'schema_org_compliant',
            'internal_linking': {
                'strategy': 'hierarchical',
                'anchor_text_optimization': True,
                'deep_link_distribution': True
            },
            'pagination_handling': {
                'rel_next_prev': True,
                'canonical_to_page_one': True,
                'noindex_deep_pages': False
            }
        }
    
    async def _validate_redirect_rule(self, redirect: URLRedirect) -> Dict[str, Any]:
        """Validate redirect rule for potential issues."""
        validation = {'valid': True, 'reason': ''}
        
        # Check for self-redirect
        if redirect.source_url == redirect.target_url:
            validation = {'valid': False, 'reason': 'Source and target URLs are identical'}
            return validation
        
        # Check for circular redirects
        if any(r.source_url == redirect.target_url and r.target_url == redirect.source_url 
               for r in self.redirect_rules if r.is_active):
            validation = {'valid': False, 'reason': 'Circular redirect detected'}
            return validation
        
        # Check URL format
        try:
            parsed_source = urlparse(redirect.source_url)
            parsed_target = urlparse(redirect.target_url)
            
            if not all([parsed_source.scheme, parsed_source.netloc, parsed_target.scheme, parsed_target.netloc]):
                validation = {'valid': False, 'reason': 'Invalid URL format'}
        except Exception:
            validation = {'valid': False, 'reason': 'URL parsing error'}
        
        return validation
    
    async def _resolve_redirect_chains(self, redirects: List[URLRedirect]) -> Dict[str, Any]:
        """Resolve redirect chains to improve performance."""
        resolved_chains = 0
        chain_mappings = {}
        
        # Build redirect mapping
        redirect_map = {r.source_url: r.target_url for r in redirects if r.is_active}
        
        # Find and resolve chains
        for source_url in redirect_map:
            chain = [source_url]
            current_url = source_url
            
            # Follow the chain
            while current_url in redirect_map and len(chain) < 10:  # Prevent infinite loops
                next_url = redirect_map[current_url]
                if next_url in chain:  # Circular reference
                    break
                chain.append(next_url)
                current_url = next_url
            
            # If chain length > 2, we have a chain to resolve
            if len(chain) > 2:
                chain_mappings[source_url] = chain[-1]  # Direct redirect to final destination
                resolved_chains += 1
        
        return {
            'resolved_chains': resolved_chains,
            'chain_mappings': chain_mappings,
            'recommendations': [
                f'Create direct redirects for {resolved_chains} redirect chains',
                'Monitor redirect performance after implementation'
            ]
        }
    
    async def _calculate_redirect_seo_improvements(self, redirects: List[URLRedirect]) -> Dict[str, Any]:
        """Calculate SEO improvements from redirect implementation."""
        return {
            'link_equity_preservation': f'{len(redirects)} redirects preserving link equity',
            'crawl_efficiency': 'Improved by reducing redirect chains',
            'user_experience': 'Enhanced by faster page loads',
            'search_ranking_impact': 'Positive - maintains ranking signals',
            'estimated_impact_timeline': '2-4 weeks for full effect'
        }
    
    def _generate_redirect_implementation_config(self, redirects: List[URLRedirect]) -> Dict[str, Any]:
        """Generate implementation configuration for redirects."""
        config = {
            'redirect_count': len(redirects),
            'implementation_methods': {},
            'testing_requirements': [],
            'monitoring_setup': {}
        }
        
        # Generate different implementation formats
        config['implementation_methods'] = {
            'htaccess': self._generate_htaccess_rules(redirects),
            'nginx': self._generate_nginx_rules(redirects),
            'cloudflare': self._generate_cloudflare_rules(redirects)
        }
        
        config['testing_requirements'] = [
            'Test each redirect returns correct status code',
            'Verify target URLs are accessible',
            'Check for redirect loops',
            'Validate preservation of query parameters where needed'
        ]
        
        return config
    
    def _generate_htaccess_rules(self, redirects: List[URLRedirect]) -> List[str]:
        """Generate .htaccess redirect rules."""
        rules = []
        for redirect in redirects:
            source_path = urlparse(redirect.source_url).path
            status_code = redirect.redirect_type.value
            rules.append(f'Redirect {status_code} {source_path} {redirect.target_url}')
        return rules
    
    def _generate_nginx_rules(self, redirects: List[URLRedirect]) -> List[str]:
        """Generate Nginx redirect rules."""
        rules = []
        for redirect in redirects:
            source_path = urlparse(redirect.source_url).path
            redirect_type = 'permanent' if redirect.is_permanent else 'redirect'
            rules.append(f'rewrite ^{source_path}$ {redirect.target_url} {redirect_type};')
        return rules
    
    def _generate_cloudflare_rules(self, redirects: List[URLRedirect]) -> List[Dict[str, Any]]:
        """Generate Cloudflare redirect rules."""
        rules = []
        for redirect in redirects:
            rules.append({
                'source': redirect.source_url,
                'target': redirect.target_url,
                'status_code': int(redirect.redirect_type.value),
                'preserve_query_string': True
            })
        return rules
    
    def _setup_redirect_monitoring(self, redirects: List[URLRedirect]) -> Dict[str, Any]:
        """Setup monitoring for redirect performance."""
        return {
            'metrics_to_track': [
                'Redirect response time',
                'Error rate (4xx, 5xx)',
                'Traffic through redirects',
                'Search engine crawl success'
            ],
            'alerts': [
                'High error rate on redirects',
                'Slow redirect response times',
                'Redirect loops detected'
            ],
            'reporting_frequency': 'weekly',
            'dashboards': [
                'Redirect performance overview',
                'SEO impact tracking',
                'User experience metrics'
            ]
        }
    
    def _generate_breadcrumb_name(self, segment: str, position: int, page_data: Dict[str, Any]) -> str:
        """Generate human-readable breadcrumb name from URL segment."""
        # Convert slug back to readable name
        name = segment.replace('-', ' ').replace('_', ' ').title()
        
        # Use page data if available
        if position == 0 and 'category' in page_data:
            return page_data['category']
        elif 'creator' in segment and 'creator_name' in page_data:
            return page_data['creator_name']
        elif position == len(page_data.get('url_segments', [])) - 1 and 'title' in page_data:
            return page_data['title']
        
        return name
    
    def _generate_breadcrumb_schema_markup(self, levels: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate schema.org markup for breadcrumbs."""
        return {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {
                    '@type': 'ListItem',
                    'position': level['position'],
                    'name': level['name'],
                    'item': level['url']
                }
                for level in levels
            ]
        }

# Enterprise URL structure management
class URLArchitectureManager:
    """High-level URL architecture management for IA Chéries platform."""
    
    def __init__(self, base_domain: str):
        self.optimizer = URLStructureOptimizer(base_domain)
        self.base_domain = base_domain
        
    async def optimize_platform_url_architecture(self,
                                                platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entire platform URL architecture."""
        optimization_results = {
            'site_structure_optimization': {},
            'creator_url_optimizations': {},
            'redirect_management': {},
            'seo_enhancements': {},
            'implementation_roadmap': {}
        }
        
        # Optimize site-wide structure
        site_structure = platform_data.get('site_structure', {})
        if site_structure:
            site_optimization = await self.optimizer.optimize_site_navigation_structure(site_structure)
            optimization_results['site_structure_optimization'] = site_optimization
        
        # Optimize creator URLs
        creators_data = platform_data.get('creators', [])
        creator_optimizations = []
        
        for creator_data in creators_data[:10]:  # Limit for performance
            creator_id = creator_data.get('id')
            content_types = creator_data.get('content_types', ['video', 'audio', 'image'])
            
            creator_structure = await self.optimizer.generate_creator_url_structure(
                creator_id, creator_data, content_types
            )
            creator_optimizations.append(creator_structure)
        
        optimization_results['creator_url_optimizations'] = creator_optimizations
        
        return optimization_results