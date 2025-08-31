"""
Tests for Ultra-Advanced SEO Techniques

This test module validates the functionality of the ultra-advanced SEO
automation system including API integrations, real-time trending analysis,
and automated keyword research.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from seo.optimization import (
    UltraAdvancedKeywordResearch, ResearchParameters, ResearchDepth,
    ResearchStrategy, RealTimeTrendingSystem, UltraAdvancedSEOManager,
    AutomationConfig, AutomationMode, NotificationChannel, APIProvider,
    create_seo_automation_manager
)


class TestUltraAdvancedKeywordResearch:
    """Test ultra-advanced keyword research functionality"""
    
    @pytest.fixture
    def research_engine(self):
        """Create research engine for testing"""
        return UltraAdvancedKeywordResearch()
    
    @pytest.fixture
    def sample_parameters(self):
        """Create sample research parameters"""
        return ResearchParameters(
            seed_keywords=["AI", "machine learning", "artificial intelligence"],
            target_industry="technology",
            target_audience="developers",
            research_depth=ResearchDepth.COMPREHENSIVE,
            research_strategy=ResearchStrategy.FULL_SPECTRUM,
            max_keywords=50
        )
    
    @pytest.mark.asyncio
    async def test_ultra_advanced_research(self, research_engine, sample_parameters):
        """Test comprehensive research functionality"""
        
        result = await research_engine.conduct_ultra_advanced_research(sample_parameters)
        
        # Verify result structure
        assert result is not None
        assert hasattr(result, 'keyword_opportunities')
        assert hasattr(result, 'competitor_gap_analysis')
        assert hasattr(result, 'trending_insights')
        assert hasattr(result, 'research_metadata')
        
        # Verify keyword opportunities
        assert len(result.keyword_opportunities) > 0
        assert len(result.keyword_opportunities) <= sample_parameters.max_keywords
        
        # Check keyword opportunity structure
        first_opportunity = result.keyword_opportunities[0]
        assert hasattr(first_opportunity, 'keyword')
        assert hasattr(first_opportunity, 'opportunity_score')
        assert hasattr(first_opportunity, 'search_volume')
        assert hasattr(first_opportunity, 'competition')
        assert hasattr(first_opportunity, 'confidence_level')
        
        # Verify opportunity scores are valid
        for opp in result.keyword_opportunities:
            assert 0 <= opp.opportunity_score <= 100
            assert 0 <= opp.competition <= 1
            assert 0 <= opp.confidence_level <= 1
        
        # Verify metadata
        assert result.research_metadata['research_depth'] == sample_parameters.research_depth.value
        assert result.research_metadata['total_keywords_analyzed'] == len(result.keyword_opportunities)
    
    @pytest.mark.asyncio
    async def test_research_with_competitor_analysis(self, research_engine):
        """Test research with competitor analysis"""
        
        parameters = ResearchParameters(
            seed_keywords=["SEO", "digital marketing"],
            target_industry="marketing",
            target_audience="marketers",
            competitor_domains=["competitor1.com", "competitor2.com"],
            include_competitor_analysis=True,
            research_depth=ResearchDepth.STANDARD
        )
        
        result = await research_engine.conduct_ultra_advanced_research(parameters)
        
        # Verify competitor analysis
        assert len(result.competitor_gap_analysis) > 0
        
        competitor_analysis = result.competitor_gap_analysis[0]
        assert hasattr(competitor_analysis, 'competitor_domain')
        assert hasattr(competitor_analysis, 'keyword_gaps')
        assert hasattr(competitor_analysis, 'content_opportunities')
        assert hasattr(competitor_analysis, 'traffic_potential')
        
        # Verify competitor domain matches input
        analyzed_domains = [comp.competitor_domain for comp in result.competitor_gap_analysis]
        for domain in parameters.competitor_domains:
            assert domain in analyzed_domains
    
    @pytest.mark.asyncio
    async def test_roi_calculations(self, research_engine, sample_parameters):
        """Test ROI calculation functionality"""
        
        result = await research_engine.conduct_ultra_advanced_research(sample_parameters)
        
        # Verify ROI estimates exist
        assert result.roi_estimates is not None
        assert 'estimated_content_investment_usd' in result.roi_estimates
        assert 'estimated_monthly_roi_percentage' in result.roi_estimates
        assert 'payback_period_months' in result.roi_estimates
        
        # Verify ROI values are reasonable
        assert result.roi_estimates['estimated_content_investment_usd'] > 0
        assert result.roi_estimates['estimated_monthly_roi_percentage'] >= 0


class TestRealTimeTrendingSystem:
    """Test real-time trending system functionality"""
    
    @pytest.fixture
    def trending_system(self):
        """Create trending system for testing"""
        return RealTimeTrendingSystem(update_interval=1)  # 1 second for testing
    
    def test_trending_system_initialization(self, trending_system):
        """Test trending system initialization"""
        
        assert trending_system.update_interval == 1
        assert not trending_system.is_monitoring
        assert len(trending_system.alerts) == 0
        assert len(trending_system.callbacks) == 0
    
    def test_add_alert(self, trending_system):
        """Test adding trend alerts"""
        from seo.optimization import TrendAlert, AlertSeverity
        
        alert = TrendAlert(
            keyword_pattern="AI",
            threshold_type="volume",
            threshold_value=1000,
            severity=AlertSeverity.HIGH
        )
        
        trending_system.add_alert(alert)
        
        assert len(trending_system.alerts) == 1
        assert trending_system.alerts[0].keyword_pattern == "AI"
        assert trending_system.alerts[0].severity == AlertSeverity.HIGH
    
    def test_keyword_subscription(self, trending_system):
        """Test keyword subscription functionality"""
        
        callback_called = False
        
        def test_callback(trend_data):
            nonlocal callback_called
            callback_called = True
        
        trending_system.subscribe_to_keyword("test keyword", test_callback)
        
        assert "test keyword" in trending_system.callbacks
        assert len(trending_system.callbacks["test keyword"]) == 1
    
    @pytest.mark.asyncio
    async def test_trending_opportunities(self, trending_system):
        """Test trending opportunities detection"""
        
        # Start monitoring briefly to generate some data
        trending_system.start_monitoring(["AI", "machine learning"])
        
        # Wait a moment for data collection
        await asyncio.sleep(2)
        
        opportunities = trending_system.get_trending_opportunities(min_opportunity_score=50.0)
        
        # Stop monitoring
        trending_system.stop_monitoring()
        
        # Verify opportunities structure
        for opp in opportunities:
            assert hasattr(opp, 'keyword')
            assert hasattr(opp, 'opportunity_score')
            assert hasattr(opp, 'current_volume')
            assert hasattr(opp, 'growth_rate')
            assert hasattr(opp, 'confidence')
            assert opp.opportunity_score >= 50.0


class TestSEOAutomationManager:
    """Test SEO automation manager functionality"""
    
    @pytest.fixture
    def automation_config(self):
        """Create automation config for testing"""
        return AutomationConfig(
            automation_mode=AutomationMode.MANUAL,
            research_frequency_hours=1,
            trending_monitoring=True,
            notification_channels=[NotificationChannel.IN_APP]
        )
    
    @pytest.fixture
    def seo_manager(self, automation_config):
        """Create SEO manager for testing"""
        return UltraAdvancedSEOManager(automation_config)
    
    def test_seo_manager_initialization(self, seo_manager, automation_config):
        """Test SEO manager initialization"""
        
        assert seo_manager.config.automation_mode == AutomationMode.MANUAL
        assert seo_manager.config.trending_monitoring is True
        assert not seo_manager.automation_active
        assert seo_manager.last_research_time is None
    
    @pytest.mark.asyncio
    async def test_manual_research(self, seo_manager):
        """Test manual research functionality"""
        
        parameters = ResearchParameters(
            seed_keywords=["test", "keyword"],
            target_industry="technology",
            target_audience="developers",
            research_depth=ResearchDepth.BASIC,
            max_keywords=10
        )
        
        result = await seo_manager.conduct_manual_research(parameters)
        
        # Verify research was conducted
        assert result is not None
        assert len(result.keyword_opportunities) > 0
        assert seo_manager.last_research_time is not None
        assert len(seo_manager.insights_history) > 0
    
    @pytest.mark.asyncio
    async def test_real_time_opportunities(self, seo_manager):
        """Test real-time opportunities retrieval"""
        
        # Start automation to generate data
        await seo_manager.start_automation(["AI", "technology"])
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        opportunities = await seo_manager.get_real_time_opportunities(min_score=50.0)
        
        # Stop automation
        await seo_manager.stop_automation()
        
        # Verify opportunities format
        for opp in opportunities:
            assert 'keyword' in opp
            assert 'opportunity_score' in opp
            assert 'current_volume' in opp
            assert 'growth_rate' in opp
            assert opp['opportunity_score'] >= 50.0
    
    @pytest.mark.asyncio
    async def test_automation_report_generation(self, seo_manager):
        """Test automation report generation"""
        
        # Generate some insights first
        parameters = ResearchParameters(
            seed_keywords=["test"],
            target_industry="technology",
            target_audience="developers",
            research_depth=ResearchDepth.BASIC,
            max_keywords=5
        )
        
        await seo_manager.conduct_manual_research(parameters)
        
        # Generate report
        report = await seo_manager.generate_automation_report(time_period_hours=1)
        
        # Verify report structure
        assert report is not None
        assert hasattr(report, 'report_id')
        assert hasattr(report, 'generated_at')
        assert hasattr(report, 'performance_insights')
        assert hasattr(report, 'automation_recommendations')
        assert hasattr(report, 'api_usage_stats')
        
        # Verify report contains insights
        assert len(report.performance_insights) > 0
        assert len(report.automation_recommendations) > 0


class TestAPIIntegrations:
    """Test API integration functionality"""
    
    def test_api_credentials_loading(self):
        """Test API credentials loading"""
        
        with patch.dict('os.environ', {
            'GOOGLE_ADS_API_KEY': 'test_google_key',
            'GOOGLE_ADS_CUSTOMER_ID': 'test_customer_id',
            'SEMRUSH_API_KEY': 'test_semrush_key',
            'AHREFS_API_KEY': 'test_ahrefs_key'
        }):
            from seo.optimization import load_api_credentials
            
            credentials = load_api_credentials()
            
            assert APIProvider.GOOGLE_KEYWORD_PLANNER in credentials
            assert APIProvider.SEMRUSH in credentials
            assert APIProvider.AHREFS in credentials
            
            google_creds = credentials[APIProvider.GOOGLE_KEYWORD_PLANNER]
            assert google_creds.api_key == 'test_google_key'
            assert google_creds.additional_params['customer_id'] == 'test_customer_id'
    
    @pytest.mark.asyncio
    async def test_api_integration_manager(self):
        """Test API integration manager"""
        from seo.optimization import APIIntegrationManager, APICredentials
        
        manager = APIIntegrationManager()
        
        # Add test credentials
        test_credentials = APICredentials(
            provider=APIProvider.GOOGLE_KEYWORD_PLANNER,
            api_key="test_key",
            additional_params={"customer_id": "test_id"}
        )
        
        manager.add_integration(APIProvider.GOOGLE_KEYWORD_PLANNER, test_credentials)
        
        assert APIProvider.GOOGLE_KEYWORD_PLANNER in manager.integrations
        assert APIProvider.GOOGLE_KEYWORD_PLANNER in manager.credentials


class TestFactoryFunctions:
    """Test factory functions and convenience methods"""
    
    def test_create_seo_automation_manager(self):
        """Test SEO automation manager factory function"""
        
        manager = create_seo_automation_manager(
            automation_mode=AutomationMode.SCHEDULED,
            research_frequency_hours=12,
            enable_trending=True,
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
        )
        
        assert isinstance(manager, UltraAdvancedSEOManager)
        assert manager.config.automation_mode == AutomationMode.SCHEDULED
        assert manager.config.research_frequency_hours == 12
        assert manager.config.trending_monitoring is True
        assert NotificationChannel.EMAIL in manager.config.notification_channels
        assert NotificationChannel.SLACK in manager.config.notification_channels


class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_seo_workflow(self):
        """Test complete SEO automation workflow"""
        
        # Create manager with full automation
        manager = create_seo_automation_manager(
            automation_mode=AutomationMode.MANUAL,  # Use manual for testing
            enable_trending=True
        )
        
        # Start automation
        await manager.start_automation(["SEO", "automation", "testing"])
        
        # Conduct manual research
        parameters = ResearchParameters(
            seed_keywords=["SEO automation", "keyword research"],
            target_industry="marketing",
            target_audience="marketers",
            research_depth=ResearchDepth.COMPREHENSIVE,
            max_keywords=20
        )
        
        research_result = await manager.conduct_manual_research(parameters)
        
        # Get real-time opportunities
        opportunities = await manager.get_real_time_opportunities(min_score=60.0)
        
        # Generate comprehensive report
        report = await manager.generate_automation_report(time_period_hours=1)
        
        # Add keyword alert
        from seo.optimization import AlertSeverity
        await manager.add_keyword_alert(
            keyword_pattern="automation",
            threshold_type="volume",
            threshold_value=5000,
            severity=AlertSeverity.MEDIUM
        )
        
        # Stop automation
        await manager.stop_automation()
        
        # Verify workflow results
        assert research_result is not None
        assert len(research_result.keyword_opportunities) > 0
        assert report is not None
        assert report.report_id is not None
        
        # Verify insights were generated
        assert len(manager.insights_history) > 0
    
    @pytest.mark.asyncio
    async def test_export_functionality(self):
        """Test data export functionality"""
        
        manager = create_seo_automation_manager()
        
        # Conduct research for export
        parameters = ResearchParameters(
            seed_keywords=["export", "test"],
            target_industry="technology",
            target_audience="developers",
            research_depth=ResearchDepth.BASIC,
            max_keywords=5
        )
        
        result = await manager.conduct_manual_research(parameters)
        
        # Test JSON export
        json_export = await manager.export_research_data(result, format="json")
        assert json_export is not None
        assert '"keyword_opportunities"' in json_export
        
        # Test CSV export
        csv_export = await manager.export_research_data(result, format="csv")
        assert csv_export is not None
        assert "Keyword,Opportunity Score" in csv_export


# Performance and stress tests
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_large_keyword_research(self):
        """Test research with large keyword sets"""
        
        research_engine = UltraAdvancedKeywordResearch()
        
        # Create parameters with many keywords
        large_keyword_list = [f"keyword_{i}" for i in range(50)]
        
        parameters = ResearchParameters(
            seed_keywords=large_keyword_list,
            target_industry="technology",
            target_audience="developers",
            research_depth=ResearchDepth.STANDARD,
            max_keywords=100
        )
        
        start_time = datetime.now()
        result = await research_engine.conduct_ultra_advanced_research(parameters)
        end_time = datetime.now()
        
        # Verify performance (should complete within reasonable time)
        duration = (end_time - start_time).total_seconds()
        assert duration < 30  # Should complete within 30 seconds
        
        # Verify result quality
        assert len(result.keyword_opportunities) > 0
        assert len(result.keyword_opportunities) <= parameters.max_keywords
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent SEO operations"""
        
        manager = create_seo_automation_manager()
        
        # Define multiple research tasks
        tasks = []
        for i in range(3):
            parameters = ResearchParameters(
                seed_keywords=[f"concurrent_{i}", f"test_{i}"],
                target_industry="technology",
                target_audience="developers",
                research_depth=ResearchDepth.BASIC,
                max_keywords=5
            )
            
            task = manager.conduct_manual_research(parameters)
            tasks.append(task)
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all tasks completed successfully
        assert len(results) == 3
        for result in results:
            assert result is not None
            assert len(result.keyword_opportunities) > 0


if __name__ == "__main__":
    # Run basic functionality test
    async def run_basic_test():
        print("Running basic ultra-advanced SEO functionality test...")
        
        # Test basic research
        research_engine = UltraAdvancedKeywordResearch()
        parameters = ResearchParameters(
            seed_keywords=["AI", "automation"],
            target_industry="technology",
            target_audience="developers",
            research_depth=ResearchDepth.STANDARD,
            max_keywords=10
        )
        
        result = await research_engine.conduct_ultra_advanced_research(parameters)
        print(f"✓ Research completed: {len(result.keyword_opportunities)} opportunities found")
        
        # Test trending system
        trending_system = RealTimeTrendingSystem(update_interval=1)
        trending_system.start_monitoring(["AI"])
        await asyncio.sleep(2)
        opportunities = trending_system.get_trending_opportunities(50.0)
        trending_system.stop_monitoring()
        print(f"✓ Trending analysis completed: {len(opportunities)} opportunities found")
        
        # Test automation manager
        manager = create_seo_automation_manager()
        report = await manager.generate_automation_report()
        print(f"✓ Automation report generated: {report.report_id}")
        
        print("All basic tests passed! ✅")
    
    # Run the test
    asyncio.run(run_basic_test())