"""
Final Implementation Validation and Status Checker
==================================================

Comprehensive validation system to verify the completeness and quality
of all implemented modules in the AI Influencer Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited
"""

import ast
import os
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import importlib.util
import inspect


@dataclass
class ModuleValidationResult:
    """Result of module validation"""
    module_path: str
    module_name: str
    is_complete: bool
    has_implementations: bool
    has_proper_structure: bool
    incomplete_methods: List[str]
    missing_docstrings: List[str]
    todo_count: int
    line_count: int
    class_count: int
    function_count: int
    complexity_score: float
    quality_score: float


class PlatformValidator:
    """Validates the entire platform implementation"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.logger = logging.getLogger(__name__)
        
        # Critical modules that must be complete
        self.critical_modules = [
            'data_management/governance/privacy.py',
            'data_management/governance/compliance.py', 
            'data_management/governance/reporting.py',
            'data_management/governance/monitoring.py',
            'monetization/platform_apis.py',
            'monitoring/enterprise_integration.py',
            'analytics/business_intelligence.py'
        ]
        
        self.validation_results = []
    
    async def validate_platform(self) -> Dict[str, Any]:
        """Comprehensive platform validation"""
        try:
            self.logger.info("Starting comprehensive platform validation...")
            
            # Validate all Python modules
            module_results = await self._validate_all_modules()
            
            # Validate critical modules specifically
            critical_results = await self._validate_critical_modules()
            
            # Generate overall assessment
            overall_assessment = await self._generate_overall_assessment(
                module_results, critical_results
            )
            
            # Create final report
            validation_report = {
                "validation_timestamp": datetime.utcnow().isoformat(),
                "platform_status": overall_assessment["status"],
                "critical_modules_status": critical_results,
                "module_statistics": overall_assessment["statistics"],
                "quality_metrics": overall_assessment["quality_metrics"],
                "recommendations": overall_assessment["recommendations"],
                "detailed_results": module_results[:50]  # Limit for readability
            }
            
            return validation_report
            
        except Exception as e:
            self.logger.error(f"Error during platform validation: {e}")
            return {"error": f"Validation failed: {e}"}
    
    async def _validate_all_modules(self) -> List[ModuleValidationResult]:
        """Validate all Python modules in the platform"""
        results = []
        
        for python_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(python_file):
                continue
                
            try:
                validation_result = await self._validate_single_module(python_file)
                results.append(validation_result)
                
            except Exception as e:
                self.logger.warning(f"Error validating {python_file}: {e}")
        
        return sorted(results, key=lambda r: r.quality_score, reverse=True)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during validation"""
        skip_patterns = [
            '__pycache__',
            '.git',
            'test_',
            'tests/',
            'migrations/',
            'node_modules',
            '.pytest_cache',
            '__init__.py'
        ]
        
        str_path = str(file_path)
        return any(pattern in str_path for pattern in skip_patterns)
    
    async def _validate_single_module(self, file_path: Path) -> ModuleValidationResult:
        """Validate a single Python module"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Analyze module structure
            analysis = self._analyze_module_structure(tree, content)
            
            # Calculate quality metrics
            quality_score = self._calculate_quality_score(analysis, content)
            
            # Get relative path
            relative_path = file_path.relative_to(self.root_path)
            
            return ModuleValidationResult(
                module_path=str(relative_path),
                module_name=file_path.stem,
                is_complete=analysis["is_complete"],
                has_implementations=analysis["has_implementations"], 
                has_proper_structure=analysis["has_proper_structure"],
                incomplete_methods=analysis["incomplete_methods"],
                missing_docstrings=analysis["missing_docstrings"],
                todo_count=analysis["todo_count"],
                line_count=len(content.splitlines()),
                class_count=analysis["class_count"],
                function_count=analysis["function_count"],
                complexity_score=analysis["complexity_score"],
                quality_score=quality_score
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            return ModuleValidationResult(
                module_path=str(file_path.relative_to(self.root_path)),
                module_name=file_path.stem,
                is_complete=False,
                has_implementations=False,
                has_proper_structure=False,
                incomplete_methods=[],
                missing_docstrings=[],
                todo_count=0,
                line_count=0,
                class_count=0,
                function_count=0,
                complexity_score=0.0,
                quality_score=0.0
            )
    
    def _analyze_module_structure(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Analyze the structure of a module"""
        analysis = {
            "is_complete": True,
            "has_implementations": False,
            "has_proper_structure": True,
            "incomplete_methods": [],
            "missing_docstrings": [],
            "todo_count": 0,
            "class_count": 0,
            "function_count": 0,
            "complexity_score": 0.0
        }
        
        # Count TODOs, FIXMEs, NotImplementedErrors
        content_lines = content.lower()
        analysis["todo_count"] = (
            content_lines.count("todo") + 
            content_lines.count("fixme") + 
            content_lines.count("notimplementederror")
        )
        
        # Analyze AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                analysis["class_count"] += 1
                if not ast.get_docstring(node):
                    analysis["missing_docstrings"].append(f"Class: {node.name}")
                    
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                analysis["function_count"] += 1
                if not ast.get_docstring(node):
                    analysis["missing_docstrings"].append(f"Function: {node.name}")
                
                # Check for incomplete implementations
                if self._is_incomplete_function(node):
                    analysis["incomplete_methods"].append(node.name)
                    analysis["is_complete"] = False
                else:
                    analysis["has_implementations"] = True
            
            elif isinstance(node, ast.Raise):
                # Check for NotImplementedError - but ignore in abstract methods
                if isinstance(node.exc, ast.Call):
                    if isinstance(node.exc.func, ast.Name):
                        if node.exc.func.id == "NotImplementedError":
                            # Check if this is in an abstract method
                            parent_function = self._find_parent_function(node, tree)
                            if parent_function and not self._is_abstract_method(parent_function):
                                analysis["is_complete"] = False
        
        # Calculate complexity score
        analysis["complexity_score"] = self._calculate_complexity(tree)
        
        return analysis
    
    def _is_incomplete_function(self, node: ast.FunctionDef) -> bool:
        """Check if a function is incomplete"""
        # Skip abstract methods
        if self._is_abstract_method(node):
            return False
            
        if len(node.body) == 0:
            return True
        
        # Check for pass-only functions (except in try/except blocks)
        if len(node.body) == 1:
            stmt = node.body[0]
            if isinstance(stmt, ast.Pass):
                return True
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                # Just a docstring
                return True
        
        # Check for NotImplementedError (but not in abstract methods)
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Raise):
                if isinstance(stmt.exc, ast.Call):
                    if isinstance(stmt.exc.func, ast.Name):
                        if stmt.exc.func.id == "NotImplementedError":
                            return True
        
        return False
    
    def _find_parent_function(self, node: ast.AST, tree: ast.AST) -> Optional[ast.FunctionDef]:
        """Find the parent function of a given node"""
        for parent in ast.walk(tree):
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for child in ast.walk(parent):
                    if child is node:
                        return parent
        return None
    
    def _is_abstract_method(self, func_node: ast.FunctionDef) -> bool:
        """Check if a function is an abstract method"""
        # Check for @abstractmethod decorator
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == "abstractmethod":
                return True
        return False
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity += 1
        
        return complexity / 10.0  # Normalize
    
    def _calculate_quality_score(self, analysis: Dict[str, Any], content: str) -> float:
        """Calculate overall quality score for a module"""
        score = 100.0
        
        # Deduct for incomplete implementations
        if not analysis["is_complete"]:
            score -= 30.0
        
        if not analysis["has_implementations"]:
            score -= 20.0
        
        # Deduct for missing docstrings
        docstring_penalty = min(len(analysis["missing_docstrings"]) * 2, 20)
        score -= docstring_penalty
        
        # Deduct for TODOs/FIXMEs
        todo_penalty = min(analysis["todo_count"] * 5, 25)
        score -= todo_penalty
        
        # Add points for good structure
        if analysis["class_count"] > 0 and analysis["function_count"] > 0:
            score += 10.0
        
        # Add points for proper length (not too short, not too long)
        line_count = len(content.splitlines())
        if 50 <= line_count <= 1000:
            score += 5.0
        
        return max(0.0, min(100.0, score))
    
    async def _validate_critical_modules(self) -> Dict[str, Any]:
        """Validate critical modules specifically"""
        critical_results = {}
        
        for module_path in self.critical_modules:
            full_path = self.root_path / module_path
            
            if full_path.exists():
                result = await self._validate_single_module(full_path)
                critical_results[module_path] = {
                    "status": "complete" if result.is_complete else "incomplete",
                    "quality_score": result.quality_score,
                    "line_count": result.line_count,
                    "has_implementations": result.has_implementations,
                    "incomplete_methods": result.incomplete_methods[:5]  # Limit output
                }
            else:
                critical_results[module_path] = {
                    "status": "missing",
                    "quality_score": 0.0,
                    "line_count": 0,
                    "has_implementations": False,
                    "incomplete_methods": []
                }
        
        return critical_results
    
    async def _generate_overall_assessment(
        self,
        module_results: List[ModuleValidationResult],
        critical_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate overall platform assessment"""
        
        # Calculate statistics
        total_modules = len(module_results)
        complete_modules = len([r for r in module_results if r.is_complete])
        high_quality_modules = len([r for r in module_results if r.quality_score >= 80])
        
        total_lines = sum(r.line_count for r in module_results)
        avg_quality = sum(r.quality_score for r in module_results) / total_modules if total_modules > 0 else 0
        
        # Critical modules assessment
        critical_complete = len([r for r in critical_results.values() if r["status"] == "complete"])
        critical_total = len(critical_results)
        
        # Determine overall status
        if critical_complete == critical_total and avg_quality >= 75:
            status = "PRODUCTION_READY"
        elif critical_complete >= critical_total * 0.8:
            status = "MOSTLY_COMPLETE"
        elif critical_complete >= critical_total * 0.5:
            status = "DEVELOPMENT_READY"
        else:
            status = "NEEDS_WORK"
        
        # Generate recommendations
        recommendations = []
        
        if avg_quality < 80:
            recommendations.append("Improve code quality and documentation across modules")
        
        if complete_modules / total_modules < 0.9:
            recommendations.append("Complete remaining incomplete module implementations")
        
        if critical_complete < critical_total:
            recommendations.append("Focus on completing critical platform modules")
        
        if not recommendations:
            recommendations.append("Platform is in excellent condition - continue monitoring and optimization")
        
        return {
            "status": status,
            "statistics": {
                "total_modules": total_modules,
                "complete_modules": complete_modules,
                "completion_rate": (complete_modules / total_modules) * 100 if total_modules > 0 else 0,
                "high_quality_modules": high_quality_modules,
                "quality_rate": (high_quality_modules / total_modules) * 100 if total_modules > 0 else 0,
                "total_lines_of_code": total_lines,
                "critical_modules_complete": critical_complete,
                "critical_completion_rate": (critical_complete / critical_total) * 100 if critical_total > 0 else 0
            },
            "quality_metrics": {
                "average_quality_score": round(avg_quality, 2),
                "platform_maturity": "High" if avg_quality >= 80 else "Medium" if avg_quality >= 60 else "Low",
                "code_coverage_estimate": min(95, complete_modules * 2) if total_modules > 0 else 0
            },
            "recommendations": recommendations
        }


async def main():
    """Main validation function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get the platform root directory
    current_dir = Path(__file__).parent
    platform_root = current_dir  # Script is in the root directory
    
    # Create validator and run validation
    validator = PlatformValidator(str(platform_root))
    
    print("🚀 Starting AI Influencer Platform Validation...")
    print("=" * 60)
    
    validation_report = await validator.validate_platform()
    
    # Print summary
    print("\n📊 VALIDATION SUMMARY:")
    print("=" * 60)
    
    if "error" in validation_report:
        print(f"❌ Validation failed: {validation_report['error']}")
        return
    
    status = validation_report["platform_status"]
    stats = validation_report["module_statistics"]
    quality = validation_report["quality_metrics"]
    
    print(f"🎯 Platform Status: {status}")
    print(f"📈 Completion Rate: {stats['completion_rate']:.1f}%")
    print(f"⭐ Quality Rate: {stats['quality_rate']:.1f}%")
    print(f"📝 Total Lines of Code: {stats['total_lines_of_code']:,}")
    print(f"🏗️ Total Modules: {stats['total_modules']}")
    print(f"✅ Complete Modules: {stats['complete_modules']}")
    print(f"🎖️ High Quality Modules: {stats['high_quality_modules']}")
    print(f"⚡ Average Quality Score: {quality['average_quality_score']}/100")
    print(f"🔥 Platform Maturity: {quality['platform_maturity']}")
    
    print("\n🔧 CRITICAL MODULES STATUS:")
    print("-" * 40)
    critical_status = validation_report["critical_modules_status"]
    for module, info in critical_status.items():
        status_emoji = "✅" if info["status"] == "complete" else "⚠️" if info["status"] == "incomplete" else "❌"
        print(f"{status_emoji} {module}: {info['status'].upper()} (Quality: {info['quality_score']:.1f})")
    
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    for i, rec in enumerate(validation_report["recommendations"], 1):
        print(f"{i}. {rec}")
    
    print("\n" + "=" * 60)
    print("🏆 AI INFLUENCER PLATFORM VALIDATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())