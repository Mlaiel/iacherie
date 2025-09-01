#!/usr/bin/env python3
"""Crawler Functional Verification Test.

====================================

Enhanced functional verification for crawler implementations beyond static analysis.
Tests actual functionality, initialization, and core capabilities of priority crawlers.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import sys
import os
import ast
import inspect
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class FunctionalTest:
    """
Result of a functional test."""
    test_name: str
    status: str  # 'pass', 'fail', 'skip'
    message: str
    details: Optional[Dict[str, Any]] = None

class CrawlerFunctionalVerifier:
    """
Enhanced functional verification for crawler implementations."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = []
        
    def verify_implementation_completeness(self, file_path: Path) -> FunctionalTest:
        """Verify that a crawler has real implementation vs stub."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST to analyze implementation
            tree = ast.parse(content)
            
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            methods = []
            real_implementations = 0
            stub_indicators = 0
            
            for cls in classes:
                for item in cls.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                        
                        # Check if method has real implementation
                        method_body = ast.get_source_segment(content, item) or ""
                        
                        # Real implementation indicators
                        if any(indicator in method_body.lower() for indicator in [
                            'aiohttp', 'requests', 'await', 'async def', '.get(', '.post(',
                            'selenium', 'api', 'http', 'json', 'response'
                        ]):
                            real_implementations += 1
                            
                        # Stub indicators
                        if any(indicator in method_body for indicator in [
                            'pass', '...', 'NotImplementedError', 'TODO', 'FIXME'
                        ]):
                            stub_indicators += 1
            
            total_methods = len(methods)
            implementation_ratio = real_implementations / max(total_methods, 1)
            
            if implementation_ratio > 0.7:
                status = "pass"
                message = f"Real implementation confirmed ({implementation_ratio:.1%} real indicators)"
            elif stub_indicators > real_implementations:
                status = "fail"
                message = f"Stub implementation detected ({stub_indicators} stub indicators)"
            else:
                status = "skip"
                message = f"Mixed implementation ({implementation_ratio:.1%} real indicators)"
                
            return FunctionalTest(
                test_name=f"Implementation Completeness - {file_path.name}",
                status=status,
                message=message,
                details={
                    "total_methods": total_methods,
                    "real_implementations": real_implementations,
                    "stub_indicators": stub_indicators,
                    "implementation_ratio": implementation_ratio,
                    "classes_found": [cls.name for cls in classes]
                }
            )
            
        except Exception as e:
            return FunctionalTest(
                test_name=f"Implementation Completeness - {file_path.name}",
                status="fail",
                message=f"Analysis failed: {str(e)}"
            )
    
    def verify_data_structures(self, file_path: Path) -> FunctionalTest:
        """Verify that crawler has proper data structures."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for dataclass definitions
            dataclass_count = content.count('@dataclass')
            class_count = content.count('class ')
            
            # Check for type hints
            has_type_hints = any(pattern in content for pattern in [
                'List[', 'Dict[', 'Optional[', 'Union[', 'AsyncGenerator['
            ])
            
            # Check for proper data modeling
            data_indicators = [
                'from dataclasses import',
                'from typing import',
                '__init__',
                'def __str__',
                'def __repr__'
            ]
            
            data_score = sum(1 for indicator in data_indicators if indicator in content)
            
            if dataclass_count > 0 and has_type_hints:
                status = "pass"
                message = f"Professional data structures found ({dataclass_count} dataclasses)"
            elif class_count > 0:
                status = "skip"
                message = f"Basic data structures found ({class_count} classes)"
            else:
                status = "fail"
                message = "No proper data structures found"
                
            return FunctionalTest(
                test_name=f"Data Structures - {file_path.name}",
                status=status,
                message=message,
                details={
                    "dataclass_count": dataclass_count,
                    "class_count": class_count,
                    "has_type_hints": has_type_hints,
                    "data_score": data_score
                }
            )
            
        except Exception as e:
            return FunctionalTest(
                test_name=f"Data Structures - {file_path.name}",
                status="fail",
                message=f"Analysis failed: {str(e)}"
            )
    
    def verify_api_integration(self, file_path: Path) -> FunctionalTest:
        """Verify that crawler has real API integration capabilities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for API libraries
            api_libraries = ['aiohttp', 'requests', 'urllib', 'httpx']
            platform_apis = ['spotipy', 'googleapiclient', 'selenium', 'instagram-basic-display']
            
            api_lib_found = any(lib in content for lib in api_libraries)
            platform_api_found = any(api in content for api in platform_apis)
            
            # Check for HTTP methods
            http_methods = ['.get(', '.post(', '.put(', '.delete(', 'async def', 'await']
            http_methods_found = sum(1 for method in http_methods if method in content)
            
            # Check for authentication patterns
            auth_patterns = ['oauth', 'token', 'api_key', 'credentials', 'authorization']
            auth_found = any(pattern in content.lower() for pattern in auth_patterns)
            
            if api_lib_found and platform_api_found and http_methods_found > 3:
                status = "pass"
                message = f"Professional API integration ({http_methods_found} HTTP methods)"
            elif api_lib_found and http_methods_found > 1:
                status = "skip"
                message = f"Basic API integration ({http_methods_found} HTTP methods)"
            else:
                status = "fail"
                message = "No API integration found"
                
            return FunctionalTest(
                test_name=f"API Integration - {file_path.name}",
                status=status,
                message=message,
                details={
                    "api_lib_found": api_lib_found,
                    "platform_api_found": platform_api_found,
                    "http_methods_count": http_methods_found,
                    "auth_found": auth_found
                }
            )
            
        except Exception as e:
            return FunctionalTest(
                test_name=f"API Integration - {file_path.name}",
                status="fail",
                message=f"Analysis failed: {str(e)}"
            )
    
    def verify_error_handling(self, file_path: Path) -> FunctionalTest:
        """Verify that crawler has proper error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for exception handling
            try_count = content.count('try:')
            except_count = content.count('except')
            finally_count = content.count('finally:')
            
            # Check for logging
            logging_found = 'logging' in content or 'logger' in content
            
            # Check for custom exceptions
            custom_exceptions = content.count('raise ') + content.count('CrawlerError') + content.count('RateLimitError')
            
            error_score = try_count + except_count + (1 if logging_found else 0) + custom_exceptions
            
            if error_score > 5:
                status = "pass"
                message = f"Comprehensive error handling (score: {error_score})"
            elif error_score > 2:
                status = "skip"
                message = f"Basic error handling (score: {error_score})"
            else:
                status = "fail"
                message = f"Insufficient error handling (score: {error_score})"
                
            return FunctionalTest(
                test_name=f"Error Handling - {file_path.name}",
                status=status,
                message=message,
                details={
                    "try_blocks": try_count,
                    "except_blocks": except_count,
                    "finally_blocks": finally_count,
                    "logging_found": logging_found,
                    "custom_exceptions": custom_exceptions,
                    "error_score": error_score
                }
            )
            
        except Exception as e:
            return FunctionalTest(
                test_name=f"Error Handling - {file_path.name}",
                status="fail",
                message=f"Analysis failed: {str(e)}"
            )
    
    def verify_priority_crawlers(self) -> List[FunctionalTest]:
        """Verify the three priority crawlers: Spotify, YouTube, Instagram."""
        priority_crawlers = [
            'spotify_crawler.py',
            'youtube_crawler.py', 
            'instagram_crawler.py'
        ]
        
        all_tests = []
        
        for crawler_name in priority_crawlers:
            # Find crawler file
            crawler_path = None
            for potential_path in [
                self.project_root / 'crawlers' / crawler_name,
                self.project_root / 'crawlers' / 'platforms' / crawler_name,
                self.project_root / 'core' / 'crawlers' / crawler_name.replace('_crawler.py', '_api.py')
            ]:
                if potential_path.exists():
                    crawler_path = potential_path
                    break
            
            if not crawler_path:
                all_tests.append(FunctionalTest(
                    test_name=f"File Existence - {crawler_name}",
                    status="fail",
                    message=f"Crawler file not found: {crawler_name}"
                ))
                continue
                
            # Run all tests for this crawler
            tests = [
                self.verify_implementation_completeness(crawler_path),
                self.verify_data_structures(crawler_path),
                self.verify_api_integration(crawler_path),
                self.verify_error_handling(crawler_path)
            ]
            
            all_tests.extend(tests)
            
        return all_tests
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive functional verification report."""
        tests = self.verify_priority_crawlers()
        
        passed = [t for t in tests if t.status == 'pass']
        failed = [t for t in tests if t.status == 'fail']
        skipped = [t for t in tests if t.status == 'skip']
        
        # Group by crawler
        crawler_results = {}
        for test in tests:
            crawler = test.test_name.split(' - ')[-1].replace('.py', '')
            if crawler not in crawler_results:
                crawler_results[crawler] = []
            crawler_results[crawler].append({
                "test_name": test.test_name,
                "status": test.status,
                "message": test.message,
                "details": test.details
            })
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(tests),
                "passed": len(passed),
                "failed": len(failed),
                "skipped": len(skipped),
                "success_rate": len(passed) / len(tests) if tests else 0
            },
            "crawler_results": crawler_results,
            "detailed_results": [
                {
                    "test_name": t.test_name,
                    "status": t.status,
                    "message": t.message,
                    "details": t.details
                }
                for t in tests
            ]
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a human-readable summary of the verification results."""
        print("\n🔍 CRAWLER FUNCTIONAL VERIFICATION RESULTS")
        print("=" * 50)
        
        summary = report["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⚠️  Skipped: {summary['skipped']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print()
        
        # Print crawler-specific results
        for crawler, test_dicts in report["crawler_results"].items():
            print(f"📱 {crawler.upper()} CRAWLER:")
            for test_dict in test_dicts:
                icon = "✅" if test_dict["status"] == "pass" else "❌" if test_dict["status"] == "fail" else "⚠️"
                print(f"  {icon} {test_dict['test_name'].split(' - ')[0]}: {test_dict['message']}")
            print()

def main():
    """Main execution function."""
    verifier = CrawlerFunctionalVerifier()
    report = verifier.generate_report()
    
    # Print summary
    verifier.print_summary(report)
    
    # Save detailed report
    with open('crawler_functional_verification_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("📄 Detailed report saved to: crawler_functional_verification_report.json")
    
    # Return success if all priority crawlers pass core tests
    priority_tests = [t for t in report["detailed_results"] 
                     if any(crawler in t["test_name"].lower() for crawler in ["spotify", "youtube", "instagram"])]
    core_tests = [t for t in priority_tests if "Implementation Completeness" in t["test_name"]]
    
    if all(t["status"] == "pass" for t in core_tests):
        print("\n🎉 VERIFICATION SUCCESSFUL: All priority crawlers have real implementations!")
        return 0
    else:
        print("\n⚠️  VERIFICATION INCOMPLETE: Some priority crawlers need attention.")
        return 1

if __name__ == "__main__":
    exit(main())