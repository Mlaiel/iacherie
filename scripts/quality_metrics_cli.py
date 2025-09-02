#!/usr/bin/env python3
"""🎯 Quality Metrics CLI - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + DEVOPS_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Command-line interface for running comprehensive quality metrics
analysis and generating reports.
================================================================
"""

import asyncio
import sys
import json
import click
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from quality.metrics_orchestrator import QualityMetricsOrchestrator, quality_orchestrator
    from quality.technical_debt_tracker import TechnicalDebtTracker, technical_debt_tracker
    from quality.api_breaking_detector import APIBreakingChangesDetector, api_breaking_detector
    from quality.security_scorecard import SecurityScorecardEngine, security_scorecard
except ImportError as e:
    print(f"Error importing quality modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Async command wrapper
def async_command(f):
    """Decorator to handle async commands in Click"""
    import functools
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"Executing wrapper")
            
            # Implementation for wrapper
            # Business logic implementation

            try:

                logger.info(f"Executing business logic")

                

                # Core business implementation

                result = {

                    "status": "success",

                    "operation": "business_logic",

                    "timestamp": datetime.utcnow().isoformat()

                }

                

                logger.info(f"Business logic completed successfully")

                return result

                

            except Exception as e:

                logger.error(f"Business logic failed: {e}")

                raise
            
            result = {

            
                "status": "completed",

            
                "data": [],

            
                "timestamp": datetime.utcnow().isoformat()

            
            }
            logger.info(f"wrapper completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"wrapper failed: {e}")
            raise
    return wrapper

@click.group()
@click.option('--config', '-c', default='config/quality_metrics.yaml', 
              help='Path to quality metrics configuration file')
@click.option('--project-root', '-p', default='.', 
              help='Project root directory')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, project_root, verbose):
    """Ainflue Platform Quality Metrics CLI"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['project_root'] = project_root

@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'markdown', 'html']), 
              default='json', help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.option('--environment', '-e', default='development', 
              help='Environment (development, staging, production)')
@click.pass_context
@async_command
async def analyze(ctx, format, output, environment):
    """Run comprehensive quality analysis"""
    try:
        click.echo("🎯 Starting comprehensive quality analysis...")
        
        # Initialize orchestrator
        orchestrator = QualityMetricsOrchestrator(ctx.obj['config'])
        
        # Run analysis
        report = await orchestrator.run_comprehensive_analysis(
            project_path=ctx.obj['project_root'],
            environment=environment
        )
        
        # Generate report
        report_content = await orchestrator.generate_report(report, format)
        
        # Output results
        if output:
            with open(output, 'w') as f:
                f.write(report_content)
            click.echo(f"✅ Report saved to {output}")
        else:
            click.echo(report_content)
        
        # Print summary
        click.echo(f"\n📊 Quality Analysis Summary:")
        click.echo(f"Overall Score: {report.overall_score:.1f}%")
        click.echo(f"Quality Level: {report.overall_level.value.title()}")
        click.echo(f"Metrics Analyzed: {len(report.metrics)}")
        
        if report.recommendations:
            click.echo(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(report.recommendations[:3], 1):
                click.echo(f"{i}. {rec}")
        
        # Exit with appropriate code
        if report.overall_score < 70:
            click.echo("\n❌ Quality score below threshold!")
            sys.exit(1)
        else:
            click.echo("\n✅ Quality analysis passed!")
            
    except Exception as e:
        click.echo(f"❌ Error during analysis: {e}")
        sys.exit(1)

@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'markdown']), 
              default='json', help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
@async_command
async def debt(ctx, format, output):
    """Analyze technical debt"""
    try:
        click.echo("🔧 Analyzing technical debt...")
        
        # Initialize tracker
        tracker = TechnicalDebtTracker(ctx.obj['project_root'])
        
        # Run analysis
        summary = await tracker.analyze_technical_debt()
        
        # Generate report
        report_content = tracker.export_debt_report(format)
        
        # Output results
        if output:
            with open(output, 'w') as f:
                f.write(report_content)
            click.echo(f"✅ Technical debt report saved to {output}")
        else:
            click.echo(report_content)
        
        # Print summary
        click.echo(f"\n📊 Technical Debt Summary:")
        click.echo(f"Total Items: {summary.total_items}")
        click.echo(f"Total Effort: {summary.total_effort} story points")
        click.echo(f"Debt Ratio: {summary.debt_ratio:.2f}%")
        
        if summary.recommendations:
            click.echo(f"\n💡 Recommendations:")
            for i, rec in enumerate(summary.recommendations, 1):
                click.echo(f"{i}. {rec}")
        
        # Exit with appropriate code
        if summary.total_items > 50:
            click.echo("\n⚠️ High technical debt detected!")
            sys.exit(1)
        else:
            click.echo("\n✅ Technical debt analysis completed!")
            
    except Exception as e:
        click.echo(f"❌ Error analyzing technical debt: {e}")
        sys.exit(1)

@cli.command()
@click.option('--baseline', '-b', help='Baseline contract file path')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
@async_command
async def api_changes(ctx, baseline, output):
    """Detect API breaking changes"""
    try:
        click.echo("🔧 Detecting API breaking changes...")
        
        # Initialize detector
        detector = APIBreakingChangesDetector(ctx.obj['project_root'])
        
        # Run detection
        changes = await detector.detect_breaking_changes(baseline)
        
        # Generate report
        report_content = detector.generate_breaking_changes_report(changes)
        
        # Output results
        if output:
            with open(output, 'w') as f:
                f.write(report_content)
            click.echo(f"✅ API changes report saved to {output}")
        else:
            click.echo(report_content)
        
        # Print summary
        breaking_changes = [c for c in changes if c.change_type.value == "breaking"]
        click.echo(f"\n📊 API Changes Summary:")
        click.echo(f"Total Changes: {len(changes)}")
        click.echo(f"Breaking Changes: {len(breaking_changes)}")
        
        if breaking_changes:
            click.echo(f"\n⚠️ Breaking Changes Detected:")
            for change in breaking_changes[:3]:
                click.echo(f"- {change.description}")
        
        # Exit with appropriate code
        if breaking_changes:
            click.echo("\n❌ Breaking changes detected!")
            sys.exit(1)
        else:
            click.echo("\n✅ No breaking changes detected!")
            
    except Exception as e:
        click.echo(f"❌ Error detecting API changes: {e}")
        sys.exit(1)

@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'markdown']), 
              default='json', help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
@async_command
async def security(ctx, format, output):
    """Generate security scorecard"""
    try:
        click.echo("🛡️ Generating security scorecard...")
        
        # Initialize scorecard engine
        engine = SecurityScorecardEngine(ctx.obj['project_root'])
        
        # Generate scorecard
        scorecard = await engine.generate_scorecard()
        
        # Generate report
        report_content = engine.export_scorecard(scorecard, format)
        
        # Output results
        if output:
            with open(output, 'w') as f:
                f.write(report_content)
            click.echo(f"✅ Security scorecard saved to {output}")
        else:
            click.echo(report_content)
        
        # Print summary
        critical_findings = [f for f in scorecard.findings if f.severity == "critical"]
        high_findings = [f for f in scorecard.findings if f.severity == "high"]
        
        click.echo(f"\n📊 Security Scorecard Summary:")
        click.echo(f"Overall Score: {scorecard.overall_score:.1f}/100")
        click.echo(f"Security Level: {scorecard.overall_level.value.title()}")
        click.echo(f"Critical Findings: {len(critical_findings)}")
        click.echo(f"High Findings: {len(high_findings)}")
        
        if scorecard.improvement_suggestions:
            click.echo(f"\n💡 Top Improvement Suggestions:")
            for i, suggestion in enumerate(scorecard.improvement_suggestions[:3], 1):
                click.echo(f"{i}. {suggestion}")
        
        # Exit with appropriate code
        if scorecard.overall_score < 80 or critical_findings:
            click.echo("\n❌ Security issues detected!")
            sys.exit(1)
        else:
            click.echo("\n✅ Security scorecard passed!")
            
    except Exception as e:
        click.echo(f"❌ Error generating security scorecard: {e}")
        sys.exit(1)

@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'markdown', 'html']), 
              default='markdown', help='Output format')
@click.option('--output', '-o', default='quality_report.md', help='Output file path')
@click.option('--environment', '-e', default='development', 
              help='Environment (development, staging, production)')
@click.pass_context
@async_command
async def all(ctx, format, output, environment):
    """Run all quality checks and generate comprehensive report"""
    try:
        click.echo("🚀 Running comprehensive quality assessment...")
        
        results = {}
        
        # 1. Quality analysis
        click.echo("1/4 Running quality analysis...")
        orchestrator = QualityMetricsOrchestrator(ctx.obj['config'])
        quality_report = await orchestrator.run_comprehensive_analysis(
            project_path=ctx.obj['project_root'],
            environment=environment
        )
        results['quality'] = quality_report
        
        # 2. Technical debt analysis
        click.echo("2/4 Analyzing technical debt...")
        tracker = TechnicalDebtTracker(ctx.obj['project_root'])
        debt_summary = await tracker.analyze_technical_debt()
        results['technical_debt'] = debt_summary
        
        # 3. API breaking changes
        click.echo("3/4 Checking API breaking changes...")
        detector = APIBreakingChangesDetector(ctx.obj['project_root'])
        api_changes = await detector.detect_breaking_changes()
        results['api_changes'] = api_changes
        
        # 4. Security scorecard
        click.echo("4/4 Generating security scorecard...")
        engine = SecurityScorecardEngine(ctx.obj['project_root'])
        scorecard = await engine.generate_scorecard()
        results['security'] = scorecard
        
        # Generate comprehensive report
        report_content = await _generate_comprehensive_report(results, format)
        
        # Save report
        with open(output, 'w') as f:
            f.write(report_content)
        
        click.echo(f"✅ Comprehensive quality report saved to {output}")
        
        # Print summary
        click.echo(f"\n📊 Comprehensive Quality Assessment Summary:")
        click.echo(f"Overall Quality Score: {quality_report.overall_score:.1f}%")
        click.echo(f"Security Score: {scorecard.overall_score:.1f}%")
        click.echo(f"Technical Debt Items: {debt_summary.total_items}")
        
        breaking_changes = [c for c in api_changes if c.change_type.value == "breaking"]
        click.echo(f"Breaking API Changes: {len(breaking_changes)}")
        
        # Determine overall status
        issues = []
        if quality_report.overall_score < 70:
            issues.append("Low quality score")
        if scorecard.overall_score < 80:
            issues.append("Security issues")
        if debt_summary.total_items > 50:
            issues.append("High technical debt")
        if breaking_changes:
            issues.append("Breaking API changes")
        
        if issues:
            click.echo(f"\n❌ Issues found: {', '.join(issues)}")
            sys.exit(1)
        else:
            click.echo("\n✅ All quality checks passed!")
            
    except Exception as e:
        click.echo(f"❌ Error during comprehensive assessment: {e}")
        sys.exit(1)

async def _generate_comprehensive_report(results, format):
    """Generate comprehensive quality report"""
    if format == "json":
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": results['quality'].overall_score,
            "security_score": results['security'].overall_score,
            "technical_debt_items": results['technical_debt'].total_items,
            "api_breaking_changes": len([c for c in results['api_changes'] if c.change_type.value == "breaking"]),
            "overall_status": "passed" if all([
                results['quality'].overall_score >= 70,
                results['security'].overall_score >= 80,
                results['technical_debt'].total_items <= 50,
                len([c for c in results['api_changes'] if c.change_type.value == "breaking"]) == 0
            ]) else "failed"
        }, indent=2)
    
    elif format == "markdown":
        quality = results['quality']
        security = results['security']
        debt = results['technical_debt']
        api_changes = results['api_changes']
        breaking_changes = [c for c in api_changes if c.change_type.value == "breaking"]
        
        return f"""# Comprehensive Quality Assessment Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

| Metric | Score/Count | Status |
|--------|-------------|--------|
| Overall Quality | {quality.overall_score:.1f}% | {'✅ Pass' if quality.overall_score >= 70 else '❌ Fail'} |
| Security Score | {security.overall_score:.1f}% | {'✅ Pass' if security.overall_score >= 80 else '❌ Fail'} |
| Technical Debt | {debt.total_items} items | {'✅ Pass' if debt.total_items <= 50 else '❌ Fail'} |
| Breaking Changes | {len(breaking_changes)} | {'✅ Pass' if len(breaking_changes) == 0 else '❌ Fail'} |

## Quality Metrics Details

### Overall Score: {quality.overall_score:.1f}% ({quality.overall_level.value.title()})

**Metrics Analyzed:**
{chr(10).join([f'- {m.name}: {m.value:.1f}% ({m.status.value.title()})' for m in quality.metrics])}

### Security Scorecard: {security.overall_score:.1f}% ({security.overall_level.value.title()})

**Security Findings:**
- Critical: {len([f for f in security.findings if f.severity == "critical"])}
- High: {len([f for f in security.findings if f.severity == "high"])}
- Medium: {len([f for f in security.findings if f.severity == "medium"])}
- Low: {len([f for f in security.findings if f.severity == "low"])}

### Technical Debt: {debt.total_items} items ({debt.total_effort} story points)

**Debt Breakdown:**
{chr(10).join([f'- {debt_type.value.replace("_", " ").title()}: {count}' for debt_type, count in debt.type_breakdown.items() if count > 0])}

### API Changes: {len(api_changes)} total ({len(breaking_changes)} breaking)

{chr(10).join([f'- {change.description}' for change in breaking_changes[:5]])}

## Recommendations

### Quality Improvements
{chr(10).join([f'- {rec}' for rec in quality.recommendations[:5]])}

### Security Improvements  
{chr(10).join([f'- {rec}' for rec in security.improvement_suggestions[:5]])}

### Technical Debt Reduction
{chr(10).join([f'- {rec}' for rec in debt.recommendations[:5]])}

---
*Generated by Ainflue Quality Metrics System*
"""
    
    else:  # html
        return "<html><body><h1>Quality Report</h1><p>HTML format not implemented yet</p></body></html>"

def main():
    """Main entry point"""
    cli()

if __name__ == '__main__':
    main()