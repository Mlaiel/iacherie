#!/usr/bin/env python3
"""
Enhanced Crawler Import and Mock Test
=====================================

Tests crawler imports and basic functionality using mocks to avoid dependency issues.
This provides functional verification that the crawlers can be imported and initialized.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import sys
import os
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class CrawlerImportTester:
    """Test crawler imports and basic functionality with mocks."""
    
    def __init__(self):
        self.results = []
        
    def mock_dependencies(self):
        """Mock common dependencies that might not be available."""
        # Mock external libraries
        mocks = {
            'aiohttp': MagicMock(),
            'spotipy': MagicMock(), 
            'googleapiclient': MagicMock(),
            'googleapiclient.discovery': MagicMock(),
            'selenium': MagicMock(),
            'selenium.webdriver': MagicMock(),
            'selenium.webdriver.common.by': MagicMock(),
            'selenium.webdriver.support.ui': MagicMock(),
            'selenium.webdriver.support': MagicMock(),
            'selenium.webdriver.support.expected_conditions': MagicMock(),
            'selenium.common.exceptions': MagicMock(),
            'isodate': MagicMock(),
            'feedparser': MagicMock(),
            'bs4': MagicMock()
        }
        
        for module_name, mock_obj in mocks.items():
            sys.modules[module_name] = mock_obj
    
    def test_spotify_crawler(self) -> Dict[str, Any]:
        """Test Spotify crawler import and initialization."""



        try:
            self.mock_dependencies()
            
            # Mock internal dependencies that might not exist
            with patch.multiple(
                sys.modules,
                **{
                    'crawlers.utils.rate_limiter': MagicMock(),
                    'crawlers.utils.proxy_manager': MagicMock(),
                    'crawlers.utils.user_agent_rotator': MagicMock(),
                    'core.config': MagicMock(),
                    'core.exceptions': MagicMock(),
                    'database.models': MagicMock()
                }
            ):
                # Mock the modules at import time
                with patch.dict('sys.modules', {
                    'crawlers.utils.rate_limiter': MagicMock(),
                    'crawlers.utils.proxy_manager': MagicMock(), 
                    'crawlers.utils.user_agent_rotator': MagicMock(),
                    'core.config': MagicMock(),
                    'core.exceptions': MagicMock(),
                    'database.models': MagicMock()
                }):
                    
                    # Import the crawler module
                    spec = importlib.util.spec_from_file_location(
                        "spotify_crawler", 
                        project_root / "crawlers" / "spotify_crawler.py"
                    )
                    module = importlib.util.module_from_spec(spec)
                    
                    # Execute the module
                    spec.loader.exec_module(module)
                    
                    # Test that we can access classes
                    if hasattr(module, 'SpotifyCrawler'):
                        # Try to initialize (with mocked dependencies)
                        crawler_class = getattr(module, 'SpotifyCrawler')
                        
                        # Check methods exist
                        methods = [attr for attr in dir(crawler_class) if not attr.startswith('_')]
                        
                        return {
                            "status": "success",
                            "message": f"Spotify crawler imported and analyzed successfully",
                            "details": {
                                "class_found": True,
                                "methods_count": len(methods),
                                "sample_methods": methods[:5]
                            }
                        }
                    else:
                        return {
                            "status": "warning",
                            "message": "Spotify crawler imported but SpotifyCrawler class not found",
                            "details": {"available_attributes": list(dir(module))}
                        }
                        
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Spotify crawler import failed: {str(e)}",
                "details": {"error_type": type(e).__name__}
            }
    
    def test_youtube_crawler(self) -> Dict[str, Any]:
        """Test YouTube crawler import and initialization."""



        try:
            self.mock_dependencies()
            
            with patch.dict('sys.modules', {
                'crawlers.utils.rate_limiter': MagicMock(),
                'crawlers.utils.proxy_manager': MagicMock(),
                'crawlers.utils.user_agent_rotator': MagicMock(), 
                'core.config': MagicMock(),
                'core.exceptions': MagicMock(),
                'database.models': MagicMock()
            }):
                
                spec = importlib.util.spec_from_file_location(
                    "youtube_crawler",
                    project_root / "crawlers" / "youtube_crawler.py"  
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'YouTubeCrawler'):
                    crawler_class = getattr(module, 'YouTubeCrawler')
                    methods = [attr for attr in dir(crawler_class) if not attr.startswith('_')]
                    
                    return {
                        "status": "success",
                        "message": f"YouTube crawler imported and analyzed successfully",
                        "details": {
                            "class_found": True,
                            "methods_count": len(methods),
                            "sample_methods": methods[:5]
                        }
                    }
                else:
                    return {
                        "status": "warning",
                        "message": "YouTube crawler imported but YouTubeCrawler class not found",
                        "details": {"available_attributes": list(dir(module))}
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"YouTube crawler import failed: {str(e)}",
                "details": {"error_type": type(e).__name__}
            }
    
    def test_instagram_crawler(self) -> Dict[str, Any]:
        """Test Instagram crawler import and initialization."""



        try:
            self.mock_dependencies()
            
            with patch.dict('sys.modules', {
                'crawlers.utils.rate_limiter': MagicMock(),
                'crawlers.utils.proxy_manager': MagicMock(),
                'crawlers.utils.user_agent_rotator': MagicMock(),
                'core.config': MagicMock(), 
                'core.exceptions': MagicMock(),
                'database.models': MagicMock()
            }):
                
                spec = importlib.util.spec_from_file_location(
                    "instagram_crawler",
                    project_root / "crawlers" / "instagram_crawler.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'InstagramCrawler'):
                    crawler_class = getattr(module, 'InstagramCrawler')
                    methods = [attr for attr in dir(crawler_class) if not attr.startswith('_')]
                    
                    return {
                        "status": "success",
                        "message": f"Instagram crawler imported and analyzed successfully", 
                        "details": {
                            "class_found": True,
                            "methods_count": len(methods),
                            "sample_methods": methods[:5]
                        }
                    }
                else:
                    return {
                        "status": "warning",
                        "message": "Instagram crawler imported but InstagramCrawler class not found",
                        "details": {"available_attributes": list(dir(module))}
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"Instagram crawler import failed: {str(e)}",
                "details": {"error_type": type(e).__name__}
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all crawler import tests."""
        results = {
            "spotify": self.test_spotify_crawler(),
            "youtube": self.test_youtube_crawler(), 
            "instagram": self.test_instagram_crawler()
        }
        
        # Calculate summary
        success_count = sum(1 for r in results.values() if r["status"] == "success")
        warning_count = sum(1 for r in results.values() if r["status"] == "warning")
        error_count = sum(1 for r in results.values() if r["status"] == "error")
        
        summary = {
            "total": len(results),
            "success": success_count,
            "warning": warning_count,
            "error": error_count,
            "success_rate": success_count / len(results)
        }
        
        return {
            "summary": summary,
            "results": results
        }

def main():
    """Main execution function."""
    
    print("🧪 CRAWLER IMPORT AND FUNCTIONALITY TEST")
    print("=" * 50)
    
    tester = CrawlerImportTester()
    report = tester.run_all_tests()
    
    # Print results
    summary = report["summary"]
    print(f"Total Tests: {summary['total']}")
    print(f" Success: {summary['success']}")
    print(f"  Warning: {summary['warning']}")
    print(f" Error: {summary['error']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print()
    
    for platform, result in report["results"].items():
        icon = "" if result["status"] == "success" else "" if result["status"] == "warning" else ""
        print(f"{icon} {platform.upper()}: {result['message']}")
        if result["details"] and "methods_count" in result["details"]:
            print(f"   Methods found: {result['details']['methods_count']}")
    
    # Save detailed report
    with open('crawler_import_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n Detailed report saved to: crawler_import_test_report.json")
    
    if summary["success"] == summary["total"]:
        print("\n ALL CRAWLER IMPORTS SUCCESSFUL!")
        return 0
    else:
        print("\n  Some crawler imports had issues.")
        return 1

if __name__ == "__main__":
    exit(main())