#!/usr/bin/env python3
"""🔄 API Breaking Changes Detector - Ainflue Platform
================================================================
Automatic detection of API breaking changes and versioning validation
================================================================
"""

import ast
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import argparse
import subprocess


@dataclass
class APIEndpoint:
    """API endpoint definition"""
    path: str
    method: str
    function_name: str
    file_path: str
    line_number: int
    parameters: List[str] = field(default_factory=list)
    response_schema: Optional[str] = None
    deprecated: bool = False
    version: Optional[str] = None


@dataclass
class APIChange:
    """API change detection result"""
    change_type: str  # added, removed, modified, deprecated
    endpoint: APIEndpoint
    details: str
    severity: str  # breaking, non-breaking, warning
    affected_clients: List[str] = field(default_factory=list)


@dataclass
class APIChangeReport:
    """API change detection report"""
    total_endpoints: int
    changes: List[APIChange]
    breaking_changes: int
    non_breaking_changes: int
    warnings: int
    generated_at: datetime = field(default_factory=datetime.now)


class APIBreakingChangesDetector:
    """
    Automated API breaking changes detection system
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.api_paths = ["api/", "routes/", "endpoints/", "views/"]
        self.previous_api_snapshot = None
        self.current_api_snapshot = None
    
    def analyze_api_changes(self, compare_with_git: bool = True) -> APIChangeReport:
        """
        Analyze API changes by comparing current state with previous version
        """
        print("🔍 Analyzing API changes...")
        
        # Get current API snapshot
        self.current_api_snapshot = self._extract_api_snapshot()
        
        if compare_with_git:
            # Get previous API snapshot from git
            self.previous_api_snapshot = self._get_previous_api_snapshot()
        else:
            # Load from stored snapshot if available
            snapshot_file = self.project_root / ".api_snapshot.json"
            if snapshot_file.exists():
                with open(snapshot_file, 'r') as f:
                    self.previous_api_snapshot = json.load(f)
        
        # Compare snapshots and detect changes
        changes = []
        if self.previous_api_snapshot:
            changes = self._compare_api_snapshots()
        else:
            print("ℹ️ No previous API snapshot found - treating all endpoints as new")
        
        # Save current snapshot for future comparisons
        self._save_api_snapshot()
        
        # Generate report
        report = self._generate_change_report(changes)
        
        print(f"✅ API analysis complete. Found {len(changes)} changes ({report.breaking_changes} breaking)")
        
        return report
    
    def _extract_api_snapshot(self) -> Dict[str, APIEndpoint]:
        """Extract current API snapshot from codebase"""
        endpoints = {}
        
        # Find API files
        api_files = []
        for api_path in self.api_paths:
            path_obj = self.project_root / api_path
            if path_obj.exists():
                api_files.extend(path_obj.rglob("*.py"))
        
        # Also check for files with common API patterns
        for py_file in self.project_root.rglob("*.py"):
            if any(pattern in str(py_file) for pattern in ["route", "endpoint", "api", "view"]):
                api_files.append(py_file)
        
        # Remove duplicates
        api_files = list(set(api_files))
        
        # Extract endpoints from each file
        for api_file in api_files:
            file_endpoints = self._extract_endpoints_from_file(api_file)
            endpoints.update(file_endpoints)
        
        return endpoints
    
    def _extract_endpoints_from_file(self, file_path: Path) -> Dict[str, APIEndpoint]:
        """Extract API endpoints from a single file"""
        endpoints = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            # Look for decorators that define API endpoints
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    endpoint = self._extract_endpoint_from_function(node, file_path, content)
                    if endpoint:
                        key = f"{endpoint.method}:{endpoint.path}"
                        endpoints[key] = endpoint
                        
        except Exception as e:
            print(f"⚠️ Warning: Could not parse {file_path}: {e}")
        
        return endpoints
    
    def _extract_endpoint_from_function(self, func_node: ast.FunctionDef, file_path: Path, content: str) -> Optional[APIEndpoint]:
        """Extract endpoint information from function node"""
        # Look for API decorators
        api_decorators = []
        deprecated = False
        
        for decorator in func_node.decorator_list:
            decorator_info = self._analyze_decorator(decorator, content)
            if decorator_info:
                api_decorators.append(decorator_info)
            
            # Check for deprecation
            if isinstance(decorator, ast.Name) and decorator.id.lower() in ["deprecated", "deprecate"]:
                deprecated = True
        
        # If no API decorators found, not an endpoint
        if not api_decorators:
            return None
        
        # Extract parameters
        parameters = []
        for arg in func_node.args.args:
            if arg.arg not in ["self", "request", "cls"]:
                parameters.append(arg.arg)
        
        # Use the first API decorator found
        decorator_info = api_decorators[0]
        
        return APIEndpoint(
            path=decorator_info.get("path", "/unknown"),
            method=decorator_info.get("method", "GET"),
            function_name=func_node.name,
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=func_node.lineno,
            parameters=parameters,
            deprecated=deprecated
        )
    
    def _analyze_decorator(self, decorator, content: str) -> Optional[Dict[str, Any]]:
        """Analyze decorator to extract API information"""
        decorator_info = {}
        
        # Handle different decorator patterns
        if isinstance(decorator, ast.Call):
            # @app.route("/path", methods=["GET"])
            if isinstance(decorator.func, ast.Attribute):
                attr_name = decorator.func.attr
                if attr_name in ["route", "get", "post", "put", "delete", "patch", "head", "options"]:
                    # Extract path from first argument
                    if decorator.args:
                        path_node = decorator.args[0]
                        if isinstance(path_node, ast.Constant):
                            decorator_info["path"] = path_node.value
                        elif isinstance(path_node, ast.Str):  # Python < 3.8
                            decorator_info["path"] = path_node.s
                    
                    # Extract method
                    if attr_name == "route":
                        # Look for methods parameter
                        for keyword in decorator.keywords:
                            if keyword.arg == "methods":
                                if isinstance(keyword.value, ast.List):
                                    methods = []
                                    for elt in keyword.value.elts:
                                        if isinstance(elt, ast.Constant):
                                            methods.append(elt.value)
                                        elif isinstance(elt, ast.Str):
                                            methods.append(elt.s)
                                    if methods:
                                        decorator_info["method"] = methods[0]
                    else:
                        decorator_info["method"] = attr_name.upper()
            
            # @router.get("/path")
            elif isinstance(decorator.func, ast.Name):
                func_name = decorator.func.id
                if func_name in ["get", "post", "put", "delete", "patch", "head", "options"]:
                    decorator_info["method"] = func_name.upper()
                    if decorator.args:
                        path_node = decorator.args[0]
                        if isinstance(path_node, ast.Constant):
                            decorator_info["path"] = path_node.value
                        elif isinstance(path_node, ast.Str):
                            decorator_info["path"] = path_node.s
        
        elif isinstance(decorator, ast.Attribute):
            # @app.get (without parentheses)
            attr_name = decorator.attr
            if attr_name in ["get", "post", "put", "delete", "patch", "head", "options"]:
                decorator_info["method"] = attr_name.upper()
                decorator_info["path"] = "/unknown"
        
        return decorator_info if decorator_info else None
    
    def _get_previous_api_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get previous API snapshot from git"""
        try:
            # Get the previous commit
            result = subprocess.run(
                ["git", "rev-parse", "HEAD~1"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print("ℹ️ No previous commit found")
                return None
            
            prev_commit = result.stdout.strip()
            
            # Check if API snapshot exists in previous commit
            result = subprocess.run(
                ["git", "show", f"{prev_commit}:.api_snapshot.json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print("ℹ️ No previous API snapshot found in git")
                return None
                
        except Exception as e:
            print(f"⚠️ Warning: Could not get previous API snapshot from git: {e}")
            return None
    
    def _compare_api_snapshots(self) -> List[APIChange]:
        """Compare current and previous API snapshots"""
        changes = []
        
        if not self.previous_api_snapshot:
            return changes
        
        previous_endpoints = set(self.previous_api_snapshot.keys())
        current_endpoints = set(self.current_api_snapshot.keys())
        
        # Detect removed endpoints (breaking changes)
        removed_endpoints = previous_endpoints - current_endpoints
        for endpoint_key in removed_endpoints:
            prev_endpoint_data = self.previous_api_snapshot[endpoint_key]
            endpoint = APIEndpoint(**prev_endpoint_data)
            
            changes.append(APIChange(
                change_type="removed",
                endpoint=endpoint,
                details=f"Endpoint {endpoint.method} {endpoint.path} was removed",
                severity="breaking"
            ))
        
        # Detect new endpoints (non-breaking)
        added_endpoints = current_endpoints - previous_endpoints
        for endpoint_key in added_endpoints:
            endpoint = self.current_api_snapshot[endpoint_key]
            
            changes.append(APIChange(
                change_type="added",
                endpoint=endpoint,
                details=f"New endpoint {endpoint.method} {endpoint.path} was added",
                severity="non-breaking"
            ))
        
        # Detect modified endpoints
        common_endpoints = previous_endpoints & current_endpoints
        for endpoint_key in common_endpoints:
            prev_endpoint_data = self.previous_api_snapshot[endpoint_key]
            curr_endpoint = self.current_api_snapshot[endpoint_key]
            
            endpoint_changes = self._detect_endpoint_changes(prev_endpoint_data, curr_endpoint)
            changes.extend(endpoint_changes)
        
        return changes
    
    def _detect_endpoint_changes(self, prev_endpoint_data: Dict, curr_endpoint: APIEndpoint) -> List[APIChange]:
        """Detect changes in a specific endpoint"""
        changes = []
        
        prev_endpoint = APIEndpoint(**prev_endpoint_data)
        
        # Check parameter changes
        prev_params = set(prev_endpoint.parameters)
        curr_params = set(curr_endpoint.parameters)
        
        # Removed parameters (breaking change)
        removed_params = prev_params - curr_params
        if removed_params:
            changes.append(APIChange(
                change_type="modified",
                endpoint=curr_endpoint,
                details=f"Parameters removed: {', '.join(removed_params)}",
                severity="breaking"
            ))
        
        # Added parameters (potentially breaking if required)
        added_params = curr_params - prev_params
        if added_params:
            changes.append(APIChange(
                change_type="modified",
                endpoint=curr_endpoint,
                details=f"Parameters added: {', '.join(added_params)}",
                severity="warning"  # Could be breaking if parameters are required
            ))
        
        # Check deprecation status
        if not prev_endpoint.deprecated and curr_endpoint.deprecated:
            changes.append(APIChange(
                change_type="deprecated",
                endpoint=curr_endpoint,
                details=f"Endpoint {curr_endpoint.method} {curr_endpoint.path} was deprecated",
                severity="warning"
            ))
        
        # Check file changes
        if prev_endpoint.file_path != curr_endpoint.file_path:
            changes.append(APIChange(
                change_type="modified",
                endpoint=curr_endpoint,
                details=f"Endpoint moved from {prev_endpoint.file_path} to {curr_endpoint.file_path}",
                severity="non-breaking"
            ))
        
        return changes
    
    def _save_api_snapshot(self) -> None:
        """Save current API snapshot for future comparisons"""
        snapshot_file = self.project_root / ".api_snapshot.json"
        
        # Convert endpoints to serializable format
        serializable_snapshot = {}
        for key, endpoint in self.current_api_snapshot.items():
            serializable_snapshot[key] = {
                "path": endpoint.path,
                "method": endpoint.method,
                "function_name": endpoint.function_name,
                "file_path": endpoint.file_path,
                "line_number": endpoint.line_number,
                "parameters": endpoint.parameters,
                "response_schema": endpoint.response_schema,
                "deprecated": endpoint.deprecated,
                "version": endpoint.version
            }
        
        with open(snapshot_file, 'w') as f:
            json.dump(serializable_snapshot, f, indent=2)
        
        print(f"📊 API snapshot saved to {snapshot_file}")
    
    def _generate_change_report(self, changes: List[APIChange]) -> APIChangeReport:
        """Generate API change report"""
        breaking_changes = sum(1 for c in changes if c.severity == "breaking")
        non_breaking_changes = sum(1 for c in changes if c.severity == "non-breaking")
        warnings = sum(1 for c in changes if c.severity == "warning")
        
        return APIChangeReport(
            total_endpoints=len(self.current_api_snapshot),
            changes=changes,
            breaking_changes=breaking_changes,
            non_breaking_changes=non_breaking_changes,
            warnings=warnings
        )
    
    def print_report(self, report: APIChangeReport) -> None:
        """Print API change report"""
        print("\n" + "="*60)
        print("🔄 API BREAKING CHANGES REPORT")
        print("="*60)
        print(f"📅 Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Total Endpoints: {report.total_endpoints}")
        print(f"📊 Total Changes: {len(report.changes)}")
        print(f"🚨 Breaking Changes: {report.breaking_changes}")
        print(f"✅ Non-Breaking Changes: {report.non_breaking_changes}")
        print(f"⚠️ Warnings: {report.warnings}")
        print()
        
        if not report.changes:
            print("✅ No API changes detected")
            return
        
        # Group changes by severity
        breaking = [c for c in report.changes if c.severity == "breaking"]
        warnings = [c for c in report.changes if c.severity == "warning"]
        non_breaking = [c for c in report.changes if c.severity == "non-breaking"]
        
        # Show breaking changes first
        if breaking:
            print("🚨 BREAKING CHANGES:")
            print("-" * 40)
            for change in breaking:
                print(f"  ❌ {change.endpoint.method} {change.endpoint.path}")
                print(f"     {change.details}")
                print(f"     File: {change.endpoint.file_path}:{change.endpoint.line_number}")
                print()
        
        # Show warnings
        if warnings:
            print("⚠️ WARNINGS:")
            print("-" * 40)
            for change in warnings:
                print(f"  ⚠️ {change.endpoint.method} {change.endpoint.path}")
                print(f"     {change.details}")
                print(f"     File: {change.endpoint.file_path}:{change.endpoint.line_number}")
                print()
        
        # Show non-breaking changes
        if non_breaking:
            print("✅ NON-BREAKING CHANGES:")
            print("-" * 40)
            for change in non_breaking:
                print(f"  ✅ {change.endpoint.method} {change.endpoint.path}")
                print(f"     {change.details}")
                print(f"     File: {change.endpoint.file_path}:{change.endpoint.line_number}")
                print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if report.breaking_changes > 0:
            print("  🚨 Breaking changes detected! Consider:")
            print("     - Incrementing major version number")
            print("     - Providing migration guide for clients")
            print("     - Maintaining backward compatibility if possible")
        elif report.warnings > 0:
            print("  ⚠️ Potential breaking changes detected:")
            print("     - Review parameter additions for required vs optional")
            print("     - Ensure proper API documentation")
        else:
            print("  ✅ No breaking changes detected")
    
    def save_report_json(self, report: APIChangeReport, output_file: Path) -> None:
        """Save report to JSON file"""
        report_data = {
            "generated_at": report.generated_at.isoformat(),
            "summary": {
                "total_endpoints": report.total_endpoints,
                "total_changes": len(report.changes),
                "breaking_changes": report.breaking_changes,
                "non_breaking_changes": report.non_breaking_changes,
                "warnings": report.warnings
            },
            "changes": [
                {
                    "change_type": change.change_type,
                    "severity": change.severity,
                    "details": change.details,
                    "endpoint": {
                        "path": change.endpoint.path,
                        "method": change.endpoint.method,
                        "function_name": change.endpoint.function_name,
                        "file_path": change.endpoint.file_path,
                        "line_number": change.endpoint.line_number,
                        "parameters": change.endpoint.parameters,
                        "deprecated": change.endpoint.deprecated
                    }
                }
                for change in report.changes
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Report saved to {output_file}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="API Breaking Changes Detector for Ainflue Platform"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="api_changes_report.json",
        help="Output file for JSON report"
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Don't compare with git history"
    )
    parser.add_argument(
        "--format",
        choices=["summary", "detailed", "json"],
        default="summary",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = APIBreakingChangesDetector(project_root=args.project_root)
    
    # Analyze changes
    report = detector.analyze_api_changes(compare_with_git=not args.no_git)
    
    # Output results
    if args.format in ["summary", "detailed"]:
        detector.print_report(report)
    
    # Always save JSON report
    detector.save_report_json(report, args.output)
    
    # Return exit code based on breaking changes
    if report.breaking_changes > 0:
        print(f"\n❌ {report.breaking_changes} breaking changes detected")
        return 1
    elif report.warnings > 0:
        print(f"\n⚠️ {report.warnings} potential issues detected")
        return 0
    else:
        print("\n✅ No breaking changes detected")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)