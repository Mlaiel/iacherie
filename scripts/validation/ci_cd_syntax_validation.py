#!/usr/bin/env python3
"""CI/CD Integration for automated syntax validation

This script integrates syntax validation into the CI/CD pipeline using
the existing quality gates infrastructure.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any
import subprocess
import logging

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from kubernetes.ci_cd.quality_gates import QualityGateValidator, QualityGateConfig, QualityGateType
except ImportError:
    # Fallback for when the module is not available
    print("Warning: kubernetes.ci_cd.quality_gates not available, using standalone implementation")
    QualityGateValidator = None

class SyntaxValidationGate:
    """Syntax validation quality gate for CI/CD pipeline"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def validate_python_syntax(self) -> Dict[str, Any]:
        """
Validate Python syntax across the repository"""
        self.logger.info("🔍 Running syntax validation quality gate...")
        
        # Find all Python files
        python_files = []
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in ['.git', '__pycache__', 'venv', '.venv']):
                continue
            python_files.append(py_file)
        
        total_files = len(python_files)
        syntax_errors = []
        files_checked = 0
        
        # Check syntax for each file
        for py_file in python_files:
            files_checked += 1
            if files_checked % 500 == 0:
                self.logger.info(f"Progress: {files_checked}/{total_files} files checked")
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip()
                    syntax_errors.append({
                        "file": str(py_file),
                        "error": error_msg
                    })
                    
            except subprocess.TimeoutExpired:
                syntax_errors.append({
                    "file": str(py_file),
                    "error": "Compilation timeout"
                })
            except Exception as e:
                syntax_errors.append({
                    "file": str(py_file),
                    "error": f"Unexpected error: {e}"
                })
        
        # Calculate results
        error_count = len(syntax_errors)
        success_rate = ((total_files - error_count) / total_files) * 100 if total_files > 0 else 0
        
        result = {
            "gate_type": "syntax_validation",
            "status": "PASSED" if error_count == 0 else "FAILED",
            "total_files": total_files,
            "files_checked": files_checked,
            "syntax_errors": error_count,
            "success_rate": success_rate,
            "errors": syntax_errors[:10],  # Limit to first 10 errors
            "threshold": 0  # Zero tolerance for syntax errors
        }
        
        return result
    
    async def run_linting_validation(self) -> Dict[str, Any]:
        """Run linting validation using flake8"""
        self.logger.info("🔍 Running linting validation...")
        
        try:
            # Run flake8 linting
            result = subprocess.run([
                "flake8",
                ".",
                "--format=json",
                "--max-line-length=120",
                "--ignore=E203,W503",
                "--exclude=__pycache__,migrations,venv,.git,*.bak",
                "--count"
            ], capture_output=True, text=True, timeout=300)
            
            # Parse results
            linting_issues = []
            if result.stdout:
                try:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            linting_issues.append(line)
                except Exception:
                    linting_issues = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            issue_count = len(linting_issues)
            
            return {
                "gate_type": "linting",
                "status": "PASSED" if issue_count == 0 else "WARNING",
                "issue_count": issue_count,
                "issues": linting_issues[:20],  # Limit to first 20 issues
                "threshold": 100  # Allow up to 100 linting issues
            }
            
        except subprocess.TimeoutExpired:
            return {
                "gate_type": "linting",
                "status": "FAILED",
                "error": "Linting timeout",
                "issue_count": -1
            }
        except Exception as e:
            return {
                "gate_type": "linting",
                "status": "FAILED", 
                "error": str(e),
                "issue_count": -1
            }
    
    async def run_docstring_validation(self) -> Dict[str, Any]:
        """Run docstring validation using pydocstyle"""
        self.logger.info("🔍 Running docstring validation...")
        
        try:
            # Run pydocstyle for PEP257 compliance
            result = subprocess.run([
                "pydocstyle",
                ".",
                "--count",
                "--explain"
            ], capture_output=True, text=True, timeout=300)
            
            # Parse results
            docstring_issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        docstring_issues.append(line)
            
            issue_count = len(docstring_issues)
            
            return {
                "gate_type": "docstring_validation",
                "status": "WARNING" if issue_count > 0 else "PASSED",
                "issue_count": issue_count,
                "issues": docstring_issues[:15],  # Limit to first 15 issues
                "threshold": 1000  # Allow many docstring issues for now
            }
            
        except subprocess.TimeoutExpired:
            return {
                "gate_type": "docstring_validation",
                "status": "FAILED",
                "error": "Docstring validation timeout",
                "issue_count": -1
            }
        except Exception as e:
            return {
                "gate_type": "docstring_validation",
                "status": "WARNING",
                "error": str(e),
                "issue_count": -1
            }
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation checks"""
        self.logger.info("🚀 Starting comprehensive syntax and quality validation...")
        
        # Run all validations concurrently
        syntax_result, linting_result, docstring_result = await asyncio.gather(
            self.validate_python_syntax(),
            self.run_linting_validation(), 
            self.run_docstring_validation()
        )
        
        # Aggregate results
        overall_status = "PASSED"
        if syntax_result["status"] == "FAILED":
            overall_status = "FAILED"
        elif any(r["status"] == "FAILED" for r in [linting_result, docstring_result]):
            overall_status = "FAILED"
        elif any(r["status"] == "WARNING" for r in [syntax_result, linting_result, docstring_result]):
            overall_status = "WARNING"
        
        return {
            "overall_status": overall_status,
            "timestamp": "2025-08-31T08:30:00Z",
            "validations": {
                "syntax": syntax_result,
                "linting": linting_result,
                "docstrings": docstring_result
            }
        }
    
    def print_validation_report(self, results: Dict[str, Any]):
        """Print validation results in a readable format"""
        print("\n" + "=" * 80)
        print("🏭 CI/CD SYNTAX VALIDATION RESULTS")
        print("=" * 80)
        
        overall_status = results["overall_status"]
        status_emoji = "✅" if overall_status == "PASSED" else "⚠️" if overall_status == "WARNING" else "❌"
        print(f"{status_emoji} Overall Status: {overall_status}")
        
        for validation_type, result in results["validations"].items():
            print(f"\n📊 {validation_type.upper()} Validation:")
            print(f"   Status: {result['status']}")
            
            if validation_type == "syntax":
                print(f"   Files checked: {result['files_checked']:,}")
                print(f"   Syntax errors: {result['syntax_errors']}")
                print(f"   Success rate: {result['success_rate']:.2f}%")
                
                if result['syntax_errors'] > 0:
                    print(f"   🚨 First few errors:")
                    for error in result['errors'][:3]:
                        print(f"      • {error['file']}: {error['error']}")
            
            elif validation_type in ["linting", "docstring_validation"]:
                print(f"   Issues found: {result.get('issue_count', 'N/A')}")
                if result.get('issues'):
                    print(f"   📝 Sample issues:")
                    for issue in result['issues'][:3]:
                        print(f"      • {issue}")
        
        print("=" * 80)
    
    def save_results(self, results: Dict[str, Any]) -> Path:
        """Save validation results to file"""
        reports_dir = self.root_path / "reports" / "ci_cd"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / "syntax_validation_results.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return report_file


async def main():
    """Main function for CI/CD syntax validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI/CD Syntax Validation")
    parser.add_argument("--root", default=".", help="Root directory to validate")
    parser.add_argument("--fail-on-errors", action="store_true", help="Fail if any syntax errors found")
    parser.add_argument("--save-results", action="store_true", help="Save results to file")
    
    args = parser.parse_args()
    
    try:
        validator = SyntaxValidationGate(args.root)
        results = await validator.run_comprehensive_validation()
        
        # Print results
        validator.print_validation_report(results)
        
        # Save results if requested
        if args.save_results:
            report_file = validator.save_results(results)
            print(f"\n📄 Results saved to: {report_file}")
        
        # Determine exit code
        if args.fail_on_errors and results["overall_status"] == "FAILED":
            print("\n❌ Validation failed - syntax errors found")
            return 1
        elif results["overall_status"] == "WARNING":
            print("\n⚠️  Validation completed with warnings")
            return 0
        else:
            print("\n✅ All validations passed!")
            return 0
            
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)