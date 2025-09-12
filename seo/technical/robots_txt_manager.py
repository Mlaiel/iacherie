"""
Robots.txt Manager for Ainflue Platform
Advanced robots.txt generation and management for SEO optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import Dict, List, Optional, Union
from datetime import datetime
from urllib.parse import urljoin
import re


class RobotsTxtManager:
    """
    Advanced robots.txt manager for SEO optimization
    Handles dynamic robots.txt generation, sitemap inclusion, and crawler management
    """
    
    def __init__(self, base_url: str, sitemap_url: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.sitemap_url = sitemap_url or f"{self.base_url}/sitemap.xml"
        self.rules = []
        self.user_agents = {}
        self.crawl_delay = {}
        self.sitemaps = []
        
    def add_user_agent_rules(self, user_agent: str, allow: List[str] = None, 
                           disallow: List[str] = None, crawl_delay: Optional[int] = None):
        """Add rules for specific user agent"""
        if user_agent not in self.user_agents:
            self.user_agents[user_agent] = {'allow': [], 'disallow': []}
            
        if allow:
            self.user_agents[user_agent]['allow'].extend(allow)
        if disallow:
            self.user_agents[user_agent]['disallow'].extend(disallow)
        if crawl_delay:
            self.crawl_delay[user_agent] = crawl_delay
            
    def add_sitemap(self, sitemap_url: str):
        """Add sitemap URL to robots.txt"""
        if sitemap_url not in self.sitemaps:
            self.sitemaps.append(sitemap_url)
            
    def generate_creator_friendly_robots(self, creator_type: str = "general"):
        """Generate creator-optimized robots.txt rules"""
        
        # General rules for all creators
        self.add_user_agent_rules(
            "*",
            allow=[
                "/api/public/",
                "/content/public/",
                "/creator/profile/",
                "/portfolio/",
                "/*.jpg$",
                "/*.png$", 
                "/*.gif$",
                "/*.webp$",
                "/*.mp4$",
                "/*.mp3$"
            ],
            disallow=[
                "/api/private/",
                "/admin/",
                "/user/private/",
                "/analytics/",
                "/payment/",
                "/temp/",
                "/*?session=",
                "/*?token=",
                "/draft/"
            ],
            crawl_delay=1
        )
        
        # Creator-specific optimizations
        if creator_type == "musician":
            self.add_user_agent_rules(
                "*",
                allow=[
                    "/music/",
                    "/audio/",
                    "/albums/",
                    "/tracks/",
                    "/*.mp3$",
                    "/*.wav$",
                    "/*.flac$"
                ]
            )
            
        elif creator_type == "photographer":
            self.add_user_agent_rules(
                "*", 
                allow=[
                    "/gallery/",
                    "/photos/",
                    "/portfolio/",
                    "/*.jpg$",
                    "/*.jpeg$",
                    "/*.png$",
                    "/*.webp$"
                ]
            )
            
        elif creator_type == "blogger":
            self.add_user_agent_rules(
                "*",
                allow=[
                    "/blog/",
                    "/articles/",
                    "/posts/",
                    "/rss.xml",
                    "/feed.xml"
                ]
            )
            
        # Social media bot optimizations
        self.add_user_agent_rules(
            "facebookexternalhit",
            allow=[
                "/",
                "/content/public/",
                "/creator/profile/"
            ],
            crawl_delay=0
        )
        
        self.add_user_agent_rules(
            "Twitterbot",
            allow=[
                "/",
                "/content/public/",
                "/creator/profile/"
            ],
            crawl_delay=0
        )
        
    def generate_platform_specific_rules(self, platforms: List[str]):
        """Generate platform-specific SEO rules"""
        
        for platform in platforms:
            if platform.lower() == "youtube":
                self.add_user_agent_rules(
                    "*",
                    allow=[
                        "/videos/",
                        "/thumbnails/",
                        "/*.mp4$",
                        "/*.webm$",
                        "/video-sitemaps/"
                    ]
                )
                
            elif platform.lower() == "spotify":
                self.add_user_agent_rules(
                    "*", 
                    allow=[
                        "/music/",
                        "/audio/",
                        "/artist-profile/",
                        "/*.mp3$",
                        "/audio-sitemaps/"
                    ]
                )
                
            elif platform.lower() == "instagram":
                self.add_user_agent_rules(
                    "*",
                    allow=[
                        "/images/",
                        "/posts/",
                        "/*.jpg$",
                        "/*.png$",
                        "/image-sitemaps/"
                    ]
                )
                
    def add_security_rules(self):
        """Add security-focused robots.txt rules"""
        
        # Block malicious bots
        malicious_bots = [
            "AhrefsBot", "MJ12bot", "DotBot", "BLEXBot",
            "SemrushBot", "MegaIndex", "MajesticSEO"
        ]
        
        for bot in malicious_bots:
            self.add_user_agent_rules(
                bot,
                disallow=["/"]
            )
            
        # Protect sensitive areas
        self.add_user_agent_rules(
            "*",
            disallow=[
                "/config/",
                "/logs/", 
                "/backups/",
                "/database/",
                "/env/",
                "/.git/",
                "/node_modules/",
                "/vendor/",
                "/*?debug=",
                "/*?test="
            ]
        )
        
    def generate_robots_txt(self) -> str:
        """Generate complete robots.txt content"""
        
        content = []
        content.append(f"# Robots.txt for {self.base_url}")
        content.append(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"# Ainflue Platform - Creator-Optimized SEO")
        content.append("")
        
        # User-agent specific rules
        for user_agent, rules in self.user_agents.items():
            content.append(f"User-agent: {user_agent}")
            
            # Add allow rules
            for allow_rule in rules.get('allow', []):
                content.append(f"Allow: {allow_rule}")
                
            # Add disallow rules  
            for disallow_rule in rules.get('disallow', []):
                content.append(f"Disallow: {disallow_rule}")
                
            # Add crawl delay
            if user_agent in self.crawl_delay:
                content.append(f"Crawl-delay: {self.crawl_delay[user_agent]}")
                
            content.append("")
            
        # Add sitemaps
        if self.sitemaps:
            content.append("# Sitemaps")
            for sitemap in self.sitemaps:
                content.append(f"Sitemap: {sitemap}")
            content.append("")
            
        # Add host directive
        content.append(f"Host: {self.base_url}")
        
        return "\n".join(content)
        
    def save_robots_txt(self, file_path: str):
        """Save robots.txt to file"""
        content = self.generate_robots_txt()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def validate_robots_txt(self, content: str) -> Dict[str, Union[bool, List[str]]]:
        """Validate robots.txt content"""
        
        issues = []
        warnings = []
        
        lines = content.split('\n')
        
        # Check for basic structure
        has_user_agent = any('User-agent:' in line for line in lines)
        has_sitemap = any('Sitemap:' in line for line in lines)
        
        if not has_user_agent:
            issues.append("No User-agent directive found")
            
        if not has_sitemap:
            warnings.append("No Sitemap directive found")
            
        # Check for common issues
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for wildcard in wrong position
            if line.startswith('Disallow:') and '*' in line and not line.endswith('*'):
                warnings.append(f"Line {i}: Wildcard (*) should typically be at the end")
                
            # Check for trailing spaces
            if line != line.rstrip():
                warnings.append(f"Line {i}: Trailing whitespace detected")
                
            # Check for invalid directives
            if line and not line.startswith('#') and ':' in line:
                directive = line.split(':')[0].strip()
                valid_directives = ['User-agent', 'Disallow', 'Allow', 'Crawl-delay', 'Sitemap', 'Host']
                if directive not in valid_directives:
                    issues.append(f"Line {i}: Invalid directive '{directive}'")
                    
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
        
    def generate_dynamic_rules(self, creator_data: Dict):
        """Generate dynamic rules based on creator data"""
        
        # Allow public content
        if creator_data.get('public_content', []):
            for content_path in creator_data['public_content']:
                self.add_user_agent_rules("*", allow=[f"/{content_path}/"])
                
        # Disallow private/premium content from general crawling
        if creator_data.get('premium_content', []):
            for content_path in creator_data['premium_content']:
                self.add_user_agent_rules("*", disallow=[f"/{content_path}/"])
                
        # Add language-specific sitemaps
        if creator_data.get('languages', []):
            for lang in creator_data['languages']:
                self.add_sitemap(f"{self.base_url}/sitemap-{lang}.xml")
                
        # Platform-specific optimization
        if creator_data.get('platforms', []):
            self.generate_platform_specific_rules(creator_data['platforms'])


class RobotsTxtAnalyzer:
    """Analyze and optimize existing robots.txt files"""
    
    def __init__(self):
        self.seo_recommendations = []
        
    def analyze_robots_txt(self, content: str) -> Dict:
        """Comprehensive robots.txt analysis"""
        
        analysis = {
            'seo_score': 0,
            'recommendations': [],
            'security_issues': [],
            'performance_issues': [],
            'mobile_optimization': False,
            'social_media_optimization': False
        }
        
        lines = content.split('\n')
        
        # Check for mobile optimization
        mobile_bots = ['Googlebot-Mobile', 'Mobile']
        analysis['mobile_optimization'] = any(
            any(bot in line for bot in mobile_bots) for line in lines
        )
        
        # Check for social media optimization  
        social_bots = ['facebookexternalhit', 'Twitterbot', 'LinkedInBot']
        analysis['social_media_optimization'] = any(
            any(bot in line for bot in social_bots) for line in lines
        )
        
        # Calculate SEO score
        score = 0
        
        if 'Sitemap:' in content:
            score += 20
        if analysis['mobile_optimization']:
            score += 15
        if analysis['social_media_optimization']:
            score += 15
        if 'Crawl-delay:' in content:
            score += 10
        if '/admin' in content and 'Disallow:' in content:
            score += 20
        if len([l for l in lines if l.strip().startswith('Allow:')]) > 0:
            score += 20
            
        analysis['seo_score'] = min(score, 100)
        
        # Generate recommendations
        if analysis['seo_score'] < 80:
            analysis['recommendations'].extend([
                "Add sitemap directives for better indexing",
                "Include mobile bot optimization", 
                "Add social media crawler rules",
                "Implement crawl delay for better server performance"
            ])
            
        return analysis


# Example usage and configuration
def create_ainflue_robots_txt(creator_type: str = "general", 
                             platforms: List[str] = None,
                             base_url: str = "https://ainflue.com") -> str:
    """Create optimized robots.txt for Ainflue creators"""
    
    manager = RobotsTxtManager(base_url)
    
    # Generate creator-friendly rules
    manager.generate_creator_friendly_robots(creator_type)
    
    # Add platform-specific rules
    if platforms:
        manager.generate_platform_specific_rules(platforms)
        
    # Add security rules
    manager.add_security_rules()
    
    # Add default sitemaps
    manager.add_sitemap(f"{base_url}/sitemap.xml")
    manager.add_sitemap(f"{base_url}/image-sitemap.xml")
    manager.add_sitemap(f"{base_url}/video-sitemap.xml")
    
    return manager.generate_robots_txt()


if __name__ == "__main__":
    # Example: Generate robots.txt for a musician
    robots_content = create_ainflue_robots_txt(
        creator_type="musician",
        platforms=["spotify", "youtube"],
        base_url="https://ainflue.com"
    )
    
    print(robots_content)
    
    # Analyze the generated content
    analyzer = RobotsTxtAnalyzer()
    analysis = analyzer.analyze_robots_txt(robots_content)
    print(f"\nSEO Score: {analysis['seo_score']}/100")
    print(f"Recommendations: {analysis['recommendations']}")