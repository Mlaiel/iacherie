#!/usr/bin/env python3
"""
Crawler Implementation Verification Tool
========================================

This tool analyzes all crawler implementations to distinguish between:
- Real implementations with actual functionality
- Stub implementations with placeholder code
- API connectivity status

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import os
import ast
import re
import asyncio
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CrawlerAnalysis:
    """Data structure for crawler analysis results."""
    name: str
    file_path: str
    implementation_type: str  # 'real', 'stub', 'abstract', 'incomplete'
    line_count: int
    method_count: int
    has_api_calls: bool
    has_imports: bool
    stub_indicators: List[str]
    real_indicators: List[str]
    confidence_score: float  # 0.0 = definitely stub, 1.0 = definitely real
    api_dependencies: List[str]
    test_file_exists: bool

class CrawlerVerifier:
    """Comprehensive crawler implementation analyzer."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.crawlers_path = self.project_root / "crawlers"
        self.core_crawlers_path = self.project_root / "core" / "crawlers"
        self.tests_path = self.project_root / "tests"
        
        # Patterns that indicate stub implementations
        self.stub_patterns = [
            r'^\s*pass\s*$',
            r'^\s*\.\.\.\s*$',
            r'raise\s+NotImplementedError',
            r'raise\s+NotImplemented',
            r'TODO',
            r'FIXME',
            r'STUB',
            r'PLACEHOLDER'
        ]
        
        # Patterns that indicate real implementations
        self.real_patterns = [
            r'aiohttp\.',
            r'requests\.',
            r'urllib\.',
            r'async\s+def\s+\w+.*:',
            r'await\s+',
            r'\.get\s*\(',
            r'\.post\s*\(',
            r'api\.',
            r'session\.',
            r'response\.',
            r'json\(\)',
            r'status_code',
            r'headers',
            r'params'
        ]
        
        # API-related imports that indicate real functionality
        self.api_imports = [
            'aiohttp', 'requests', 'urllib', 'httpx',
            'spotipy', 'googleapiclient', 'tweepy', 
            'instagrapi', 'selenium', 'playwright',
            'youtube_dl', 'yt_dlp', 'pytube'
        ]

    def analyze_file(self, file_path: Path) -> CrawlerAnalysis:
        """Analyze a single crawler file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return self._create_error_analysis(file_path, str(e))
        
        # Basic metrics
        lines = content.split('\n')
        line_count = len([line for line in lines if line.strip()])
        
        # Parse AST to count methods
        method_count = self._count_methods(content)
        
        # Check for stub indicators
        stub_indicators = []
        for pattern in self.stub_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                stub_indicators.extend(matches)
        
        # Check for real implementation indicators
        real_indicators = []
        for pattern in self.real_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                real_indicators.extend(matches)
        
        # Check for API dependencies
        api_dependencies = []
        has_imports = 'import' in content
        for api in self.api_imports:
            if re.search(rf'\b{api}\b', content):
                api_dependencies.append(api)
        
        has_api_calls = bool(api_dependencies) or any(
            pattern in content for pattern in ['requests.', 'aiohttp.', 'await ', 'async ']
        )
        
        # Determine implementation type and confidence
        implementation_type, confidence_score = self._classify_implementation(
            content, stub_indicators, real_indicators, has_api_calls, method_count, line_count
        )
        
        # Check for test file
        test_file_exists = self._has_test_file(file_path)
        
        return CrawlerAnalysis(
            name=file_path.stem,
            file_path=str(file_path.relative_to(self.project_root)),
            implementation_type=implementation_type,
            line_count=line_count,
            method_count=method_count,
            has_api_calls=has_api_calls,
            has_imports=has_imports,
            stub_indicators=stub_indicators[:5],  # Limit for readability
            real_indicators=real_indicators[:5],
            confidence_score=confidence_score,
            api_dependencies=api_dependencies,
            test_file_exists=test_file_exists
        )
    
    def _count_methods(self, content: str) -> int:
        """Count methods in the file."""
        try:
            tree = ast.parse(content)
            method_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    method_count += 1
            return method_count
        except:
            # Fallback to regex counting
            return len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
    
    def _classify_implementation(self, content: str, stub_indicators: List[str], 
                               real_indicators: List[str], has_api_calls: bool,
                               method_count: int, line_count: int) -> Tuple[str, float]:
        """Classify implementation type and calculate confidence score."""
        
        # Abstract base classes
        if 'ABC' in content or '@abstractmethod' in content:
            return 'abstract', 0.9
        
        # Calculate scores
        stub_score = len(stub_indicators) / max(method_count, 1)
        real_score = len(real_indicators) / max(line_count, 1) * 100
        
        # Determine classification
        if stub_score > 0.5 and real_score < 0.1:
            return 'stub', 0.1
        elif stub_score > 0.3 and real_score < 0.2:
            return 'incomplete', 0.3
        elif has_api_calls and real_score > 0.1 and line_count > 100:
            return 'real', min(0.9, 0.5 + real_score / 100)
        elif line_count > 200 and method_count > 5:
            return 'real', 0.7
        else:
            return 'incomplete', 0.4
    
    def _has_test_file(self, crawler_path: Path) -> bool:
        """Check if a test file exists for the crawler."""
        test_name = f"test_{crawler_path.stem}.py"
        test_locations = [
            self.tests_path / test_name,
            self.tests_path / "test_crawlers" / test_name,
            self.tests_path / "unit" / test_name,
            self.tests_path / "integration" / test_name
        ]
        return any(path.exists() for path in test_locations)
    
    def _create_error_analysis(self, file_path: Path, error: str) -> CrawlerAnalysis:
        """Create analysis for files that couldn't be read."""
        return CrawlerAnalysis(
            name=file_path.stem,
            file_path=str(file_path),
            implementation_type='error',
            line_count=0,
            method_count=0,
            has_api_calls=False,
            has_imports=False,
            stub_indicators=[f"ERROR: {error}"],
            real_indicators=[],
            confidence_score=0.0,
            api_dependencies=[],
            test_file_exists=False
        )
    
    def find_crawler_files(self) -> List[Path]:
        """Find all crawler Python files."""
        crawler_files = []
        
        # Find files in main crawlers directory
        if self.crawlers_path.exists():
            crawler_files.extend(self.crawlers_path.glob("**/*crawler*.py"))
            crawler_files.extend(self.crawlers_path.glob("**/platforms/*.py"))
        
        # Find files in core crawlers directory
        if self.core_crawlers_path.exists():
            crawler_files.extend(self.core_crawlers_path.glob("**/*crawler*.py"))
            crawler_files.extend(self.core_crawlers_path.glob("**/*.py"))
        
        # Remove duplicates and __init__ files
        unique_files = list(set(crawler_files))
        return [f for f in unique_files if f.name != "__init__.py"]
    
    def analyze_all_crawlers(self) -> List[CrawlerAnalysis]:
        """Analyze all crawler implementations."""
        crawler_files = self.find_crawler_files()
        logger.info(f"Found {len(crawler_files)} crawler files to analyze")
        
        analyses = []
        for file_path in crawler_files:
            logger.info(f"Analyzing {file_path.name}...")
            analysis = self.analyze_file(file_path)
            analyses.append(analysis)
        
        return analyses
    
    def generate_report(self, analyses: List[CrawlerAnalysis]) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        
        # Categorize results
        real_crawlers = [a for a in analyses if a.implementation_type == 'real']
        stub_crawlers = [a for a in analyses if a.implementation_type == 'stub']
        incomplete_crawlers = [a for a in analyses if a.implementation_type == 'incomplete']
        abstract_crawlers = [a for a in analyses if a.implementation_type == 'abstract']
        error_crawlers = [a for a in analyses if a.implementation_type == 'error']
        
        # Priority crawlers (Spotify, YouTube, Instagram)
        priority_crawlers = {}
        for crawler in ['spotify_crawler', 'youtube_crawler', 'instagram_crawler']:
            matching = [a for a in analyses if crawler in a.name.lower()]
            if matching:
                priority_crawlers[crawler] = matching[0]
        
        # Generate statistics
        total_count = len(analyses)
        real_count = len(real_crawlers)
        stub_count = len(stub_crawlers)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_crawlers': total_count,
                'real_implementations': real_count,
                'stub_implementations': stub_count,
                'incomplete_implementations': len(incomplete_crawlers),
                'abstract_implementations': len(abstract_crawlers),
                'error_implementations': len(error_crawlers),
                'real_percentage': round((real_count / total_count * 100) if total_count > 0 else 0, 2)
            },
            'priority_crawlers': {
                name: {
                    'status': crawler.implementation_type,
                    'confidence': crawler.confidence_score,
                    'has_api_calls': crawler.has_api_calls,
                    'api_dependencies': crawler.api_dependencies,
                    'test_exists': crawler.test_file_exists,
                    'file_path': crawler.file_path
                } for name, crawler in priority_crawlers.items()
            },
            'categorized_results': {
                'real_implementations': [
                    {
                        'name': a.name,
                        'confidence': a.confidence_score,
                        'file_path': a.file_path,
                        'api_dependencies': a.api_dependencies,
                        'test_exists': a.test_file_exists
                    } for a in real_crawlers
                ],
                'stub_implementations': [
                    {
                        'name': a.name,
                        'file_path': a.file_path,
                        'stub_indicators': a.stub_indicators
                    } for a in stub_crawlers
                ],
                'incomplete_implementations': [
                    {
                        'name': a.name,
                        'confidence': a.confidence_score,
                        'file_path': a.file_path,
                        'issues': a.stub_indicators
                    } for a in incomplete_crawlers
                ]
            },
            'recommendations': self._generate_recommendations(analyses, priority_crawlers)
        }
        
        return report
    
    def _generate_recommendations(self, analyses: List[CrawlerAnalysis], 
                                priority_crawlers: Dict[str, CrawlerAnalysis]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check priority crawlers
        for name, crawler in priority_crawlers.items():
            if crawler.implementation_type in ['stub', 'incomplete']:
                recommendations.append(
                    f"CRITICAL: {name} requires implementation completion - currently {crawler.implementation_type}"
                )
            elif not crawler.has_api_calls:
                recommendations.append(
                    f"WARNING: {name} may lack API integration - verify external connectivity"
                )
            elif not crawler.test_file_exists:
                recommendations.append(
                    f"MEDIUM: {name} needs test coverage - create comprehensive tests"
                )
        
        # General recommendations
        stub_count = len([a for a in analyses if a.implementation_type == 'stub'])
        if stub_count > 0:
            recommendations.append(f"Complete {stub_count} stub implementations")
        
        incomplete_count = len([a for a in analyses if a.implementation_type == 'incomplete'])
        if incomplete_count > 0:
            recommendations.append(f"Enhance {incomplete_count} incomplete implementations")
        
        return recommendations

def main():
    """Main execution function."""
    print("🔍 Crawler Implementation Verification Analysis")
    print("=" * 50)
    
    # Initialize verifier
    verifier = CrawlerVerifier()
    
    # Run analysis
    print("📊 Analyzing crawler implementations...")
    analyses = verifier.analyze_all_crawlers()
    
    # Generate report
    print("📋 Generating comprehensive report...")
    report = verifier.generate_report(analyses)
    
    # Save report
    report_file = "crawler_verification_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n✅ Analysis Complete!")
    print(f"📁 Report saved to: {report_file}")
    print(f"📊 Summary:")
    print(f"   - Total crawlers: {report['summary']['total_crawlers']}")
    print(f"   - Real implementations: {report['summary']['real_implementations']} ({report['summary']['real_percentage']}%)")
    print(f"   - Stub implementations: {report['summary']['stub_implementations']}")
    print(f"   - Incomplete implementations: {report['summary']['incomplete_implementations']}")
    
    # Priority crawler status
    print(f"\n🎯 Priority Crawler Status:")
    for name, status in report['priority_crawlers'].items():
        print(f"   - {name}: {status['status']} (confidence: {status['confidence']:.2f})")
    
    # Recommendations
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    return report

if __name__ == "__main__":
    main()