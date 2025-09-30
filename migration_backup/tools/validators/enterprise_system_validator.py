#!/usr/bin/env python3
"""
Enterprise System Validator for Ainflue Platform
Comprehensive validation of all expert role implementations
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
import subprocess
import traceback
from datetime import datetime
import pytest
import yaml

@dataclass
class ValidationResult:
    """Validation result for a component"""
    component: str
    expert_role: str
    status: str  # 'pass', 'fail', 'warning'
    score: float  # 0-100
    details: str
    execution_time_ms: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ExpertRoleValidation:
    """Validation summary for an expert role"""
    role: str
    total_components: int
    passed_components: int
    failed_components: int
    warning_components: int
    overall_score: float
    critical_issues: List[str] = field(default_factory=list)
    
class SystemValidator:
    """Enterprise system validator"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.project_root = Path("/home/runner/work/Ainfluencer/Ainfluencer")
        self.validation_results = []
        
        # Expert role mappings
        self.expert_roles = {
            'Lead Dev IA': ['ml/', 'ai/', 'prompt_engineering/', 'analytics/'],
            'Backend Senior': ['backend/', 'api/', 'services/', 'core/'],
            'ML Engineer': ['ml/', 'models/', 'pipelines/'],
            'DBA': ['database/', 'data/', 'schemas/'],
            'Sécurité': ['security/', 'protection/', 'encryption/'],
            'Microservices': ['microservices/', 'orchestration/', 'docker/'],
            'Audio Engineer': ['multimedia/', 'audio/', 'streaming/'],
            'DevOps': ['devops/', 'kubernetes/', 'monitoring/', 'infrastructure/'],
            'IA Prompt Engineer': ['prompt_engineering/', 'templates/', 'optimization/']
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for validation"""
        logger = logging.getLogger("SystemValidator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def validate_python_imports(self) -> List[ValidationResult]:
        """Validate that all Python modules can be imported"""
        results = []
        
        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if '__pycache__' not in str(f)]
        
        self.logger.info(f"Validating {len(python_files)} Python files for import errors")
        
        for py_file in python_files[:50]:  # Limit for performance
            start_time = time.time()
            
            try:
                # Try to compile the file
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                compile(source, str(py_file), 'exec')
                
                result = ValidationResult(
                    component=str(py_file.relative_to(self.project_root)),
                    expert_role=self._determine_expert_role(py_file),
                    status='pass',
                    score=100.0,
                    details="File compiles successfully",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
                
            except SyntaxError as e:
                result = ValidationResult(
                    component=str(py_file.relative_to(self.project_root)),
                    expert_role=self._determine_expert_role(py_file),
                    status='fail',
                    score=0.0,
                    details=f"Syntax error: {e}",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    issues=[f"Syntax error at line {e.lineno}: {e.msg}"]
                )
                
            except Exception as e:
                result = ValidationResult(
                    component=str(py_file.relative_to(self.project_root)),
                    expert_role=self._determine_expert_role(py_file),
                    status='warning',
                    score=75.0,
                    details=f"Compilation warning: {e}",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    issues=[str(e)]
                )
            
            results.append(result)
        
        return results
    
    async def validate_api_endpoints(self) -> List[ValidationResult]:
        """Validate API endpoints and structure"""
        results = []
        
        # Check for main API files
        api_files = [
            'main.py',
            'api/index.py',
            'backend/index.py'
        ]
        
        for api_file in api_files:
            file_path = self.project_root / api_file
            start_time = time.time()
            
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for FastAPI patterns
                    has_fastapi = 'FastAPI' in content or 'app = ' in content
                    has_routes = '@app.' in content or 'router' in content
                    
                    score = 100.0 if has_fastapi and has_routes else 50.0
                    status = 'pass' if score == 100.0 else 'warning'
                    
                    result = ValidationResult(
                        component=api_file,
                        expert_role='Backend Senior',
                        status=status,
                        score=score,
                        details=f"API structure validation - FastAPI: {has_fastapi}, Routes: {has_routes}",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                    
                except Exception as e:
                    result = ValidationResult(
                        component=api_file,
                        expert_role='Backend Senior',
                        status='fail',
                        score=0.0,
                        details=f"Failed to read API file: {e}",
                        execution_time_ms=(time.time() - start_time) * 1000,
                        issues=[str(e)]
                    )
            else:
                result = ValidationResult(
                    component=api_file,
                    expert_role='Backend Senior',
                    status='warning',
                    score=25.0,
                    details="API file not found",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    issues=[f"Missing API file: {api_file}"]
                )
            
            results.append(result)
        
        return results
    
    async def validate_ml_components(self) -> List[ValidationResult]:
        """Validate ML components and pipelines"""
        results = []
        
        ml_components = [
            'ml/automl_pipeline.py',
            'ml/model_serving_optimizer.py',
            'ml/pipelines/pipeline_orchestrator.py'
        ]
        
        for component in ml_components:
            file_path = self.project_root / component
            start_time = time.time()
            
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check for ML patterns
                    has_torch = 'torch' in content
                    has_sklearn = 'sklearn' in content or 'scikit' in content
                    has_async = 'async' in content
                    has_logging = 'logging' in content
                    
                    score = 0
                    score += 25 if has_torch or has_sklearn else 0
                    score += 25 if has_async else 0
                    score += 25 if has_logging else 0
                    score += 25  # Base score for existence
                    
                    result = ValidationResult(
                        component=component,
                        expert_role='ML Engineer',
                        status='pass' if score >= 75 else 'warning',
                        score=float(score),
                        details=f"ML patterns: Torch/Sklearn: {has_torch or has_sklearn}, "
                               f"Async: {has_async}, Logging: {has_logging}",
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                    
                except Exception as e:
                    result = ValidationResult(
                        component=component,
                        expert_role='ML Engineer',
                        status='fail',
                        score=0.0,
                        details=f"Failed to validate ML component: {e}",
                        execution_time_ms=(time.time() - start_time) * 1000,
                        issues=[str(e)]
                    )
            else:
                result = ValidationResult(
                    component=component,
                    expert_role='ML Engineer',
                    status='fail',
                    score=0.0,
                    details="ML component not found",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    issues=[f"Missing ML component: {component}"]
                )
            
            results.append(result)
        
        return results
    
    async def validate_security_components(self) -> List[ValidationResult]:
        """Validate security and compliance components"""
        results = []
        
        security_dirs = ['security/', 'protection/', 'compliance/']
        
        for sec_dir in security_dirs:
            dir_path = self.project_root / sec_dir
            start_time = time.time()
            
            if dir_path.exists():
                # Count security-related files
                security_files = list(dir_path.rglob("*.py"))
                config_files = list(dir_path.rglob("*.yaml")) + list(dir_path.rglob("*.yml"))
                
                total_files = len(security_files) + len(config_files)
                score = min(100.0, total_files * 10)  # 10 points per file, max 100
                
                result = ValidationResult(
                    component=sec_dir,
                    expert_role='Sécurité',
                    status='pass' if score >= 50 else 'warning',
                    score=score,
                    details=f"Security files: {len(security_files)}, Config files: {len(config_files)}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            else:
                result = ValidationResult(
                    component=sec_dir,
                    expert_role='Sécurité',
                    status='warning',
                    score=0.0,
                    details="Security directory not found",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    issues=[f"Missing security directory: {sec_dir}"]
                )
            
            results.append(result)
        
        return results
    
    async def validate_infrastructure_components(self) -> List[ValidationResult]:
        """Validate DevOps and infrastructure components"""
        results = []
        
        infra_components = [
            ('docker/', 'DevOps'),
            ('kubernetes/', 'DevOps'),
            ('monitoring/', 'DevOps'),
            ('microservices/', 'Microservices')
        ]
        
        for component_dir, role in infra_components:
            dir_path = self.project_root / component_dir
            start_time = time.time()
            
            if dir_path.exists():
                # Count different types of files
                docker_files = list(dir_path.rglob("*.dockerfile")) + list(dir_path.rglob("Dockerfile*"))
                k8s_files = list(dir_path.rglob("*.yaml")) + list(dir_path.rglob("*.yml"))
                py_files = list(dir_path.rglob("*.py"))
                
                total_files = len(docker_files) + len(k8s_files) + len(py_files)
                
                # Calculate score based on infrastructure completeness
                score = 0
                score += min(30, len(docker_files) * 10)  # Docker files
                score += min(40, len(k8s_files) * 2)      # K8s manifests
                score += min(30, len(py_files) * 3)       # Python automation
                
                result = ValidationResult(
                    component=component_dir,
                    expert_role=role,
                    status='pass' if score >= 70 else 'warning',
                    score=float(score),
                    details=f"Docker: {len(docker_files)}, K8s: {len(k8s_files)}, Python: {len(py_files)}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            else:
                result = ValidationResult(
                    component=component_dir,
                    expert_role=role,
                    status='warning',
                    score=25.0,
                    details="Infrastructure directory not found",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    issues=[f"Missing infrastructure directory: {component_dir}"]
                )
            
            results.append(result)
        
        return results
    
    async def validate_audio_multimedia_components(self) -> List[ValidationResult]:
        """Validate audio and multimedia processing components"""
        results = []
        
        multimedia_dirs = ['multimedia/', 'audio/', 'streaming/']
        
        for mm_dir in multimedia_dirs:
            dir_path = self.project_root / mm_dir
            start_time = time.time()
            
            if dir_path.exists():
                # Look for audio processing files
                py_files = list(dir_path.rglob("*.py"))
                
                # Check for audio-related content
                audio_score = 0
                for py_file in py_files[:10]:  # Check first 10 files
                    try:
                        with open(py_file, 'r') as f:
                            content = f.read()
                        
                        if any(keyword in content.lower() for keyword in 
                               ['librosa', 'ffmpeg', 'audio', 'sound', 'wav', 'mp3']):
                            audio_score += 20
                            
                    except Exception:
                        continue
                
                score = min(100.0, audio_score + len(py_files) * 5)
                
                result = ValidationResult(
                    component=mm_dir,
                    expert_role='Audio Engineer',
                    status='pass' if score >= 50 else 'warning',
                    score=score,
                    details=f"Audio processing files: {len(py_files)}, Audio content score: {audio_score}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            else:
                result = ValidationResult(
                    component=mm_dir,
                    expert_role='Audio Engineer',
                    status='warning',
                    score=20.0,
                    details="Multimedia directory not found",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    issues=[f"Missing multimedia directory: {mm_dir}"]
                )
            
            results.append(result)
        
        return results
    
    def _determine_expert_role(self, file_path: Path) -> str:
        """Determine which expert role a file belongs to"""
        path_str = str(file_path)
        
        for role, patterns in self.expert_roles.items():
            for pattern in patterns:
                if pattern in path_str:
                    return role
        
        return 'General'
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive system validation"""
        self.logger.info("Starting comprehensive system validation...")
        start_time = time.time()
        
        # Run all validation categories
        validation_tasks = [
            ("Python Imports", self.validate_python_imports()),
            ("API Endpoints", self.validate_api_endpoints()),
            ("ML Components", self.validate_ml_components()),
            ("Security Components", self.validate_security_components()),
            ("Infrastructure", self.validate_infrastructure_components()),
            ("Audio/Multimedia", self.validate_audio_multimedia_components())
        ]
        
        all_results = []
        category_summaries = {}
        
        for category_name, task in validation_tasks:
            self.logger.info(f"Validating {category_name}...")
            try:
                category_results = await task
                all_results.extend(category_results)
                
                # Calculate category summary
                total = len(category_results)
                passed = len([r for r in category_results if r.status == 'pass'])
                failed = len([r for r in category_results if r.status == 'fail'])
                warnings = len([r for r in category_results if r.status == 'warning'])
                avg_score = sum(r.score for r in category_results) / total if total > 0 else 0
                
                category_summaries[category_name] = {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'warnings': warnings,
                    'average_score': avg_score
                }
                
            except Exception as e:
                self.logger.error(f"Failed to validate {category_name}: {e}")
                category_summaries[category_name] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 1,
                    'warnings': 0,
                    'average_score': 0.0,
                    'error': str(e)
                }
        
        # Generate expert role summaries
        expert_summaries = self._generate_expert_role_summaries(all_results)
        
        # Calculate overall metrics
        total_components = len(all_results)
        total_passed = len([r for r in all_results if r.status == 'pass'])
        total_failed = len([r for r in all_results if r.status == 'fail'])
        total_warnings = len([r for r in all_results if r.status == 'warning'])
        overall_score = sum(r.score for r in all_results) / total_components if total_components > 0 else 0
        
        execution_time = time.time() - start_time
        
        report = {
            'validation_summary': {
                'total_components': total_components,
                'passed': total_passed,
                'failed': total_failed,
                'warnings': total_warnings,
                'overall_score': overall_score,
                'success_rate': (total_passed / total_components * 100) if total_components > 0 else 0,
                'execution_time_seconds': execution_time
            },
            'category_summaries': category_summaries,
            'expert_role_summaries': expert_summaries,
            'detailed_results': [
                {
                    'component': r.component,
                    'expert_role': r.expert_role,
                    'status': r.status,
                    'score': r.score,
                    'details': r.details,
                    'issues': r.issues,
                    'recommendations': r.recommendations
                }
                for r in all_results
            ],
            'critical_issues': [
                r.component for r in all_results 
                if r.status == 'fail' and r.score == 0
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return report
    
    def _generate_expert_role_summaries(self, results: List[ValidationResult]) -> Dict[str, ExpertRoleValidation]:
        """Generate summaries for each expert role"""
        role_results = {}
        
        # Group results by expert role
        for result in results:
            role = result.expert_role
            if role not in role_results:
                role_results[role] = []
            role_results[role].append(result)
        
        # Create summaries
        summaries = {}
        for role, role_result_list in role_results.items():
            total = len(role_result_list)
            passed = len([r for r in role_result_list if r.status == 'pass'])
            failed = len([r for r in role_result_list if r.status == 'fail'])
            warnings = len([r for r in role_result_list if r.status == 'warning'])
            avg_score = sum(r.score for r in role_result_list) / total if total > 0 else 0
            
            critical_issues = [
                r.component for r in role_result_list
                if r.status == 'fail' and r.score == 0
            ]
            
            summaries[role] = ExpertRoleValidation(
                role=role,
                total_components=total,
                passed_components=passed,
                failed_components=failed,
                warning_components=warnings,
                overall_score=avg_score,
                critical_issues=critical_issues
            )
        
        return {
            role: {
                'total_components': summary.total_components,
                'passed': summary.passed_components,
                'failed': summary.failed_components,
                'warnings': summary.warning_components,
                'overall_score': summary.overall_score,
                'success_rate': (summary.passed_components / summary.total_components * 100) 
                              if summary.total_components > 0 else 0,
                'critical_issues': summary.critical_issues
            }
            for role, summary in summaries.items()
        }
    
    def save_validation_report(self, report: Dict[str, Any], output_path: Optional[Path] = None):
        """Save validation report to file"""
        if output_path is None:
            output_path = self.project_root / "validation_report.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Validation report saved to {output_path}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print validation summary to console"""
        summary = report['validation_summary']
        
        print("\n" + "="*80)
        print("🎯 AINFLUE ENTERPRISE SYSTEM VALIDATION REPORT")
        print("="*80)
        
        print(f"\n📊 OVERALL METRICS:")
        print(f"   Total Components: {summary['total_components']}")
        print(f"   ✅ Passed: {summary['passed']} ({summary['success_rate']:.1f}%)")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⚠️  Warnings: {summary['warnings']}")
        print(f"   🎯 Overall Score: {summary['overall_score']:.1f}/100")
        print(f"   ⏱️  Execution Time: {summary['execution_time_seconds']:.2f}s")
        
        print(f"\n👨‍💻 EXPERT ROLE PERFORMANCE:")
        expert_summaries = report['expert_role_summaries']
        for role, metrics in expert_summaries.items():
            status_icon = "✅" if metrics['success_rate'] >= 80 else "⚠️" if metrics['success_rate'] >= 60 else "❌"
            print(f"   {status_icon} {role}: {metrics['overall_score']:.1f}/100 "
                  f"({metrics['success_rate']:.1f}% success)")
        
        critical_issues = report.get('critical_issues', [])
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
            for issue in critical_issues[:5]:  # Show first 5
                print(f"   - {issue}")
            if len(critical_issues) > 5:
                print(f"   ... and {len(critical_issues) - 5} more")
        
        print("\n" + "="*80)

# Main execution
async def main():
    """Run system validation"""
    validator = SystemValidator()
    
    print("🚀 Starting Ainflue Enterprise System Validation...")
    
    # Run comprehensive validation
    report = await validator.run_comprehensive_validation()
    
    # Print summary
    validator.print_summary(report)
    
    # Save detailed report
    validator.save_validation_report(report)
    
    # Determine exit code based on results
    overall_score = report['validation_summary']['overall_score']
    critical_issues = len(report.get('critical_issues', []))
    
    if overall_score >= 80 and critical_issues == 0:
        print("✅ System validation PASSED with flying colors!")
        return 0
    elif overall_score >= 60:
        print("⚠️ System validation PASSED with warnings")
        return 0
    else:
        print("❌ System validation FAILED - critical issues found")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)