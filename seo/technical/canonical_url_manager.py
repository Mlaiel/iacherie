"""
import logging

Canonical URL Manager for Ainflue Platform
Advanced canonical URL management and duplicate content prevention

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Union, Tuple
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse
import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CanonicalRule:
    """Canonical URL rule configuration"""
    pattern: str
    canonical_template: str
    priority: int = 1
    parameters_to_ignore: List[str] = None
    platform_specific: bool = False
    creator_type: Optional[str] = None


class CanonicalURLManager:
    """
    Advanced canonical URL management for SEO optimization
    Handles duplicate content prevention and URL canonicalization
    """
    
    def __init__(self, base_domain -> None: str) -> None:
        self.base_domain = base_domain.rstrip('/')
        self.rules: List[CanonicalRule] = []
        self.ignore_parameters = set()
        self.platform_rules = {}
        self.creator_type_rules = {}
        
    def add_global_ignore_parameters(self, parameters -> None: List[str]) -> None:
        """Add parameters to globally ignore in canonical URLs"""
        self.ignore_parameters.update(parameters)
        
    def add_canonical_rule(self, pattern -> None: str, canonical_template -> None: str, 
                          priority -> None: int = 1, parameters_to_ignore -> None: List[str] = None,
                          platform_specific -> None: bool = False, creator_type -> None: str = None) -> None:
        """Add a canonical URL rule"""
        
        rule = CanonicalRule(
            pattern=pattern,
            canonical_template=canonical_template,
            priority=priority,
            parameters_to_ignore=parameters_to_ignore or [],
            platform_specific=platform_specific,
            creator_type=creator_type
        )
        
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority, reverse=True)
        
    def setup_default_rules(self) -> None:
        """Setup default canonical rules for Ainflue platform"""
        
        # Content URLs - highest priority
        self.add_canonical_rule(
            r'/content/(\w+)/(\d+)/?',
            '/content/{}/{}',
            priority=10,
            parameters_to_ignore=['utm_source', 'utm_medium', 'utm_campaign', 'ref', 'share']
        )
        
        # Creator profile URLs
        self.add_canonical_rule(
            r'/creator/([^/]+)/?',
            '/creator/{}',
            priority=9,
            parameters_to_ignore=['tab', 'view', 'sort']
        )
        
        # Search result pages
        self.add_canonical_rule(
            r'/search/?',
            '/search',
            priority=8,
            parameters_to_ignore=['page', 'per_page', 'sort_by', 'view']
        )
        
        # Category pages
        self.add_canonical_rule(
            r'/category/([^/]+)/?',
            '/category/{}',
            priority=7,
            parameters_to_ignore=['page', 'sort', 'filter']
        )
        
        # Portfolio pages
        self.add_canonical_rule(
            r'/portfolio/([^/]+)/?',
            '/portfolio/{}',
            priority=7,
            parameters_to_ignore=['gallery_view', 'sort']
        )
        
        # Blog/Article URLs
        self.add_canonical_rule(
            r'/blog/(\d{4})/(\d{2})/([^/]+)/?',
            '/blog/{}/{}/{}',
            priority=6,
            parameters_to_ignore=['comment_page', 'share']
        )
        
    def setup_creator_specific_rules(self, creator_type -> None: str) -> None:
        """Setup canonical rules specific to creator type"""
        
        if creator_type == "musician":
            # Music track URLs
            self.add_canonical_rule(
                r'/music/([^/]+)/([^/]+)/?',
                '/music/{}/{}',
                priority=10,
                creator_type="musician",
                parameters_to_ignore=['autoplay', 'start_time', 'quality']
            )
            
            # Album URLs
            self.add_canonical_rule(
                r'/album/([^/]+)/?',
                '/album/{}',
                priority=9,
                creator_type="musician",
                parameters_to_ignore=['track', 'autoplay']
            )
            
        elif creator_type == "photographer":
            # Photo gallery URLs
            self.add_canonical_rule(
                r'/gallery/([^/]+)/(\d+)/?',
                '/gallery/{}/{}',
                priority=10,
                creator_type="photographer",
                parameters_to_ignore=['size', 'format', 'download']
            )
            
            # Photo collection URLs
            self.add_canonical_rule(
                r'/collection/([^/]+)/?',
                '/collection/{}',
                priority=9,
                creator_type="photographer",
                parameters_to_ignore=['view', 'sort_by']
            )
            
        elif creator_type == "blogger":
            # Blog post URLs with date
            self.add_canonical_rule(
                r'/blog/(\d{4}/\d{2}/\d{2})/([^/]+)/?',
                '/blog/{}/{}',
                priority=10,
                creator_type="blogger",
                parameters_to_ignore=['comment_page', 'preview']
            )
            
    def setup_platform_specific_rules(self, platforms -> None: List[str]) -> None:
        """Setup platform-specific canonical rules"""
        
        for platform in platforms:
            if platform.lower() == "youtube":
                self.add_canonical_rule(
                    r'/video/([^/]+)/?',
                    '/video/{}',
                    priority=10,
                    platform_specific=True,
                    parameters_to_ignore=['t', 'start', 'end', 'autoplay', 'mute']
                )
                
            elif platform.lower() == "spotify":
                self.add_canonical_rule(
                    r'/track/([^/]+)/?',
                    '/track/{}',
                    priority=10,
                    platform_specific=True,
                    parameters_to_ignore=['play', 'highlight', 'context']
                )
                
            elif platform.lower() == "instagram":
                self.add_canonical_rule(
                    r'/post/([^/]+)/?',
                    '/post/{}',
                    priority=10,
                    platform_specific=True,
                    parameters_to_ignore=['modal', 'taken-by', 'share']
                )
                
    def clean_url(self, url: str, custom_ignore_params: Set[str] = None) -> str:
        """Clean URL by removing specified parameters"""
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Combine ignore parameters
        ignore_params = self.ignore_parameters.copy()
        if custom_ignore_params:
            ignore_params.update(custom_ignore_params)
            
        # Remove ignored parameters
        cleaned_params = {
            k: v for k, v in query_params.items() 
            if k not in ignore_params
        }
        
        # Rebuild query string
        if cleaned_params:
            query_string = urlencode(cleaned_params, doseq=True)
        else:
            query_string = ''
            
        # Rebuild URL
        cleaned_parsed = parsed._replace(query=query_string)
        return urlunparse(cleaned_parsed)
        
    def generate_canonical_url(self, url: str, creator_type: str = None, 
                              platform: str = None) -> str:
        """Generate canonical URL for given URL"""
        
        parsed = urlparse(url)
        path = parsed.path.rstrip('/')
        
        # Find matching rule
        matching_rule = None
        for rule in self.rules:
            # Check creator type constraint
            if rule.creator_type and rule.creator_type != creator_type:
                continue
                
            # Check platform constraint
            if rule.platform_specific and not platform:
                continue
                
            # Check pattern match
            if re.match(rule.pattern, path):
                matching_rule = rule
                break
                
        if not matching_rule:
            # No specific rule found, use default cleaning
            return self.clean_url(url)
            
        # Extract groups from pattern match
        match = re.match(matching_rule.pattern, path)
        groups = match.groups() if match else []
        
        # Build canonical path
        try:
            canonical_path = matching_rule.canonical_template.format(*groups)
        except (IndexError, ValueError):
            # Fallback if template doesn't match groups
            canonical_path = path
            
        # Clean parameters
        ignore_params = set(matching_rule.parameters_to_ignore) if matching_rule.parameters_to_ignore else set()
        cleaned_url = self.clean_url(url, ignore_params)
        
        # Combine with canonical path
        parsed_clean = urlparse(cleaned_url)
        canonical_parsed = parsed_clean._replace(path=canonical_path)
        
        canonical_url = urlunparse(canonical_parsed)
        
        # Ensure absolute URL
        if not canonical_url.startswith('http'):
            canonical_url = urljoin(self.base_domain, canonical_url.lstrip('/'))
            
        return canonical_url
        
    def detect_duplicate_content(self, urls: List[str]) -> Dict[str, List[str]]:
        """Detect potential duplicate content URLs"""
        
        canonical_groups = {}
        
        for url in urls:
            canonical = self.generate_canonical_url(url)
            
            if canonical not in canonical_groups:
                canonical_groups[canonical] = []
                
            canonical_groups[canonical].append(url)
            
        # Return only groups with multiple URLs (potential duplicates)
        duplicates = {
            canonical: urls_list 
            for canonical, urls_list in canonical_groups.items() 
            if len(urls_list) > 1
        }
        
        return duplicates
        
    def generate_canonical_meta_tag(self, url: str, creator_type: str = None, 
                                   platform: str = None) -> str:
        """Generate HTML canonical meta tag"""
        
        canonical_url = self.generate_canonical_url(url, creator_type, platform)
        return f'<link rel="canonical" href="{canonical_url}" />'
        
    def validate_canonical_implementation(self, page_data: Dict) -> Dict[str, Union[bool, List[str]]]:
        """Validate canonical URL implementation"""
        
        issues = []
        warnings = []
        
        current_url = page_data.get('current_url', '')
        canonical_url = page_data.get('canonical_url', '')
        
        if not canonical_url:
            issues.append("No canonical URL specified")
        else:
            # Check if canonical URL is absolute
            if not canonical_url.startswith('http'):
                warnings.append("Canonical URL should be absolute")
                
            # Check if canonical points to self or different URL
            expected_canonical = self.generate_canonical_url(current_url)
            if canonical_url != expected_canonical:
                warnings.append(f"Canonical URL mismatch. Expected: {expected_canonical}, Found: {canonical_url}")
                
            # Check for HTTPS
            if canonical_url.startswith('http://'):
                warnings.append("Canonical URL should use HTTPS")
                
            # Check for trailing slash consistency
            if current_url.rstrip('/') != canonical_url.rstrip('/'):
                trailing_slash_diff = current_url.endswith('/') != canonical_url.endswith('/')
                if trailing_slash_diff:
                    warnings.append("Trailing slash inconsistency between current and canonical URL")
                    
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
        
    def generate_sitemap_canonical_urls(self, url_list: List[str], 
                                       creator_type: str = None) -> List[str]:
        """Generate canonical URLs for sitemap"""
        
        canonical_urls = set()
        
        for url in url_list:
            canonical = self.generate_canonical_url(url, creator_type)
            canonical_urls.add(canonical)
            
        return sorted(list(canonical_urls))
        
    def audit_canonical_implementation(self, website_urls: List[str]) -> Dict:
        """Comprehensive canonical URL audit"""
        
        audit_results = {
            'total_urls': len(website_urls),
            'duplicate_groups': 0,
            'potential_duplicates': 0,
            'canonical_issues': [],
            'recommendations': []
        }
        
        # Detect duplicates
        duplicates = self.detect_duplicate_content(website_urls)
        audit_results['duplicate_groups'] = len(duplicates)
        audit_results['potential_duplicates'] = sum(len(urls) for urls in duplicates.values())
        
        # Analyze URL patterns
        url_patterns = {}
        for url in website_urls:
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            pattern = '/'.join(['*' if part.isdigit() else part for part in path_parts])
            
            if pattern not in url_patterns:
                url_patterns[pattern] = 0
            url_patterns[pattern] += 1
            
        # Generate recommendations
        recommendations = []
        
        if audit_results['potential_duplicates'] > audit_results['total_urls'] * 0.1:
            recommendations.append("High number of potential duplicate URLs detected. Implement canonical tags.")
            
        if len([p for p, c in url_patterns.items() if c > 10]) > 5:
            recommendations.append("Multiple URL patterns with high frequency. Consider URL structure optimization.")
            
        parameter_heavy_urls = [url for url in website_urls if len(parse_qs(urlparse(url).query)) > 3]
        if len(parameter_heavy_urls) > audit_results['total_urls'] * 0.2:
            recommendations.append("Many URLs with multiple parameters. Implement parameter filtering.")
            
        audit_results['recommendations'] = recommendations
        
        return audit_results


class CanonicalURLMiddleware:
    """Middleware for automatic canonical URL handling"""
    
    def __init__(self, manager -> None: CanonicalURLManager) -> None:
        self.manager = manager
        
    def process_request(self, request_data: Dict) -> Dict:
        """Process incoming request and add canonical URL"""
        
        current_url = request_data.get('url', '')
        creator_type = request_data.get('creator_type')
        platform = request_data.get('platform')
        
        canonical_url = self.manager.generate_canonical_url(
            current_url, creator_type, platform
        )
        
        request_data['canonical_url'] = canonical_url
        request_data['canonical_meta_tag'] = self.manager.generate_canonical_meta_tag(
            current_url, creator_type, platform
        )
        
        return request_data


# Utility functions for integration
def create_ainflue_canonical_manager(base_domain: str = "https://ainflue.com",
                                   creator_type: str = None,
                                   platforms: List[str] = None) -> CanonicalURLManager:
    """Create configured canonical URL manager for Ainflue"""
    
    manager = CanonicalURLManager(base_domain)
    
    # Setup default rules
    manager.setup_default_rules()
    
    # Add global ignore parameters
    manager.add_global_ignore_parameters([
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'share', 'fbclid', 'gclid', 'msclkid',
        'session_id', 'user_id', 'timestamp', 'cache_bust'
    ])
    
    # Setup creator-specific rules
    if creator_type:
        manager.setup_creator_specific_rules(creator_type)
        
    # Setup platform-specific rules
    if platforms:
        manager.setup_platform_specific_rules(platforms)
        
    return manager


if __name__ == "__main__":
    # Example usage
    manager = create_ainflue_canonical_manager(
        creator_type="musician",
        platforms=["spotify", "youtube"]
    )
    
    # Test URLs
    test_urls = [
        "https://ainflue.com/music/artist/song?utm_source=google&autoplay=1",
        "https://ainflue.com/music/artist/song/",
        "https://ainflue.com/creator/johndoe?tab=music&sort=date",
        "https://ainflue.com/creator/johndoe/"
    ]
    
    for url in test_urls:
        canonical = manager.generate_canonical_url(url, creator_type="musician")
        print(f"Original: {url}")
        print(f"Canonical: {canonical}")
        print(f"Meta tag: {manager.generate_canonical_meta_tag(url, creator_type='musician')}")
        print("-" * 80)
        
    # Detect duplicates
    duplicates = manager.detect_duplicate_content(test_urls)
    print(f"Potential duplicates: {duplicates}")