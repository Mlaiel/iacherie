#!/usr/bin/env python3
"""MongoDB Test Runner
===================

Comprehensive test runner for MongoDB module with reporting and analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class MongoDBTestRunner:
    """MongoDB test runner with comprehensive reporting."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.report_dir = self.test_dir / "reports"
        self.report_dir.mkdir(exist_ok=True)
    
    def run_tests(self, test_type="all", verbose=False, coverage=False):
        """Run MongoDB tests with specified options."""
        print("🚀 Starting MongoDB Test Suite")
        print("=" * 50)
        
        # Prepare pytest command
        cmd = ["python", "-m", "pytest", str(self.test_dir)]
        
        # Add options based on test type
        if test_type == "unit":
            cmd.extend(["-m", "not integration and not performance"])
        elif test_type == "integration":
            cmd.extend(["-m", "integration"])
        elif test_type == "performance":
            cmd.extend(["-m", "performance"])
        elif test_type == "security":
            cmd.extend(["-m", "security"])
        
        # Add verbose output
        if verbose:
            cmd.append("-v")
        
        # Add coverage reporting
        if coverage:
            cmd.extend(["--cov=mongodb", "--cov-report=html", "--cov-report=term"])
        
        # Add additional pytest options
        cmd.extend([
            "--tb=short",
            "--durations=10",
            f"--junitxml={self.report_dir}/junit_report.xml",
            f"--html={self.report_dir}/html_report.html",
            "--self-contained-html"
        ])
        
        print(f"Running command: {' '.join(cmd)}")
        print("-" * 50)
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
            end_time = time.time()
            
            # Process results
            self._process_test_results(result, end_time - start_time, test_type)
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def _process_test_results(self, result, duration, test_type):
        """Process and report test results."""
        print("\n📊 Test Results")
        print("=" * 50)
        
        # Basic result info
        print(f"Test Type: {test_type}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Exit Code: {result.returncode}")
        
        # Output analysis
        output_lines = result.stdout.split('\n')
        error_lines = result.stderr.split('\n')
        
        # Extract test statistics
        stats = self._extract_test_stats(output_lines)
        
        # Display results
        if stats:
            print(f"\n✅ Passed: {stats.get('passed', 0)}")
            print(f"❌ Failed: {stats.get('failed', 0)}")
            print(f"⚠️  Skipped: {stats.get('skipped', 0)}")
            print(f"⏱️  Warnings: {stats.get('warnings', 0)}")
        
        # Save detailed report
        self._save_detailed_report(result, duration, test_type, stats)
        
        # Display summary
        if result.returncode == 0:
            print("\n🎉 All tests passed successfully!")
        else:
            print("\n💥 Some tests failed. Check the detailed report.")
            if error_lines:
                print("\nError output:")
                for line in error_lines[-10:]:  # Show last 10 error lines
                    if line.strip():
                        print(f"  {line}")
    
    def _extract_test_stats(self, output_lines):
        """Extract test statistics from pytest output."""
        stats = {}
        
        for line in output_lines:
            if "passed" in line and "failed" in line:
                # Parse pytest summary line
                # Example: "5 passed, 2 failed, 1 skipped in 2.34s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        stats['passed'] = int(parts[i-1])
                    elif part == "failed" and i > 0:
                        stats['failed'] = int(parts[i-1])
                    elif part == "skipped" and i > 0:
                        stats['skipped'] = int(parts[i-1])
                    elif part == "warnings" and i > 0:
                        stats['warnings'] = int(parts[i-1])
                break
        
        return stats
    
    def _save_detailed_report(self, result, duration, test_type, stats):
        """Save detailed test report to file."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type,
            "duration": duration,
            "exit_code": result.returncode,
            "statistics": stats,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        report_file = self.report_dir / f"test_report_{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Detailed report saved to: {report_file}")
    
    def run_performance_benchmarks(self):
        """Run performance benchmark tests."""
        print("\n🏃‍♂️ Running Performance Benchmarks")
        print("=" * 50)
        
        # Performance specific tests
        benchmarks = [
            ("Query Performance", "test_query_performance_benchmark"),
            ("Cache Performance", "test_cache_performance_benchmark"),
            ("Connection Pool", "test_connection_pool_performance"),
            ("Bulk Operations", "test_bulk_insert_performance")
        ]
        
        results = {}
        
        for name, test_pattern in benchmarks:
            print(f"\n🔍 Running {name} benchmark...")
            
            cmd = [
                "python", "-m", "pytest", 
                str(self.test_dir),
                "-k", test_pattern,
                "-v",
                "--tb=short"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
            end_time = time.time()
            
            results[name] = {
                "duration": end_time - start_time,
                "passed": result.returncode == 0,
                "output": result.stdout
            }
            
            status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
            print(f"  {status} ({end_time - start_time:.2f}s)")
        
        # Save benchmark results
        benchmark_report = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": results
        }
        
        benchmark_file = self.report_dir / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(benchmark_file, 'w') as f:
            json.dump(benchmark_report, f, indent=2)
        
        print(f"\n📈 Benchmark report saved to: {benchmark_file}")
        
        return all(r["passed"] for r in results.values())
    
    def run_security_audit(self):
        """Run security-focused tests."""
        print("\n🔒 Running Security Audit")
        print("=" * 50)
        
        security_tests = [
            ("Encryption Tests", "test_encryption"),
            ("Access Control", "test_access_control"),
            ("Audit Logging", "test_audit"),
            ("Data Masking", "test_masking"),
            ("Compliance", "test_compliance")
        ]
        
        security_results = {}
        
        for name, test_pattern in security_tests:
            print(f"\n🛡️  Testing {name}...")
            
            cmd = [
                "python", "-m", "pytest",
                str(self.test_dir),
                "-k", test_pattern,
                "-v",
                "--tb=short"
            ]
            
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
            
            security_results[name] = {
                "passed": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            status = "🔒 SECURE" if result.returncode == 0 else "⚠️  ISSUES"
            print(f"  {status}")
        
        # Generate security report
        security_report = {
            "timestamp": datetime.now().isoformat(),
            "security_tests": security_results,
            "overall_status": "SECURE" if all(r["passed"] for r in security_results.values()) else "ISSUES_FOUND"
        }
        
        security_file = self.report_dir / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(security_file, 'w') as f:
            json.dump(security_report, f, indent=2)
        
        print(f"\n🔐 Security audit saved to: {security_file}")
        
        return security_report["overall_status"] == "SECURE"
    
    def generate_coverage_report(self):
        """Generate test coverage report."""
        print("\n📊 Generating Coverage Report")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "--cov=mongodb",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=json",
            f"--cov-config={self.test_dir}/.coveragerc"
        ]
        
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Coverage report generated successfully")
            print(f"📂 HTML report: {project_root}/htmlcov/index.html")
        else:
            print("❌ Failed to generate coverage report")
            print(result.stderr)
        
        return result.returncode == 0

def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="MongoDB Test Runner")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "performance", "security"],
        default="all",
        nargs="?",
        help="Type of tests to run"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("-b", "--benchmark", action="store_true", help="Run performance benchmarks")
    parser.add_argument("-s", "--security", action="store_true", help="Run security audit")
    
    args = parser.parse_args()
    
    runner = MongoDBTestRunner()
    
    success = True
    
    # Run main tests
    if not runner.run_tests(args.test_type, args.verbose, args.coverage):
        success = False
    
    # Run benchmarks if requested
    if args.benchmark:
        if not runner.run_performance_benchmarks():
            success = False
    
    # Run security audit if requested
    if args.security:
        if not runner.run_security_audit():
            success = False
    
    # Generate coverage report if requested
    if args.coverage:
        runner.generate_coverage_report()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Check the reports for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()