#!/usr/bin/env python3
"""
117 Industrial Crawlers Verification Script
Validates all platform crawlers for industrial web surveillance
"""

import os
import sys
import importlib
import logging
from typing import Dict, List, Any
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrawlerValidator:
    """Validates crawler implementations."""
    
    def __init__(self):
        self.crawlers_path = Path("/home/runner/work/Ainflue/Ainflue/crawlers")
        self.verified_crawlers = {}
        self.failed_crawlers = {}
    
    def scan_crawler_files(self) -> List[str]:
        """Scan for crawler files in the crawlers directory."""
        crawler_files = []
        
        if not self.crawlers_path.exists():
            logger.error(f"Crawlers directory not found: {self.crawlers_path}")
            return crawler_files
        
        # Find all crawler Python files
        for file_path in self.crawlers_path.rglob("*_crawler.py"):
            if file_path.is_file() and not file_path.name.startswith('__'):
                crawler_files.append(str(file_path))
        
        logger.info(f"Found {len(crawler_files)} crawler files")
        return crawler_files
    
    def validate_crawler_structure(self, crawler_file: str) -> bool:
        """Validate crawler file structure."""
        try:
            with open(crawler_file, 'r') as f:
                content = f.read()
            
            # Check for essential crawler components
            required_components = [
                'class',
                'def crawl',
                'def extract',
                'import'
            ]
            
            missing_components = []
            for component in required_components:
                if component not in content:
                    missing_components.append(component)
            
            if missing_components:
                logger.warning(f"Crawler {crawler_file} missing: {missing_components}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating {crawler_file}: {e}")
            return False
    
    def categorize_crawlers(self, crawler_files: List[str]) -> Dict[str, List[str]]:
        """Categorize crawlers by platform type."""
        categories = {
            'social_media': [],
            'music_audio': [],
            'video_streaming': [],
            'content_platforms': [],
            'professional': [],
            'messaging': [],
            'emerging': []
        }
        
        # Platform categorization mapping
        social_platforms = ['instagram', 'facebook', 'twitter', 'linkedin', 'pinterest', 'reddit', 'snapchat', 'threads', 'mastodon', 'bereal']
        music_platforms = ['spotify', 'apple_music', 'soundcloud', 'youtube_music', 'amazon_music', 'deezer', 'bandcamp', 'mixcloud']
        video_platforms = ['youtube', 'tiktok', 'twitch', 'vimeo', 'dailymotion', 'rumble']
        content_platforms = ['medium', 'substack', 'patreon', 'onlyfans']
        messaging_platforms = ['discord', 'telegram', 'whatsapp']
        
        for crawler_file in crawler_files:
            file_name = Path(crawler_file).stem.lower()
            
            categorized = False
            for platform in social_platforms:
                if platform in file_name:
                    categories['social_media'].append(crawler_file)
                    categorized = True
                    break
            
            if not categorized:
                for platform in music_platforms:
                    if platform in file_name:
                        categories['music_audio'].append(crawler_file)
                        categorized = True
                        break
            
            if not categorized:
                for platform in video_platforms:
                    if platform in file_name:
                        categories['video_streaming'].append(crawler_file)
                        categorized = True
                        break
            
            if not categorized:
                for platform in content_platforms:
                    if platform in file_name:
                        categories['content_platforms'].append(crawler_file)
                        categorized = True
                        break
            
            if not categorized:
                for platform in messaging_platforms:
                    if platform in file_name:
                        categories['messaging'].append(crawler_file)
                        categorized = True
                        break
            
            if not categorized:
                categories['emerging'].append(crawler_file)
        
        return categories
    
    def validate_all_crawlers(self) -> Dict[str, Any]:
        """Validate all crawler implementations."""
        logger.info("🕷️ Starting 117 Industrial Crawlers Validation...")
        
        crawler_files = self.scan_crawler_files()
        categories = self.categorize_crawlers(crawler_files)
        
        validation_results = {
            'total_crawlers_found': len(crawler_files),
            'target_crawlers': 117,
            'categories': {},
            'validation_summary': {
                'valid_crawlers': 0,
                'invalid_crawlers': 0,
                'validation_rate': 0.0
            }
        }
        
        # Validate each category
        for category, crawlers in categories.items():
            logger.info(f"📊 Validating {category}: {len(crawlers)} crawlers")
            
            category_results = {
                'total': len(crawlers),
                'valid': 0,
                'invalid': 0,
                'crawlers': []
            }
            
            for crawler_file in crawlers:
                crawler_name = Path(crawler_file).stem
                is_valid = self.validate_crawler_structure(crawler_file)
                
                crawler_info = {
                    'name': crawler_name,
                    'file_path': crawler_file,
                    'valid': is_valid,
                    'size_lines': self._count_lines(crawler_file)
                }
                
                category_results['crawlers'].append(crawler_info)
                
                if is_valid:
                    category_results['valid'] += 1
                    validation_results['validation_summary']['valid_crawlers'] += 1
                    self.verified_crawlers[crawler_name] = crawler_info
                    logger.info(f"✅ {crawler_name} - Valid crawler implementation")
                else:
                    category_results['invalid'] += 1
                    validation_results['validation_summary']['invalid_crawlers'] += 1
                    self.failed_crawlers[crawler_name] = crawler_info
                    logger.warning(f"⚠️ {crawler_name} - Invalid crawler implementation")
            
            validation_results['categories'][category] = category_results
        
        # Calculate validation rate
        total_crawlers = validation_results['validation_summary']['valid_crawlers'] + validation_results['validation_summary']['invalid_crawlers']
        if total_crawlers > 0:
            validation_results['validation_summary']['validation_rate'] = (validation_results['validation_summary']['valid_crawlers'] / total_crawlers) * 100
        
        # Generate comprehensive report
        self._generate_crawler_report(validation_results)
        
        return validation_results
    
    def _count_lines(self, file_path: str) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r') as f:
                return len(f.readlines())
        except:
            return 0
    
    def _generate_crawler_report(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive crawler validation report."""
        logger.info("📊 Generating Crawler Validation Report...")
        
        print("\n" + "="*80)
        print("🕷️ 117 INDUSTRIAL CRAWLERS VALIDATION REPORT")
        print("="*80)
        
        print(f"\n📊 Summary:")
        print(f"  • Total Crawlers Found: {results['total_crawlers_found']}")
        print(f"  • Target Crawlers: {results['target_crawlers']}")
        print(f"  • Valid Crawlers: {results['validation_summary']['valid_crawlers']}")
        print(f"  • Invalid Crawlers: {results['validation_summary']['invalid_crawlers']}")
        print(f"  • Validation Rate: {results['validation_summary']['validation_rate']:.1f}%")
        
        print(f"\n📋 By Category:")
        for category, data in results['categories'].items():
            print(f"  • {category.replace('_', ' ').title()}: {data['valid']}/{data['total']} valid")
        
        print(f"\n✅ Top Verified Crawlers:")
        sorted_crawlers = sorted(self.verified_crawlers.items(), key=lambda x: x[1]['size_lines'], reverse=True)
        for i, (name, info) in enumerate(sorted_crawlers[:10]):
            print(f"  {i+1:2d}. {name} ({info['size_lines']} lines)")
        
        if self.failed_crawlers:
            print(f"\n⚠️ Failed Validations ({len(self.failed_crawlers)}):")
            for name, info in list(self.failed_crawlers.items())[:5]:
                print(f"  • {name} - Validation issues detected")
        
        # Industrial standards assessment
        print(f"\n🏭 Industrial Standards Assessment:")
        if results['validation_summary']['validation_rate'] >= 90:
            print("  ✅ EXCELLENT - Meets industrial standards (≥90%)")
        elif results['validation_summary']['validation_rate'] >= 75:
            print("  🟨 GOOD - Acceptable for production (≥75%)")
        elif results['validation_summary']['validation_rate'] >= 60:
            print("  🟧 NEEDS IMPROVEMENT - Below production standards")
        else:
            print("  ❌ CRITICAL - Requires immediate attention")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if results['validation_summary']['validation_rate'] < 90:
            print("  • Fix validation issues in failed crawlers")
            print("  • Implement comprehensive error handling")
            print("  • Add rate limiting and retry mechanisms")
        
        print("  • Implement real-time monitoring for all crawlers")
        print("  • Add performance metrics collection")
        print("  • Enhance security measures for data collection")
        
        print("\n" + "="*80)


def main():
    """Main entry point for crawler validation."""
    validator = CrawlerValidator()
    results = validator.validate_all_crawlers()
    
    # Return status code based on validation rate
    if results['validation_summary']['validation_rate'] >= 75:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()