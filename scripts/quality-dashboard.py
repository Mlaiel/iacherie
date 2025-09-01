#!/usr/bin/env python3
"""
Quality Metrics Dashboard Generator for Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Description: Generate comprehensive quality metrics dashboard
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import subprocess


@dataclass
class QualityMetric:
    """Quality metric data structure"""
    name: str
    value: float
    threshold: float
    unit: str
    status: str
    description: str


class QualityDashboard:
    """Comprehensive quality metrics dashboard generator"""
    
    def __init__(self, reports_dir: str = "quality-reports"):
        self.reports_dir = Path(reports_dir)
        self.metrics: List[QualityMetric] = []
        self.dashboard_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project": "Ainflue Platform",
            "version": "1.0.0",
            "metrics": {},
            "quality_gates": {},
            "recommendations": [],
            "alerts": []
        }
    
    def load_coverage_data(self) -> Dict[str, Any]:
        """Load code coverage data"""
        try:
            # Try to read coverage.xml
            coverage_file = self.reports_dir / "coverage.xml"
            if coverage_file.exists():
                # Parse coverage XML (simplified)
                coverage_data = {"coverage": 0.0, "lines_covered": 0, "lines_total": 0}
                
                # Get coverage percentage from pytest output
                result = subprocess.run(
                    ["coverage", "report", "--format=total"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    coverage_data["coverage"] = float(result.stdout.strip())
                
                return coverage_data
            
            return {"coverage": 0.0, "lines_covered": 0, "lines_total": 0}
            
        except Exception as e:
            print(f"Error loading coverage data: {e}")
            return {"coverage": 0.0, "lines_covered": 0, "lines_total": 0}
    
    def load_complexity_data(self) -> Dict[str, Any]:
        """Load code complexity data"""
        try:
            # Run radon for complexity analysis
            result = subprocess.run([
                "radon", "cc", ".", "--min=A", "--total-average", "--json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                complexity_data = json.loads(result.stdout)
                # Extract average complexity
                avg_complexity = 0.0
                total_functions = 0
                
                for file_data in complexity_data.values():
                    if isinstance(file_data, list):
                        for item in file_data:
                            if isinstance(item, dict) and 'complexity' in item:
                                avg_complexity += item['complexity']
                                total_functions += 1
                
                return {
                    "average_complexity": avg_complexity / total_functions if total_functions > 0 else 0.0,
                    "total_functions": total_functions,
                    "files_analyzed": len(complexity_data)
                }
            
            return {"average_complexity": 0.0, "total_functions": 0, "files_analyzed": 0}
            
        except Exception as e:
            print(f"Error loading complexity data: {e}")
            return {"average_complexity": 0.0, "total_functions": 0, "files_analyzed": 0}
    
    def load_security_data(self) -> Dict[str, Any]:
        """Load security analysis data"""
        security_data = {
            "vulnerabilities": 0,
            "security_score": 10.0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0
        }
        
        try:
            # Load bandit results
            bandit_file = list(self.reports_dir.glob("bandit-*.json"))
            if bandit_file:
                with open(bandit_file[0], 'r') as f:
                    bandit_data = json.load(f)
                    
                results = bandit_data.get('results', [])
                security_data["vulnerabilities"] = len(results)
                
                for result in results:
                    severity = result.get('issue_severity', 'LOW')
                    if severity == 'HIGH':
                        security_data["high_severity"] += 1
                    elif severity == 'MEDIUM':
                        security_data["medium_severity"] += 1
                    else:
                        security_data["low_severity"] += 1
                
                # Calculate security score
                score = 10.0
                score -= security_data["high_severity"] * 2.0
                score -= security_data["medium_severity"] * 1.0
                score -= security_data["low_severity"] * 0.5
                security_data["security_score"] = max(0.0, score)
            
            # Load safety results
            safety_file = list(self.reports_dir.glob("safety-*.json"))
            if safety_file:
                with open(safety_file[0], 'r') as f:
                    safety_data = json.load(f)
                    if isinstance(safety_data, list):
                        dependency_vulns = len(safety_data)
                        security_data["vulnerabilities"] += dependency_vulns
                        security_data["security_score"] -= dependency_vulns * 1.5
                        security_data["security_score"] = max(0.0, security_data["security_score"])
            
        except Exception as e:
            print(f"Error loading security data: {e}")
        
        return security_data
    
    def load_documentation_data(self) -> Dict[str, Any]:
        """Load documentation coverage data"""
        try:
            doc_file = list(self.reports_dir.glob("doc-coverage-*.json"))
            if doc_file:
                with open(doc_file[0], 'r') as f:
                    doc_data = json.load(f)
                    
                analysis = doc_data.get('analysis', {})
                summary = analysis.get('summary', {})
                
                return {
                    "coverage": summary.get('overall_coverage', 0.0),
                    "quality_score": summary.get('average_quality_score', 0.0),
                    "files_analyzed": summary.get('total_files', 0),
                    "items_documented": summary.get('documented_items', 0),
                    "total_items": summary.get('total_items', 0)
                }
            
            return {
                "coverage": 0.0,
                "quality_score": 0.0,
                "files_analyzed": 0,
                "items_documented": 0,
                "total_items": 0
            }
            
        except Exception as e:
            print(f"Error loading documentation data: {e}")
            return {
                "coverage": 0.0,
                "quality_score": 0.0,
                "files_analyzed": 0,
                "items_documented": 0,
                "total_items": 0
            }
    
    def load_performance_data(self) -> Dict[str, Any]:
        """Load performance benchmark data"""
        try:
            perf_file = list(self.reports_dir.glob("performance-*.json"))
            if perf_file:
                with open(perf_file[0], 'r') as f:
                    perf_data = json.load(f)
                    
                summary = perf_data.get('summary', {})
                
                return {
                    "total_metrics": summary.get('total_metrics', 0),
                    "degraded_metrics": summary.get('degraded_metrics', 0),
                    "improved_metrics": summary.get('improved_metrics', 0),
                    "stable_metrics": summary.get('stable_metrics', 0),
                    "performance_score": max(0, 100 - summary.get('degraded_metrics', 0) * 10)
                }
            
            return {
                "total_metrics": 0,
                "degraded_metrics": 0,
                "improved_metrics": 0,
                "stable_metrics": 0,
                "performance_score": 100
            }
            
        except Exception as e:
            print(f"Error loading performance data: {e}")
            return {
                "total_metrics": 0,
                "degraded_metrics": 0,
                "improved_metrics": 0,
                "stable_metrics": 0,
                "performance_score": 100
            }
    
    def load_license_data(self) -> Dict[str, Any]:
        """Load license compliance data"""
        try:
            license_file = list(self.reports_dir.glob("licenses-*.json"))
            if license_file:
                with open(license_file[0], 'r') as f:
                    license_data = json.load(f)
                    
                total_packages = len(license_data) if isinstance(license_data, list) else 0
                
                # Check for problematic licenses
                problematic_licenses = ['GPL', 'AGPL', 'LGPL', 'Copyleft']
                compliant_packages = 0
                
                if isinstance(license_data, list):
                    for package in license_data:
                        license_name = package.get('License', '')
                        if not any(prob in license_name for prob in problematic_licenses):
                            compliant_packages += 1
                
                compliance_percentage = (compliant_packages / total_packages * 100) if total_packages > 0 else 100.0
                
                return {
                    "total_packages": total_packages,
                    "compliant_packages": compliant_packages,
                    "compliance_percentage": compliance_percentage,
                    "non_compliant": total_packages - compliant_packages
                }
            
            return {
                "total_packages": 0,
                "compliant_packages": 0,
                "compliance_percentage": 100.0,
                "non_compliant": 0
            }
            
        except Exception as e:
            print(f"Error loading license data: {e}")
            return {
                "total_packages": 0,
                "compliant_packages": 0,
                "compliance_percentage": 100.0,
                "non_compliant": 0
            }
    
    def calculate_overall_quality_score(self) -> float:
        """Calculate overall quality score"""
        weights = {
            "code_coverage": 0.25,
            "security_score": 0.25,
            "documentation_coverage": 0.20,
            "performance_score": 0.15,
            "license_compliance": 0.10,
            "code_complexity": 0.05
        }
        
        scores = {}
        
        # Code coverage score
        coverage_data = self.dashboard_data["metrics"]["code_coverage"]
        scores["code_coverage"] = min(100, coverage_data["coverage"])
        
        # Security score (already 0-10, convert to 0-100)
        security_data = self.dashboard_data["metrics"]["security"]
        scores["security_score"] = security_data["security_score"] * 10
        
        # Documentation coverage score
        doc_data = self.dashboard_data["metrics"]["documentation"]
        scores["documentation_coverage"] = doc_data["coverage"]
        
        # Performance score
        perf_data = self.dashboard_data["metrics"]["performance"]
        scores["performance_score"] = perf_data["performance_score"]
        
        # License compliance score
        license_data = self.dashboard_data["metrics"]["license_compliance"]
        scores["license_compliance"] = license_data["compliance_percentage"]
        
        # Code complexity score (lower complexity is better)
        complexity_data = self.dashboard_data["metrics"]["code_complexity"]
        avg_complexity = complexity_data["average_complexity"]
        scores["code_complexity"] = max(0, 100 - (avg_complexity - 1) * 10)
        
        # Calculate weighted average
        overall_score = sum(scores[metric] * weights[metric] for metric in weights.keys())
        
        return round(overall_score, 1)
    
    def determine_quality_gates_status(self) -> Dict[str, bool]:
        """Determine quality gates status"""
        thresholds = {
            "code_coverage": 90.0,
            "security_score": 8.0,
            "documentation_coverage": 80.0,
            "performance_degradation": 0,
            "license_compliance": 95.0,
            "code_complexity": 10.0
        }
        
        status = {}
        
        # Code coverage gate
        coverage = self.dashboard_data["metrics"]["code_coverage"]["coverage"]
        status["code_coverage"] = coverage >= thresholds["code_coverage"]
        
        # Security gate
        security_score = self.dashboard_data["metrics"]["security"]["security_score"]
        status["security_score"] = security_score >= thresholds["security_score"]
        
        # Documentation gate
        doc_coverage = self.dashboard_data["metrics"]["documentation"]["coverage"]
        status["documentation_coverage"] = doc_coverage >= thresholds["documentation_coverage"]
        
        # Performance gate
        degraded_metrics = self.dashboard_data["metrics"]["performance"]["degraded_metrics"]
        status["performance_degradation"] = degraded_metrics <= thresholds["performance_degradation"]
        
        # License compliance gate
        license_compliance = self.dashboard_data["metrics"]["license_compliance"]["compliance_percentage"]
        status["license_compliance"] = license_compliance >= thresholds["license_compliance"]
        
        # Code complexity gate
        avg_complexity = self.dashboard_data["metrics"]["code_complexity"]["average_complexity"]
        status["code_complexity"] = avg_complexity <= thresholds["code_complexity"]
        
        return status
    
    def generate_recommendations(self) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        metrics = self.dashboard_data["metrics"]
        
        # Coverage recommendations
        if metrics["code_coverage"]["coverage"] < 90:
            recommendations.append(f"Increase code coverage from {metrics['code_coverage']['coverage']:.1f}% to 90%")
        
        # Security recommendations
        if metrics["security"]["security_score"] < 8.0:
            recommendations.append(f"Address security vulnerabilities (current score: {metrics['security']['security_score']:.1f}/10)")
        
        # Documentation recommendations
        if metrics["documentation"]["coverage"] < 80:
            recommendations.append(f"Improve documentation coverage from {metrics['documentation']['coverage']:.1f}% to 80%")
        
        # Performance recommendations
        if metrics["performance"]["degraded_metrics"] > 0:
            recommendations.append(f"Address {metrics['performance']['degraded_metrics']} degraded performance metrics")
        
        # License compliance recommendations
        if metrics["license_compliance"]["compliance_percentage"] < 95:
            recommendations.append(f"Review {metrics['license_compliance']['non_compliant']} packages with non-compliant licenses")
        
        # Complexity recommendations
        if metrics["code_complexity"]["average_complexity"] > 10:
            recommendations.append(f"Reduce code complexity (current average: {metrics['code_complexity']['average_complexity']:.1f})")
        
        return recommendations
    
    def generate_alerts(self) -> List[str]:
        """Generate quality alerts"""
        alerts = []
        metrics = self.dashboard_data["metrics"]
        
        # Critical alerts
        if metrics["security"]["high_severity"] > 0:
            alerts.append(f"🚨 CRITICAL: {metrics['security']['high_severity']} high-severity security issues")
        
        if metrics["code_coverage"]["coverage"] < 80:
            alerts.append(f"⚠️ WARNING: Code coverage critically low ({metrics['code_coverage']['coverage']:.1f}%)")
        
        if metrics["performance"]["degraded_metrics"] > 3:
            alerts.append(f"⚠️ WARNING: {metrics['performance']['degraded_metrics']} performance metrics degraded")
        
        if metrics["license_compliance"]["non_compliant"] > 5:
            alerts.append(f"⚠️ WARNING: {metrics['license_compliance']['non_compliant']} packages with non-compliant licenses")
        
        return alerts
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate complete quality metrics dashboard"""
        print("📊 Generating Quality Metrics Dashboard...")
        
        # Load all metrics data
        self.dashboard_data["metrics"] = {
            "code_coverage": self.load_coverage_data(),
            "code_complexity": self.load_complexity_data(),
            "security": self.load_security_data(),
            "documentation": self.load_documentation_data(),
            "performance": self.load_performance_data(),
            "license_compliance": self.load_license_data()
        }
        
        # Calculate overall score
        self.dashboard_data["overall_quality_score"] = self.calculate_overall_quality_score()
        
        # Determine quality gates status
        self.dashboard_data["quality_gates"] = self.determine_quality_gates_status()
        
        # Generate recommendations and alerts
        self.dashboard_data["recommendations"] = self.generate_recommendations()
        self.dashboard_data["alerts"] = self.generate_alerts()
        
        # Add summary
        self.dashboard_data["summary"] = {
            "quality_gates_passed": all(self.dashboard_data["quality_gates"].values()),
            "total_gates": len(self.dashboard_data["quality_gates"]),
            "passed_gates": sum(self.dashboard_data["quality_gates"].values()),
            "critical_alerts": len([alert for alert in self.dashboard_data["alerts"] if "CRITICAL" in alert]),
            "warnings": len([alert for alert in self.dashboard_data["alerts"] if "WARNING" in alert])
        }
        
        return self.dashboard_data
    
    def save_dashboard(self, output_file: str = "quality-dashboard.json"):
        """Save dashboard to file"""
        with open(output_file, 'w') as f:
            json.dump(self.dashboard_data, f, indent=2)
    
    def print_summary(self):
        """Print dashboard summary"""
        data = self.dashboard_data
        
        print("\n📊 Quality Metrics Dashboard")
        print("=" * 50)
        print(f"Overall Quality Score: {data['overall_quality_score']:.1f}/100")
        print(f"Quality Gates: {data['summary']['passed_gates']}/{data['summary']['total_gates']} passed")
        
        # Print individual metrics
        print(f"\n📈 Individual Metrics:")
        metrics = data["metrics"]
        print(f"  Code Coverage: {metrics['code_coverage']['coverage']:.1f}%")
        print(f"  Security Score: {metrics['security']['security_score']:.1f}/10")
        print(f"  Documentation: {metrics['documentation']['coverage']:.1f}%")
        print(f"  Performance: {metrics['performance']['performance_score']:.1f}/100")
        print(f"  License Compliance: {metrics['license_compliance']['compliance_percentage']:.1f}%")
        print(f"  Code Complexity: {metrics['code_complexity']['average_complexity']:.1f}")
        
        # Print quality gates status
        print(f"\n🚪 Quality Gates Status:")
        for gate, status in data["quality_gates"].items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {gate.replace('_', ' ').title()}")
        
        # Print alerts
        if data["alerts"]:
            print(f"\n🚨 Alerts:")
            for alert in data["alerts"]:
                print(f"  {alert}")
        
        # Print recommendations
        if data["recommendations"]:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(data["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        # Overall status
        if data["summary"]["quality_gates_passed"]:
            print(f"\n✅ Quality metrics validation PASSED")
        else:
            print(f"\n❌ Quality metrics validation FAILED")


def main():
    """Main dashboard generation"""
    dashboard = QualityDashboard()
    
    try:
        dashboard.generate_dashboard()
        dashboard.save_dashboard()
        dashboard.print_summary()
        
        # Exit with appropriate code
        if dashboard.dashboard_data["summary"]["quality_gates_passed"]:
            exit(0)
        else:
            exit(1)
            
    except Exception as e:
        print(f"❌ Dashboard generation failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()