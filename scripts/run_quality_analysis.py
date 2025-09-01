#!/usr/bin/env python3
"""🎯 Quality Metrics CLI - Ainflue Platform
================================================================
Run comprehensive quality analysis from command line
================================================================
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kubernetes.ci_cd.quality_metrics_manager import QualityMetricsManager


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive quality metrics analysis for Ainflue platform"
    )
    parser.add_argument(
        "--project-root", 
        type=Path, 
        default=project_root,
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--output", 
        type=Path,
        help="Output file for HTML report"
    )
    parser.add_argument(
        "--json", 
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--fail-on-warning", 
        action="store_true",
        help="Fail if any metrics have warnings"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize quality metrics manager
    print("🔍 Initializing Quality Metrics Manager...")
    manager = QualityMetricsManager(project_root=args.project_root)
    
    if not await manager.initialize():
        print("❌ Failed to initialize Quality Metrics Manager")
        return 1
    
    # Run comprehensive analysis
    print("📊 Running comprehensive quality analysis...")
    try:
        report = await manager.run_comprehensive_quality_analysis()
        
        # Display results
        print("\n" + "="*60)
        print(f"🎯 QUALITY METRICS REPORT - {report.project_name}")
        print("="*60)
        print(f"📅 Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏆 Overall Score: {report.overall_score:.1f}%")
        print(f"📈 Overall Status: {report.overall_status.value.upper()}")
        print()
        
        # Show individual metrics
        print("📋 INDIVIDUAL METRICS:")
        print("-" * 40)
        for metric_type, metric in report.metrics.items():
            status_emoji = {
                "passed": "✅",
                "warning": "⚠️",
                "failed": "❌"
            }.get(metric.status.value, "❓")
            
            print(f"{status_emoji} {metric_type.value.replace('_', ' ').title()}: {metric.value:.1f}%")
            if args.verbose:
                print(f"   {metric.message}")
                if metric.details:
                    for key, value in metric.details.items():
                        if isinstance(value, (int, float, str)):
                            print(f"   {key}: {value}")
                print()
        
        # Show recommendations
        if report.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            print("-" * 40)
            for i, recommendation in enumerate(report.recommendations, 1):
                print(f"{i}. {recommendation}")
        
        # Show baseline comparison
        if report.baseline_comparison:
            print("\n📈 BASELINE COMPARISON:")
            print("-" * 40)
            for metric_name, comparison in report.baseline_comparison.items():
                change = comparison.get("change", 0)
                change_pct = comparison.get("change_percentage", 0)
                
                if comparison.get("new_baseline"):
                    print(f"🆕 {metric_name}: {comparison['current']:.1f}% (new baseline)")
                elif change > 0:
                    print(f"📈 {metric_name}: +{change:.1f}% (+{change_pct:.1f}%)")
                elif change < 0:
                    print(f"📉 {metric_name}: {change:.1f}% ({change_pct:.1f}%)")
                else:
                    print(f"➡️ {metric_name}: No change ({comparison['current']:.1f}%)")
        
        # Output JSON if requested
        if args.json:
            import json
            result = {
                "project_name": report.project_name,
                "timestamp": report.timestamp.isoformat(),
                "overall_score": report.overall_score,
                "overall_status": report.overall_status.value,
                "metrics": {
                    k.value: {
                        "value": v.value,
                        "status": v.status.value,
                        "message": v.message,
                        "details": v.details
                    } for k, v in report.metrics.items()
                },
                "recommendations": report.recommendations,
                "baseline_comparison": report.baseline_comparison
            }
            print("\n📄 JSON OUTPUT:")
            print(json.dumps(result, indent=2))
        
        # Generate HTML report if requested
        if args.output:
            html_report = await manager.generate_quality_report_html(report)
            with open(args.output, 'w') as f:
                f.write(html_report)
            print(f"\n📊 HTML report saved to: {args.output}")
        
        # Determine exit code
        if report.overall_status.value == "failed":
            print(f"\n❌ Quality analysis FAILED (score: {report.overall_score:.1f}%)")
            return 1
        elif report.overall_status.value == "warning" and args.fail_on_warning:
            print(f"\n⚠️  Quality analysis has WARNINGS (score: {report.overall_score:.1f}%)")
            return 1
        else:
            print(f"\n✅ Quality analysis PASSED (score: {report.overall_score:.1f}%)")
            return 0
            
    except Exception as e:
        print(f"❌ Quality analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)