#!/usr/bin/env python3
"""
🎯 VALIDATION CRITERIA RUNNER

Simple script to execute the complete validation criteria system
and generate all reports and dashboards.

Usage:
    python run_validation_criteria.py [--output-dir OUTPUT_DIR]

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add validation scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "validation"))

from final_validation_criteria import FinalValidationCriteria
from validation_dashboard import ValidationDashboard


async def run_complete_validation(output_dir: str = ".") -> None:
    """
    Run complete validation criteria assessment and generate all outputs.
    
    Args:
        output_dir: Directory to save outputs
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("🎯 STARTING COMPLETE VALIDATION CRITERIA ASSESSMENT")
    print("=" * 60)
    
    # 1. Initialize and run validation
    print("📋 Running validation criteria assessment...")
    validator = FinalValidationCriteria()
    report = await validator.validate_all_criteria()
    
    # 2. Generate JSON report
    json_path = output_path / "validation_criteria_report.json"
    validator.save_report(report, str(json_path))
    print(f"✅ JSON report saved: {json_path}")
    
    # 3. Generate HTML dashboard
    print("🌐 Generating HTML dashboard...")
    dashboard = ValidationDashboard()
    html_path = await dashboard.generate_dashboard()
    html_dest = output_path / "validation_criteria_dashboard.html"
    Path(html_path).rename(html_dest)
    print(f"✅ HTML dashboard saved: {html_dest}")
    
    # 4. Generate markdown report
    print("📝 Generating markdown report...")
    markdown = dashboard.generate_markdown_report(report)
    md_path = output_path / "VALIDATION_CRITERIA_STATUS.md"
    with open(md_path, 'w') as f:
        f.write(markdown)
    print(f"✅ Markdown report saved: {md_path}")
    
    # 5. Print summary
    print("\n" + "=" * 60)
    print("🏆 VALIDATION COMPLETE")
    print("=" * 60)
    print(f"📊 Overall Score: {report.overall_score:.1f}%")
    print(f"✅ Passed: {report.passed}")
    print(f"🔄 In Progress: {report.in_progress}")
    print(f"⚠️ Warnings: {report.warnings}")
    print(f"❌ Failed: {report.failed}")
    print(f"🚫 Not Implemented: {report.not_implemented}")
    
    print(f"\n📁 All reports saved to: {output_path.absolute()}")
    print(f"🌐 Open dashboard: file://{html_dest.absolute()}")
    
    # 6. Category breakdown
    print("\n📈 CATEGORY BREAKDOWN:")
    print("-" * 40)
    for category, stats in report.summary.items():
        print(f"{category.upper():15} {stats['passed']:2}/{stats['total']:2} ({stats['score']:5.1f}%)")
    
    return report


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run complete validation criteria assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_validation_criteria.py
    python run_validation_criteria.py --output-dir ./validation_reports
    
This script will generate:
    - validation_criteria_report.json (detailed JSON report)
    - validation_criteria_dashboard.html (interactive web dashboard)
    - VALIDATION_CRITERIA_STATUS.md (markdown summary)
        """
    )
    
    parser.add_argument(
        "--output-dir", 
        default=".",
        help="Output directory for generated reports (default: current directory)"
    )
    
    args = parser.parse_args()
    
    try:
        # Run validation
        report = asyncio.run(run_complete_validation(args.output_dir))
        
        # Exit code based on results
        if report.failed > 0:
            print(f"\n⚠️ Validation completed with {report.failed} failures")
            sys.exit(1)
        elif report.overall_score < 50.0:
            print(f"\n⚠️ Validation score below 50%: {report.overall_score:.1f}%")
            sys.exit(1)
        else:
            print(f"\n✅ Validation completed successfully: {report.overall_score:.1f}%")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()