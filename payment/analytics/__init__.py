"""📊 Payment Analytics Enterprise Module
==========================================

Enterprise payment analytics engine for Creator Economy Platform.
Comprehensive analytics, reporting, and business intelligence capabilities.

Modules:
- Gateway Analytics: Core payment gateway analytics engine
- Revenue Tracker: Platform and creator revenue analytics
- Fraud Detection: ML-powered fraud detection analytics
- Financial Reporting: Enterprise financial reporting and compliance
- Creator Earnings: Creator monetization analytics
- Performance Monitor: Payment system performance monitoring
- Cost Optimization: Payment cost analysis and optimization
- Transaction Intelligence: AI-powered transaction insights
- Payment Forecasting: Predictive payment analytics
- Compliance Analytics: Regulatory compliance monitoring
- Merchant Analytics: Merchant performance and risk analytics
- Subscription Analytics: Subscription business intelligence
- Chargeback Analytics: Chargeback prevention and analysis
- Payment Flow Analyzer: Payment funnel optimization
- Real-time Dashboard: Live analytics dashboard

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .gateway_analytics import (
    PaymentGatewayAnalytics,
    MetricType,
    TimeGranularity,
    AnalyticsScope,
    PerformanceMetrics,
    AnalyticsReport,
    DashboardData
)

# Export all analytics modules when implemented
__all__ = [
    # Core Gateway Analytics
    "PaymentGatewayAnalytics",
    "MetricType", 
    "TimeGranularity",
    "AnalyticsScope",
    "PerformanceMetrics",
    "AnalyticsReport",
    "DashboardData",
    
    # Revenue Analytics
    "RevenueTracker",
    "RevenueCalculator",
    "DistributionAnalyzer",
    "CreatorRevenueTracker",
    
    # Fraud Detection
    "FraudDetectionAnalytics",
    "FraudAnalyzer", 
    "PatternDetector",
    "RiskAssessor",
    
    # Financial Reporting
    "FinancialReporting",
    "ReportGenerator",
    "ComplianceChecker",
    "AuditTrailManager",
    
    # Creator Earnings
    "CreatorEarningsAnalytics",
    "EarningsCalculator",
    "PerformanceAnalyzer",
    "PayoutTracker",
    
    # Performance Monitoring
    "PaymentPerformanceMonitor",
    "PerformanceTracker",
    "SLAMonitor",
    "AlertManager",
    
    # Cost Optimization
    "CostOptimizationAnalyzer",
    "CostAnalyzer",
    "OptimizationEngine",
    "SavingsCalculator",
    
    # Transaction Intelligence
    "TransactionIntelligence",
    "TransactionAnalyzer",
    "PatternRecognizer",
    "IntelligenceEngine",
    
    # Payment Forecasting
    "PaymentForecasting",
    "ForecastingEngine",
    "MLPredictor",
    "TrendAnalyzer",
    
    # Compliance Analytics
    "ComplianceAnalytics",
    "ComplianceMonitor",
    "RegulatoryAnalyzer",
    "AuditManager",
    
    # Merchant Analytics
    "MerchantAnalytics",
    "MerchantAnalyzer",
    "OnboardingTracker",
    "PerformanceEvaluator",
    
    # Subscription Analytics
    "SubscriptionAnalytics",
    "SubscriptionTracker",
    "ChurnAnalyzer",
    "RetentionCalculator",
    
    # Chargeback Analytics
    "ChargebackAnalytics",
    "ChargebackAnalyzer",
    "DisputeTracker",
    "PreventionOptimizer",
    
    # Payment Flow Analytics
    "PaymentFlowAnalyzer",
    "FlowTracker",
    "BottleneckDetector",
    
    # Real-time Dashboard
    "RealTimeDashboard",
    "DashboardEngine",
    "RealTimeProcessor",
    "VisualizationManager"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."