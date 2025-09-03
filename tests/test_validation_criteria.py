#!/usr/bin/env python3
"""
Test suite for the Final Validation Criteria system.

This test validates that the validation criteria system correctly
implements and reports on all specified requirements.
"""

import pytest
import asyncio
import json
from pathlib import Path
import sys
import os

# Add the scripts directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts', 'validation'))

from final_validation_criteria import (
    FinalValidationCriteria, 
    ValidationReport, 
    ValidationStatus, 
    ValidationCategory,
    ValidationCriterion
)
from validation_dashboard import ValidationDashboard


class TestValidationCriteria:
    """Test the validation criteria system."""
    
    def test_criteria_initialization(self):
        """Test that all required criteria are initialized."""
        validator = FinalValidationCriteria()
        
        # Verify total criteria count (20 total as per problem statement)
        assert len(validator.criteria) == 20
        
        # Verify all categories are represented
        categories = set(c.category for c in validator.criteria)
        expected_categories = {
            ValidationCategory.PERFORMANCE,
            ValidationCategory.SECURITY,
            ValidationCategory.SCALABILITY,
            ValidationCategory.QUALITY
        }
        assert categories == expected_categories
        
        # Verify each category has exactly 5 criteria
        for category in ValidationCategory:
            category_criteria = [c for c in validator.criteria if c.category == category]
            assert len(category_criteria) == 5, f"Category {category} should have 5 criteria"
    
    def test_performance_criteria(self):
        """Test performance criteria are correctly defined."""
        validator = FinalValidationCriteria()
        perf_criteria = [c for c in validator.criteria if c.category == ValidationCategory.PERFORMANCE]
        
        # Check specific performance criteria
        expected_ids = [
            "perf_api_response_time",
            "perf_page_load_time", 
            "perf_concurrent_users",
            "perf_uptime_sla",
            "perf_error_rate"
        ]
        
        actual_ids = [c.id for c in perf_criteria]
        assert set(actual_ids) == set(expected_ids)
        
        # Check target values match problem statement
        api_criterion = next(c for c in perf_criteria if c.id == "perf_api_response_time")
        assert "200ms" in api_criterion.target_value
        
        users_criterion = next(c for c in perf_criteria if c.id == "perf_concurrent_users")
        assert "10,000" in users_criterion.target_value or "10k" in users_criterion.target_value.lower()
    
    def test_security_criteria(self):
        """Test security criteria are correctly defined."""
        validator = FinalValidationCriteria()
        sec_criteria = [c for c in validator.criteria if c.category == ValidationCategory.SECURITY]
        
        expected_ids = [
            "sec_owasp_top10",
            "sec_pci_dss",
            "sec_gdpr",
            "sec_soc2",
            "sec_penetration_testing"
        ]
        
        actual_ids = [c.id for c in sec_criteria]
        assert set(actual_ids) == set(expected_ids)
    
    def test_scalability_criteria(self):
        """Test scalability criteria are correctly defined."""
        validator = FinalValidationCriteria()
        scale_criteria = [c for c in validator.criteria if c.category == ValidationCategory.SCALABILITY]
        
        expected_ids = [
            "scale_horizontal_scaling",
            "scale_auto_scaling",
            "scale_database_sharding",
            "scale_cdn_integration",
            "scale_multi_region"
        ]
        
        actual_ids = [c.id for c in scale_criteria]
        assert set(actual_ids) == set(expected_ids)
    
    def test_quality_criteria(self):
        """Test quality criteria are correctly defined."""
        validator = FinalValidationCriteria()
        quality_criteria = [c for c in validator.criteria if c.category == ValidationCategory.QUALITY]
        
        expected_ids = [
            "quality_test_coverage",
            "quality_critical_bugs",
            "quality_code_quality",
            "quality_documentation",
            "quality_accessibility"
        ]
        
        actual_ids = [c.id for c in quality_criteria]
        assert set(actual_ids) == set(expected_ids)
        
        # Check specific quality targets
        coverage_criterion = next(c for c in quality_criteria if c.id == "quality_test_coverage")
        assert "90%" in coverage_criterion.target_value
    
    @pytest.mark.asyncio
    async def test_validation_execution(self):
        """Test that validation can be executed successfully."""
        validator = FinalValidationCriteria()
        
        # Run validation
        report = await validator.validate_all_criteria()
        
        # Verify report structure
        assert isinstance(report, ValidationReport)
        assert report.total_criteria == 20
        assert report.overall_score >= 0.0
        assert report.overall_score <= 100.0
        
        # Verify all criteria have been processed
        assert len(report.criteria) == 20
        
        # Verify each criterion has a status
        for criterion in report.criteria:
            assert criterion.status in ValidationStatus
            assert criterion.timestamp is not None
    
    @pytest.mark.asyncio 
    async def test_gdpr_validation_passes(self):
        """Test that GDPR validation correctly identifies existing compliance framework."""
        validator = FinalValidationCriteria()
        
        # Find GDPR criterion
        gdpr_criterion = next(c for c in validator.criteria if c.id == "sec_gdpr")
        
        # Validate it
        await validator._validate_criterion(gdpr_criterion)
        
        # Should pass since data_management/governance/compliance.py exists
        assert gdpr_criterion.status == ValidationStatus.PASSED
    
    @pytest.mark.asyncio
    async def test_horizontal_scaling_validation(self):
        """Test that horizontal scaling validation works correctly."""
        validator = FinalValidationCriteria()
        
        # Find horizontal scaling criterion
        scaling_criterion = next(c for c in validator.criteria if c.id == "scale_horizontal_scaling")
        
        # Validate it
        await validator._validate_criterion(scaling_criterion)
        
        # Should pass since config/deployment/scaling_config.py exists
        assert scaling_criterion.status == ValidationStatus.PASSED
    
    def test_report_generation(self):
        """Test validation report generation."""
        validator = FinalValidationCriteria()
        
        # Create mock criteria with different statuses
        validator.criteria = [
            ValidationCriterion(
                id="test_passed", name="Test Passed", description="Test",
                category=ValidationCategory.PERFORMANCE, target_value="100%",
                status=ValidationStatus.PASSED
            ),
            ValidationCriterion(
                id="test_in_progress", name="Test In Progress", description="Test",
                category=ValidationCategory.SECURITY, target_value="100%",
                status=ValidationStatus.IN_PROGRESS
            ),
            ValidationCriterion(
                id="test_warning", name="Test Warning", description="Test",
                category=ValidationCategory.SCALABILITY, target_value="100%",
                status=ValidationStatus.WARNING
            ),
            ValidationCriterion(
                id="test_failed", name="Test Failed", description="Test",
                category=ValidationCategory.QUALITY, target_value="100%",
                status=ValidationStatus.FAILED
            ),
        ]
        
        report = validator._generate_report()
        
        # Test counts
        assert report.total_criteria == 4
        assert report.passed == 1
        assert report.in_progress == 1
        assert report.warnings == 1
        assert report.failed == 1
        
        # Test score calculation (passed + in_progress/2) / total * 100
        expected_score = (1 + 0.5) / 4 * 100  # 37.5%
        assert report.overall_score == expected_score
    
    def test_json_serialization(self):
        """Test that reports can be serialized to JSON."""
        validator = FinalValidationCriteria()
        
        # Create simple test criterion
        test_criterion = ValidationCriterion(
            id="test", name="Test", description="Test description",
            category=ValidationCategory.PERFORMANCE, target_value="100%",
            status=ValidationStatus.PASSED, message="Test message"
        )
        
        validator.criteria = [test_criterion]
        report = validator._generate_report()
        
        # Test JSON serialization
        try:
            json_str = json.dumps(report, default=str)
            parsed = json.loads(json_str)
            assert parsed is not None
        except Exception as e:
            pytest.fail(f"JSON serialization failed: {e}")


class TestValidationDashboard:
    """Test the validation dashboard."""
    
    @pytest.mark.asyncio
    async def test_dashboard_generation(self):
        """Test that dashboard can be generated."""
        dashboard = ValidationDashboard()
        
        # Generate dashboard
        dashboard_path = await dashboard.generate_dashboard()
        
        # Verify file was created
        assert Path(dashboard_path).exists()
        
        # Verify HTML content
        with open(dashboard_path, 'r') as f:
            content = f.read()
            
        assert "CRITÈRES DE VALIDATION FINALE" in content
        assert "Performance" in content
        assert "Security" in content
        assert "Scalability" in content
        assert "Quality" in content
    
    @pytest.mark.asyncio
    async def test_markdown_generation(self):
        """Test markdown report generation."""
        dashboard = ValidationDashboard()
        
        # Get validation report
        report = await dashboard.validator.validate_all_criteria()
        
        # Generate markdown
        markdown = dashboard.generate_markdown_report(report)
        
        # Verify markdown content
        assert "# 🎯 CRITÈRES DE VALIDATION FINALE" in markdown
        assert "### Performance" in markdown
        assert "### Security" in markdown
        assert "### Scalability" in markdown
        assert "### Quality" in markdown
        
        # Check for specific criteria from problem statement
        assert "< 200ms API response time" in markdown
        assert "99.9% uptime SLA" in markdown
        assert "OWASP Top 10 compliant" in markdown
        assert "90%+ test coverage" in markdown


class TestIntegration:
    """Integration tests for the complete validation system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_validation(self):
        """Test complete end-to-end validation workflow."""
        
        # 1. Initialize validator
        validator = FinalValidationCriteria()
        
        # 2. Run validation
        report = await validator.validate_all_criteria()
        
        # 3. Verify report completeness
        assert report.total_criteria == 20
        assert all(criterion.timestamp for criterion in report.criteria)
        
        # 4. Save report
        validator.save_report(report, "test_validation_report.json")
        assert Path("test_validation_report.json").exists()
        
        # 5. Generate dashboard
        dashboard = ValidationDashboard()
        dashboard_path = await dashboard.generate_dashboard()
        assert Path(dashboard_path).exists()
        
        # 6. Generate markdown
        markdown = dashboard.generate_markdown_report(report)
        assert len(markdown) > 500  # Should be substantial content
        
        # Cleanup
        Path("test_validation_report.json").unlink(missing_ok=True)
    
    def test_problem_statement_compliance(self):
        """Test that our implementation matches the exact problem statement requirements."""
        validator = FinalValidationCriteria()
        
        # Performance criteria from problem statement
        perf_criteria = [c for c in validator.criteria if c.category == ValidationCategory.PERFORMANCE]
        perf_names = [c.description for c in perf_criteria]
        
        assert any("200ms" in desc for desc in perf_names), "Missing < 200ms API response time"
        assert any("3s" in desc for desc in perf_names), "Missing < 3s page load time"
        assert any("10k" in desc.lower() or "10,000" in desc for desc in perf_names), "Missing 10k concurrent users"
        assert any("99.9%" in desc for desc in perf_names), "Missing 99.9% uptime SLA"
        assert any("1%" in desc for desc in perf_names), "Missing < 1% error rate"
        
        # Security criteria from problem statement
        sec_criteria = [c for c in validator.criteria if c.category == ValidationCategory.SECURITY]
        sec_names = [c.description for c in sec_criteria]
        
        assert any("owasp" in desc.lower() for desc in sec_names), "Missing OWASP Top 10"
        assert any("pci" in desc.lower() for desc in sec_names), "Missing PCI DSS"
        assert any("gdpr" in desc.lower() for desc in sec_names), "Missing GDPR"
        assert any("soc 2" in desc.lower() for desc in sec_names), "Missing SOC 2"
        assert any("penetration" in desc.lower() for desc in sec_names), "Missing penetration testing"
        
        # Scalability criteria from problem statement
        scale_criteria = [c for c in validator.criteria if c.category == ValidationCategory.SCALABILITY]
        scale_names = [c.description for c in scale_criteria]
        
        assert any("horizontal" in desc.lower() for desc in scale_names), "Missing horizontal scaling"
        assert any("auto-scaling" in desc.lower() or "autoscaling" in desc.lower() for desc in scale_names), "Missing auto-scaling"
        assert any("sharding" in desc.lower() for desc in scale_names), "Missing database sharding"
        assert any("cdn" in desc.lower() for desc in scale_names), "Missing CDN"
        assert any("multi-region" in desc.lower() for desc in scale_names), "Missing multi-region"
        
        # Quality criteria from problem statement
        quality_criteria = [c for c in validator.criteria if c.category == ValidationCategory.QUALITY]
        quality_names = [c.description for c in quality_criteria]
        
        assert any("90%" in desc for desc in quality_names), "Missing 90%+ test coverage"
        assert any("critical bug" in desc.lower() for desc in quality_names), "Missing 0 critical bugs"
        assert any("code quality" in desc.lower() for desc in quality_names), "Missing A+ code quality"
        assert any("documentation" in desc.lower() for desc in quality_names), "Missing documentation 100%"
        assert any("accessibility" in desc.lower() for desc in quality_names), "Missing accessibility AA"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])