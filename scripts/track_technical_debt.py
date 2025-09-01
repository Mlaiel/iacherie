#!/usr/bin/env python3
"""🔧 Technical Debt Tracker - Ainflue Platform
================================================================
Automated technical debt tracking and metrics calculation
================================================================
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse


@dataclass
class DebtItem:
    """Individual technical debt item"""
    file_path: str
    line_number: int
    debt_type: str
    description: str
    priority: str = "medium"
    estimated_hours: float = 0.5
    created_date: Optional[datetime] = None
    last_seen: Optional[datetime] = field(default_factory=datetime.now)


@dataclass
class DebtReport:
    """Technical debt report"""
    total_items: int
    total_estimated_hours: float
    debt_by_type: Dict[str, int]
    debt_by_priority: Dict[str, int]
    debt_by_file: Dict[str, int]
    items: List[DebtItem]
    generated_at: datetime = field(default_factory=datetime.now)


class TechnicalDebtTracker:
    """
    Automated technical debt tracking system
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.debt_indicators = {
            "TODO": {"priority": "medium", "hours": 0.5},
            "FIXME": {"priority": "high", "hours": 1.0},
            "HACK": {"priority": "high", "hours": 1.5},
            "XXX": {"priority": "critical", "hours": 2.0},
            "BUG": {"priority": "critical", "hours": 2.0},
            "DEPRECATED": {"priority": "medium", "hours": 0.5},
            "NOTE": {"priority": "low", "hours": 0.25},
            "OPTIMIZE": {"priority": "medium", "hours": 1.0},
            "REFACTOR": {"priority": "medium", "hours": 2.0},
            "SECURITY": {"priority": "critical", "hours": 3.0}
        }
        
        # File patterns to exclude
        self.exclude_patterns = [
            "*/tests/*",
            "*/test_*",
            "*/__pycache__/*",
            "*/node_modules/*",
            "*/venv/*",
            "*/env/*",
            "*/.git/*",
            "*/migrations/*",
            "*.pyc",
            "*.log",
            "*/logs/*"
        ]
    
    def scan_project(self) -> DebtReport:
        """
        Scan project for technical debt items
        """
        print("🔍 Scanning project for technical debt...")
        
        debt_items = []
        
        # Scan Python files
        python_files = self._get_python_files()
        for py_file in python_files:
            items = self._scan_file(py_file, ["py"])
            debt_items.extend(items)
        
        # Scan JavaScript/TypeScript files if present
        js_files = self._get_js_files()
        for js_file in js_files:
            items = self._scan_file(js_file, ["js", "ts"])
            debt_items.extend(items)
        
        # Scan YAML/Configuration files
        config_files = self._get_config_files()
        for config_file in config_files:
            items = self._scan_file(config_file, ["yml", "yaml", "json"])
            debt_items.extend(items)
        
        # Generate report
        report = self._generate_report(debt_items)
        
        print(f"✅ Scan complete. Found {report.total_items} debt items ({report.total_estimated_hours:.1f}h estimated)")
        
        return report
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files in the project"""
        python_files = []
        for pattern in ["**/*.py"]:
            files = self.project_root.rglob(pattern)
            python_files.extend([f for f in files if self._should_include_file(f)])
        return python_files
    
    def _get_js_files(self) -> List[Path]:
        """Get all JavaScript/TypeScript files in the project"""
        js_files = []
        for pattern in ["**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"]:
            files = self.project_root.rglob(pattern)
            js_files.extend([f for f in files if self._should_include_file(f)])
        return js_files
    
    def _get_config_files(self) -> List[Path]:
        """Get all configuration files in the project"""
        config_files = []
        for pattern in ["**/*.yml", "**/*.yaml", "**/*.json", "**/*.toml"]:
            files = self.project_root.rglob(pattern)
            config_files.extend([f for f in files if self._should_include_file(f)])
        return config_files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in scan"""
        file_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            # Simple pattern matching
            pattern_regex = pattern.replace("*", ".*")
            if re.search(pattern_regex, file_str):
                return False
        
        return True
    
    def _scan_file(self, file_path: Path, file_types: List[str]) -> List[DebtItem]:
        """Scan individual file for debt items"""
        debt_items = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    items = self._extract_debt_from_line(
                        line, 
                        str(file_path.relative_to(self.project_root)), 
                        line_num
                    )
                    debt_items.extend(items)
                    
        except Exception as e:
            print(f"⚠️ Warning: Could not scan {file_path}: {e}")
        
        return debt_items
    
    def _extract_debt_from_line(self, line: str, file_path: str, line_number: int) -> List[DebtItem]:
        """Extract debt items from a single line"""
        debt_items = []
        line_upper = line.upper()
        
        for indicator, config in self.debt_indicators.items():
            # Look for indicator in comments
            patterns = [
                f"#{indicator}",  # Python style
                f"//{indicator}",  # JavaScript style
                f"<!--{indicator}",  # HTML style
                f"/*{indicator}",  # CSS/multi-line comment
                f"#{indicator}:",  # With colon
                f"//{indicator}:",  # With colon
            ]
            
            for pattern in patterns:
                if pattern in line_upper:
                    # Extract description
                    description = self._extract_description(line, indicator)
                    
                    debt_item = DebtItem(
                        file_path=file_path,
                        line_number=line_number,
                        debt_type=indicator.lower(),
                        description=description,
                        priority=config["priority"],
                        estimated_hours=config["hours"]
                    )
                    
                    debt_items.append(debt_item)
                    break  # Only one debt item per line
        
        return debt_items
    
    def _extract_description(self, line: str, indicator: str) -> str:
        """Extract description from debt comment"""
        # Remove common comment prefixes and the indicator
        line_clean = line.strip()
        
        # Remove prefixes
        prefixes = ["#", "//", "<!--", "/*", "*"]
        for prefix in prefixes:
            if line_clean.startswith(prefix):
                line_clean = line_clean[len(prefix):].strip()
        
        # Remove indicator and colon
        indicator_pattern = f"{indicator}:?"
        line_clean = re.sub(indicator_pattern, "", line_clean, flags=re.IGNORECASE).strip()
        
        # Remove suffixes
        suffixes = ["-->", "*/"]
        for suffix in suffixes:
            if line_clean.endswith(suffix):
                line_clean = line_clean[:-len(suffix)].strip()
        
        return line_clean or f"{indicator} item found"
    
    def _generate_report(self, debt_items: List[DebtItem]) -> DebtReport:
        """Generate comprehensive debt report"""
        total_items = len(debt_items)
        total_hours = sum(item.estimated_hours for item in debt_items)
        
        # Group by type
        debt_by_type = {}
        for item in debt_items:
            debt_by_type[item.debt_type] = debt_by_type.get(item.debt_type, 0) + 1
        
        # Group by priority
        debt_by_priority = {}
        for item in debt_items:
            debt_by_priority[item.priority] = debt_by_priority.get(item.priority, 0) + 1
        
        # Group by file
        debt_by_file = {}
        for item in debt_items:
            debt_by_file[item.file_path] = debt_by_file.get(item.file_path, 0) + 1
        
        return DebtReport(
            total_items=total_items,
            total_estimated_hours=total_hours,
            debt_by_type=debt_by_type,
            debt_by_priority=debt_by_priority,
            debt_by_file=debt_by_file,
            items=debt_items
        )
    
    def save_report(self, report: DebtReport, output_file: Path) -> None:
        """Save report to JSON file"""
        report_data = {
            "generated_at": report.generated_at.isoformat(),
            "summary": {
                "total_items": report.total_items,
                "total_estimated_hours": report.total_estimated_hours,
                "debt_by_type": report.debt_by_type,
                "debt_by_priority": report.debt_by_priority,
                "debt_by_file": dict(sorted(report.debt_by_file.items(), key=lambda x: x[1], reverse=True)[:10])  # Top 10 files
            },
            "items": [
                {
                    "file_path": item.file_path,
                    "line_number": item.line_number,
                    "debt_type": item.debt_type,
                    "description": item.description,
                    "priority": item.priority,
                    "estimated_hours": item.estimated_hours,
                    "last_seen": item.last_seen.isoformat()
                }
                for item in report.items
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Report saved to {output_file}")
    
    def print_summary(self, report: DebtReport) -> None:
        """Print debt report summary"""
        print("\n" + "="*60)
        print("🔧 TECHNICAL DEBT SUMMARY")
        print("="*60)
        print(f"📅 Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total Items: {report.total_items}")
        print(f"⏱️  Estimated Hours: {report.total_estimated_hours:.1f}h")
        print()
        
        # Debt by type
        if report.debt_by_type:
            print("📋 BY TYPE:")
            for debt_type, count in sorted(report.debt_by_type.items(), key=lambda x: x[1], reverse=True):
                hours = count * self.debt_indicators.get(debt_type.upper(), {}).get("hours", 0.5)
                print(f"  {debt_type.upper()}: {count} items ({hours:.1f}h)")
            print()
        
        # Debt by priority
        if report.debt_by_priority:
            print("🎯 BY PRIORITY:")
            priority_order = ["critical", "high", "medium", "low"]
            for priority in priority_order:
                count = report.debt_by_priority.get(priority, 0)
                if count > 0:
                    emoji = {"critical": "🚨", "high": "⚠️", "medium": "📝", "low": "💡"}.get(priority, "📝")
                    print(f"  {emoji} {priority.title()}: {count} items")
            print()
        
        # Top files with debt
        if report.debt_by_file:
            print("📁 TOP FILES WITH DEBT:")
            top_files = sorted(report.debt_by_file.items(), key=lambda x: x[1], reverse=True)[:5]
            for file_path, count in top_files:
                print(f"  {file_path}: {count} items")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if report.total_estimated_hours > 40:
            print("  🚨 High technical debt detected! Consider dedicating a sprint to debt reduction")
        elif report.total_estimated_hours > 20:
            print("  ⚠️ Moderate technical debt. Plan regular debt reduction activities")
        else:
            print("  ✅ Technical debt is within acceptable limits")
        
        critical_count = report.debt_by_priority.get("critical", 0)
        if critical_count > 0:
            print(f"  🚨 Address {critical_count} critical items immediately")
        
        high_count = report.debt_by_priority.get("high", 0)
        if high_count > 5:
            print(f"  ⚠️ Consider prioritizing {high_count} high-priority items")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Technical Debt Tracker for Ainflue Platform"
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
        default="technical_debt_report.json",
        help="Output file for JSON report"
    )
    parser.add_argument(
        "--format",
        choices=["summary", "detailed", "json"],
        default="summary",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Initialize tracker
    tracker = TechnicalDebtTracker(project_root=args.project_root)
    
    # Scan project
    report = tracker.scan_project()
    
    # Output results
    if args.format == "summary":
        tracker.print_summary(report)
    elif args.format == "detailed":
        tracker.print_summary(report)
        print("\n📝 DETAILED ITEMS:")
        print("-" * 60)
        for item in report.items:
            priority_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📝", "low": "💡"}.get(item.priority, "📝")
            print(f"{priority_emoji} {item.file_path}:{item.line_number}")
            print(f"   Type: {item.debt_type.upper()}")
            print(f"   Description: {item.description}")
            print(f"   Estimated: {item.estimated_hours}h")
            print()
    elif args.format == "json":
        tracker.save_report(report, args.output)
        return
    
    # Always save JSON report
    tracker.save_report(report, args.output)
    
    # Return exit code based on debt level
    if report.total_estimated_hours > 40:
        print("\n❌ Critical technical debt level detected")
        return 1
    elif report.total_estimated_hours > 20:
        print("\n⚠️ High technical debt level detected")
        return 0
    else:
        print("\n✅ Technical debt is within acceptable limits")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)