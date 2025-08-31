#!/usr/bin/env python3
"""Simplified Crawler Functionality Verification
=============================================

Quick verification of crawler implementations and API connectivity.
"""import asyncio
import json
import sys
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCrawlerVerifier:
    """Simplified crawler verification without complex dependencies."""    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = {}
    
    def load_crawler_class(self, file_path: Path) -> Any:
        """Dynamically load crawler class from file."""        try:
            spec = importlib.util.spec_from_file_location("crawler_module", file_path)
            if spec is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["crawler_module"] = module
            spec.loader.exec_module(module)
            
            # Find crawler class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    name.endswith('Crawler') and 
                    name != 'BaseCrawler'):
                    return obj
            
            return None
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return None
    
    def analyze_crawler_source(self, file_path: Path) -> Dict[str, Any]:
        """Analyze crawler source code for implementation quality."""        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count meaningful implementation indicators
            real_indicators = 0
            stub_indicators = 0
            
            # Real implementation patterns
            real_patterns = [
                'async def', 'await ', 'aiohttp', 'requests', 
                'api_key', 'client_id', 'access_token',
                'json()', 'response.', 'status_code', 'headers',
                'rate_limit', 'retry', 'session'
            ]
            
            # Stub patterns
            stub_patterns = [
                'pass\n', 'NotImplemented', 'TODO', 'FIXME', 'STUB'
            ]
            
            for pattern in real_patterns:
                real_indicators += content.count(pattern)
            
            for pattern in stub_patterns:
                stub_indicators += content.count(pattern)
            
            # Calculate quality score
            total_lines = len([line for line in content.split('\n') if line.strip()])
            method_count = content.count('def ')
            
            # Determine implementation type
            if real_indicators > 20 and total_lines > 200:
                impl_type = "REAL"
                confidence = min(0.9, real_indicators / 100)
            elif real_indicators > 10 and total_lines > 100:
                impl_type = "PARTIAL"
                confidence = 0.6
            elif stub_indicators > 5 or total_lines < 50:
                impl_type = "STUB"
                confidence = 0.2
            else:
                impl_type = "UNKNOWN"
                confidence = 0.4
            
            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "implementation_type": impl_type,
                "confidence": confidence,
                "total_lines": total_lines,
                "method_count": method_count,
                "real_indicators": real_indicators,
                "stub_indicators": stub_indicators,
                "has_api_imports": any(api in content for api in ['aiohttp', 'requests', 'spotipy', 'googleapiclient']),
                "has_async": 'async def' in content
            }
            
        except Exception as e:
            return {
                "file_path": str(file_path),
                "implementation_type": "ERROR",
                "error": str(e),
                "confidence": 0.0
            }
    
    async def test_api_connectivity(self) -> Dict[str, Any]:
        """Test basic API endpoint connectivity."""        logger.info("Testing API connectivity...")
        
        connectivity_results = {}
        
        # Test endpoints without authentication
        test_endpoints = {
            'spotify': 'https://api.spotify.com/v1',
            'youtube': 'https://www.googleapis.com/youtube/v3',
            'instagram': 'https://graph.instagram.com'
        }
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                for platform, url in test_endpoints.items():
                    try:
                        async with session.get(url, timeout=10) as response:
                            connectivity_results[platform] = {
                                "accessible": True,
                                "status_code": response.status,
                                "api_available": response.status in [200, 400, 401, 403]  # 400+ expected without auth
                            }
                    except Exception as e:
                        connectivity_results[platform] = {
                            "accessible": False,
                            "error": str(e)
                        }
        
        except ImportError:
            connectivity_results = {
                "error": "aiohttp not available for connectivity testing"
            }
        
        return connectivity_results
    
    def find_priority_crawlers(self) -> Dict[str, List[Path]]:
        """Find priority crawler files (Spotify, YouTube, Instagram)."""        priority_crawlers = {
            'spotify': [],
            'youtube': [],
            'instagram': []
        }
        
        # Search in common crawler directories
        search_paths = [
            self.project_root / "crawlers",
            self.project_root / "crawlers" / "platforms",
            self.project_root / "core" / "crawlers"
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                # Find crawler files
                for pattern in ['*spotify*.py', '*youtube*.py', '*instagram*.py']:
                    files = list(search_path.glob(pattern))
                    for file in files:
                        if 'spotify' in file.name.lower():
                            priority_crawlers['spotify'].append(file)
                        elif 'youtube' in file.name.lower():
                            priority_crawlers['youtube'].append(file)
                        elif 'instagram' in file.name.lower():
                            priority_crawlers['instagram'].append(file)
        
        return priority_crawlers
    
    async def run_verification(self) -> Dict[str, Any]:
        """Run complete verification process."""        logger.info("🔍 Starting Crawler Verification")
        logger.info("=" * 50)
        
        # Find priority crawlers
        priority_crawlers = self.find_priority_crawlers()
        
        # Analyze each priority crawler
        analysis_results = {}
        for platform, files in priority_crawlers.items():
            if files:
                logger.info(f"Analyzing {platform} crawlers...")
                platform_results = []
                for file in files:
                    analysis = self.analyze_crawler_source(file)
                    platform_results.append(analysis)
                analysis_results[platform] = platform_results
            else:
                analysis_results[platform] = [{"error": "No crawler files found"}]
        
        # Test API connectivity
        connectivity_results = await self.test_api_connectivity()
        
        # Generate summary
        summary = self.generate_summary(analysis_results, connectivity_results)
        
        final_report = {
            "timestamp": "2025-08-30T07:00:00",
            "summary": summary,
            "detailed_analysis": analysis_results,
            "api_connectivity": connectivity_results,
            "recommendations": self.generate_recommendations(analysis_results, connectivity_results)
        }
        
        return final_report
    
    def generate_summary(self, analysis_results: Dict, connectivity_results: Dict) -> Dict[str, Any]:
        """Generate summary of verification results."""        total_crawlers = 0
        real_implementations = 0
        stub_implementations = 0
        
        priority_status = {}
        
        for platform, results in analysis_results.items():
            total_crawlers += len(results)
            platform_real = 0
            platform_stub = 0
            
            for result in results:
                if result.get('implementation_type') == 'REAL':
                    real_implementations += 1
                    platform_real += 1
                elif result.get('implementation_type') == 'STUB':
                    stub_implementations += 1
                    platform_stub += 1
            
            # Determine platform status
            if platform_real > 0:
                priority_status[platform] = "IMPLEMENTED"
            elif platform_stub > 0:
                priority_status[platform] = "STUB"
            else:
                priority_status[platform] = "NOT_FOUND"
        
        # API connectivity summary
        accessible_apis = sum(1 for api in connectivity_results.values() 
                            if isinstance(api, dict) and api.get('accessible', False))
        
        return {
            "total_crawlers_analyzed": total_crawlers,
            "real_implementations": real_implementations,
            "stub_implementations": stub_implementations,
            "priority_crawler_status": priority_status,
            "accessible_apis": accessible_apis,
            "total_apis_tested": len(connectivity_results) if not connectivity_results.get('error') else 0
        }
    
    def generate_recommendations(self, analysis_results: Dict, connectivity_results: Dict) -> List[str]:
        """Generate actionable recommendations."""        recommendations = []
        
        # Check priority crawlers
        for platform, results in analysis_results.items():
            if not results or results[0].get('error'):
                recommendations.append(f"CRITICAL: {platform.title()} crawler not found - needs implementation")
            else:
                real_found = any(r.get('implementation_type') == 'REAL' for r in results)
                if not real_found:
                    recommendations.append(f"CRITICAL: {platform.title()} crawler appears to be stub - needs real implementation")
        
        # Check API connectivity
        if connectivity_results.get('error'):
            recommendations.append("WARNING: Could not test API connectivity - install aiohttp for full testing")
        else:
            for platform, result in connectivity_results.items():
                if not result.get('accessible', False):
                    recommendations.append(f"WARNING: {platform.title()} API not accessible - check network connectivity")
        
        return recommendations

async def main():
    """Main execution function."""    verifier = SimpleCrawlerVerifier()
    
    # Run verification
    results = await verifier.run_verification()
    
    # Save results
    report_file = "simplified_crawler_verification_report.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print results
    print("\n✅ Crawler Verification Complete!")
    print(f"📁 Report saved to: {report_file}")
    print(f"\n📊 Summary:")
    summary = results['summary']
    print(f"   - Total crawlers analyzed: {summary['total_crawlers_analyzed']}")
    print(f"   - Real implementations: {summary['real_implementations']}")
    print(f"   - Stub implementations: {summary['stub_implementations']}")
    print(f"   - Accessible APIs: {summary['accessible_apis']}/{summary['total_apis_tested']}")
    
    print(f"\n🎯 Priority Crawler Status:")
    for platform, status in summary['priority_crawler_status'].items():
        print(f"   - {platform.title()}: {status}")
    
    if results['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())