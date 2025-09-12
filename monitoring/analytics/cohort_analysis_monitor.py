"""
🔍 MONITORING ANALYTICS - Cohort Analysis Monitor
Enterprise-grade cohort analysis for Ainflue creator ecosystem
Lead Dev IA + ML Engineer Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CohortType(Enum):
    """Cohort analysis types for creator ecosystem"""
    CREATOR_ACQUISITION = "creator_acquisition"
    CONTENT_ENGAGEMENT = "content_engagement" 
    REVENUE_GENERATION = "revenue_generation"
    COLLABORATION_SUCCESS = "collaboration_success"
    PLATFORM_RETENTION = "platform_retention"

class CohortPeriod(Enum):
    """Time periods for cohort analysis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

@dataclass
class CohortMetrics:
    """Cohort performance metrics"""
    cohort_id: str
    cohort_size: int
    retention_rate: float
    revenue_per_user: float
    engagement_score: float
    conversion_rate: float
    churn_rate: float
    lifetime_value: float
    growth_rate: float
    quality_score: float

class CohortAnalysisMonitor:
    """
    🧠 Advanced Cohort Analysis Monitor for Ainflue Platform
    
    ML-powered cohort tracking with predictive analytics:
    - Creator acquisition cohorts with retention analysis
    - Content engagement cohorts with performance tracking
    - Revenue cohorts with LTV predictions
    - Collaboration success cohorts
    - Advanced clustering and segmentation
    """
    
    def __init__(self, db_url: str, redis_url: str = None):
        """Initialize cohort analysis monitor"""
        self.db_url = db_url
        self.redis_url = redis_url
        self.engine = create_engine(db_url)
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        
        # Cohort analysis cache
        self.cohort_cache: Dict[str, Any] = {}
        self.analysis_results: Dict[str, List[CohortMetrics]] = {}
        
        logger.info("🔍 Cohort Analysis Monitor initialized")

    async def analyze_creator_acquisition_cohorts(
        self, 
        start_date: datetime,
        end_date: datetime,
        period: CohortPeriod = CohortPeriod.MONTHLY
    ) -> List[CohortMetrics]:
        """
        📊 Analyze creator acquisition cohorts
        
        Track new creator retention and performance over time
        """
        try:
            logger.info(f"🎯 Analyzing creator acquisition cohorts: {start_date} to {end_date}")
            
            # Query creator acquisition data
            query = text("""
                WITH creator_cohorts AS (
                    SELECT 
                        DATE_TRUNC(:period, created_at) as cohort_period,
                        user_id,
                        created_at,
                        EXTRACT(EPOCH FROM (NOW() - created_at))/86400 as days_since_signup
                    FROM users 
                    WHERE user_type = 'creator'
                    AND created_at BETWEEN :start_date AND :end_date
                ),
                cohort_metrics AS (
                    SELECT 
                        c.cohort_period,
                        COUNT(DISTINCT c.user_id) as cohort_size,
                        AVG(CASE WHEN a.last_activity > NOW() - INTERVAL '30 days' 
                            THEN 1 ELSE 0 END) as retention_30d,
                        AVG(CASE WHEN a.last_activity > NOW() - INTERVAL '90 days' 
                            THEN 1 ELSE 0 END) as retention_90d,
                        AVG(COALESCE(r.total_revenue, 0)) as avg_revenue,
                        AVG(COALESCE(e.engagement_score, 0)) as avg_engagement
                    FROM creator_cohorts c
                    LEFT JOIN user_activity a ON c.user_id = a.user_id
                    LEFT JOIN user_revenue r ON c.user_id = r.user_id
                    LEFT JOIN user_engagement e ON c.user_id = e.user_id
                    GROUP BY c.cohort_period
                )
                SELECT * FROM cohort_metrics ORDER BY cohort_period
            """)
            
            result = self.engine.execute(query, {
                'period': period.value,
                'start_date': start_date,
                'end_date': end_date
            })
            
            cohorts = []
            for row in result:
                metrics = CohortMetrics(
                    cohort_id=f"creator_acq_{row.cohort_period}",
                    cohort_size=row.cohort_size,
                    retention_rate=float(row.retention_30d or 0),
                    revenue_per_user=float(row.avg_revenue or 0),
                    engagement_score=float(row.avg_engagement or 0),
                    conversion_rate=self._calculate_conversion_rate(row),
                    churn_rate=1.0 - float(row.retention_90d or 0),
                    lifetime_value=self._predict_lifetime_value(row),
                    growth_rate=self._calculate_growth_rate(row),
                    quality_score=self._calculate_quality_score(row)
                )
                cohorts.append(metrics)
            
            # Store results
            self.analysis_results[CohortType.CREATOR_ACQUISITION.value] = cohorts
            
            logger.info(f"✅ Analyzed {len(cohorts)} creator acquisition cohorts")
            return cohorts
            
        except Exception as e:
            logger.error(f"❌ Error analyzing creator acquisition cohorts: {e}")
            return []

    async def analyze_content_engagement_cohorts(
        self,
        content_type: str = "all",
        timeframe: int = 90
    ) -> List[CohortMetrics]:
        """
        🎵 Analyze content engagement cohorts
        
        Track content performance by creation period
        """
        try:
            logger.info(f"🎵 Analyzing content engagement cohorts for {content_type}")
            
            # Query content engagement data
            query = text("""
                WITH content_cohorts AS (
                    SELECT 
                        DATE_TRUNC('month', c.created_at) as cohort_period,
                        c.content_id,
                        c.creator_id,
                        c.content_type,
                        AVG(e.engagement_rate) as avg_engagement,
                        SUM(e.views) as total_views,
                        SUM(e.likes) as total_likes,
                        SUM(e.shares) as total_shares,
                        SUM(e.comments) as total_comments
                    FROM content c
                    LEFT JOIN content_engagement e ON c.content_id = e.content_id
                    WHERE c.created_at > NOW() - INTERVAL :timeframe DAY
                    AND (:content_type = 'all' OR c.content_type = :content_type)
                    GROUP BY c.cohort_period, c.content_id, c.creator_id, c.content_type
                )
                SELECT 
                    cohort_period,
                    COUNT(*) as content_count,
                    AVG(avg_engagement) as cohort_engagement,
                    SUM(total_views) as cohort_views,
                    AVG(total_likes::float / NULLIF(total_views, 0)) as like_rate,
                    AVG(total_shares::float / NULLIF(total_views, 0)) as share_rate
                FROM content_cohorts
                GROUP BY cohort_period
                ORDER BY cohort_period
            """)
            
            result = self.engine.execute(query, {
                'timeframe': timeframe,
                'content_type': content_type
            })
            
            cohorts = []
            for row in result:
                metrics = CohortMetrics(
                    cohort_id=f"content_eng_{row.cohort_period}_{content_type}",
                    cohort_size=row.content_count,
                    retention_rate=self._calculate_content_retention(row),
                    revenue_per_user=0.0,  # Not applicable for content cohorts
                    engagement_score=float(row.cohort_engagement or 0),
                    conversion_rate=float(row.like_rate or 0),
                    churn_rate=self._calculate_content_churn(row),
                    lifetime_value=self._estimate_content_value(row),
                    growth_rate=self._calculate_content_growth(row),
                    quality_score=self._calculate_content_quality(row)
                )
                cohorts.append(metrics)
            
            self.analysis_results[CohortType.CONTENT_ENGAGEMENT.value] = cohorts
            
            logger.info(f"✅ Analyzed {len(cohorts)} content engagement cohorts")
            return cohorts
            
        except Exception as e:
            logger.error(f"❌ Error analyzing content engagement cohorts: {e}")
            return []

    async def analyze_revenue_cohorts(
        self,
        period: CohortPeriod = CohortPeriod.MONTHLY
    ) -> List[CohortMetrics]:
        """
        💰 Analyze revenue generation cohorts
        
        Track revenue performance by creator signup period
        """
        try:
            logger.info(f"💰 Analyzing revenue cohorts by {period.value}")
            
            # Query revenue cohort data
            query = text("""
                WITH revenue_cohorts AS (
                    SELECT 
                        DATE_TRUNC(:period, u.created_at) as cohort_period,
                        u.user_id,
                        COALESCE(SUM(t.amount), 0) as total_revenue,
                        COUNT(t.transaction_id) as transaction_count,
                        MAX(t.created_at) as last_transaction_date,
                        MIN(t.created_at) as first_transaction_date,
                        AVG(t.amount) as avg_transaction_value
                    FROM users u
                    LEFT JOIN transactions t ON u.user_id = t.creator_id
                    WHERE u.user_type = 'creator'
                    AND u.created_at > NOW() - INTERVAL '12 months'
                    GROUP BY cohort_period, u.user_id
                ),
                cohort_summary AS (
                    SELECT 
                        cohort_period,
                        COUNT(*) as cohort_size,
                        AVG(total_revenue) as avg_revenue_per_user,
                        SUM(total_revenue) as cohort_total_revenue,
                        AVG(transaction_count) as avg_transactions,
                        COUNT(CASE WHEN total_revenue > 0 THEN 1 END)::float / COUNT(*) as monetization_rate,
                        AVG(CASE WHEN total_revenue > 0 THEN 
                            EXTRACT(EPOCH FROM (last_transaction_date - first_transaction_date))/86400 
                            ELSE 0 END) as avg_monetization_period
                    FROM revenue_cohorts
                    GROUP BY cohort_period
                )
                SELECT * FROM cohort_summary ORDER BY cohort_period
            """)
            
            result = self.engine.execute(query, {'period': period.value})
            
            cohorts = []
            for row in result:
                metrics = CohortMetrics(
                    cohort_id=f"revenue_{row.cohort_period}",
                    cohort_size=row.cohort_size,
                    retention_rate=self._calculate_revenue_retention(row),
                    revenue_per_user=float(row.avg_revenue_per_user or 0),
                    engagement_score=self._calculate_revenue_engagement(row),
                    conversion_rate=float(row.monetization_rate or 0),
                    churn_rate=1.0 - float(row.monetization_rate or 0),
                    lifetime_value=self._predict_revenue_ltv(row),
                    growth_rate=self._calculate_revenue_growth(row),
                    quality_score=self._calculate_revenue_quality(row)
                )
                cohorts.append(metrics)
            
            self.analysis_results[CohortType.REVENUE_GENERATION.value] = cohorts
            
            logger.info(f"✅ Analyzed {len(cohorts)} revenue cohorts")
            return cohorts
            
        except Exception as e:
            logger.error(f"❌ Error analyzing revenue cohorts: {e}")
            return []

    async def perform_cohort_clustering(
        self,
        cohort_type: CohortType,
        features: List[str] = None
    ) -> Dict[str, Any]:
        """
        🤖 ML-powered cohort clustering
        
        Use machine learning to identify cohort patterns
        """
        try:
            logger.info(f"🤖 Performing ML clustering for {cohort_type.value}")
            
            if cohort_type.value not in self.analysis_results:
                logger.warning(f"No analysis results found for {cohort_type.value}")
                return {}
            
            cohorts = self.analysis_results[cohort_type.value]
            if not cohorts:
                return {}
            
            # Prepare feature matrix
            if features is None:
                features = ['retention_rate', 'revenue_per_user', 'engagement_score', 
                          'conversion_rate', 'lifetime_value', 'quality_score']
            
            feature_matrix = []
            cohort_ids = []
            
            for cohort in cohorts:
                row = []
                for feature in features:
                    value = getattr(cohort, feature, 0.0)
                    row.append(float(value or 0.0))
                feature_matrix.append(row)
                cohort_ids.append(cohort.cohort_id)
            
            if not feature_matrix:
                return {}
            
            # Standardize features
            X = np.array(feature_matrix)
            X_scaled = self.scaler.fit_transform(X)
            
            # Perform clustering
            clusters = self.kmeans.fit_predict(X_scaled)
            
            # Analyze clusters
            cluster_analysis = {}
            for i in range(len(clusters)):
                cluster_id = int(clusters[i])
                if cluster_id not in cluster_analysis:
                    cluster_analysis[cluster_id] = {
                        'cohorts': [],
                        'avg_metrics': {},
                        'cluster_size': 0
                    }
                
                cluster_analysis[cluster_id]['cohorts'].append(cohort_ids[i])
                cluster_analysis[cluster_id]['cluster_size'] += 1
            
            # Calculate cluster averages
            for cluster_id in cluster_analysis:
                cluster_cohorts = [c for i, c in enumerate(cohorts) 
                                 if clusters[i] == cluster_id]
                
                if cluster_cohorts:
                    cluster_analysis[cluster_id]['avg_metrics'] = {
                        'retention_rate': np.mean([c.retention_rate for c in cluster_cohorts]),
                        'revenue_per_user': np.mean([c.revenue_per_user for c in cluster_cohorts]),
                        'engagement_score': np.mean([c.engagement_score for c in cluster_cohorts]),
                        'conversion_rate': np.mean([c.conversion_rate for c in cluster_cohorts]),
                        'lifetime_value': np.mean([c.lifetime_value for c in cluster_cohorts]),
                        'quality_score': np.mean([c.quality_score for c in cluster_cohorts])
                    }
            
            result = {
                'cohort_type': cohort_type.value,
                'total_cohorts': len(cohorts),
                'num_clusters': len(cluster_analysis),
                'clusters': cluster_analysis,
                'features_used': features,
                'clustering_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Completed clustering: {len(cluster_analysis)} clusters identified")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error performing cohort clustering: {e}")
            return {}

    def _calculate_conversion_rate(self, row) -> float:
        """Calculate cohort conversion rate"""
        # Implement conversion logic based on available data
        return min(1.0, max(0.0, float(getattr(row, 'retention_30d', 0) or 0)))

    def _predict_lifetime_value(self, row) -> float:
        """Predict cohort lifetime value using ML"""
        # Simplified LTV prediction
        revenue = float(getattr(row, 'avg_revenue', 0) or 0)
        retention = float(getattr(row, 'retention_30d', 0) or 0)
        return revenue * retention * 12  # Annualized estimate

    def _calculate_growth_rate(self, row) -> float:
        """Calculate cohort growth rate"""
        # Simplified growth calculation
        return min(1.0, max(-1.0, float(getattr(row, 'avg_engagement', 0) or 0) / 100))

    def _calculate_quality_score(self, row) -> float:
        """Calculate overall cohort quality score"""
        retention = float(getattr(row, 'retention_30d', 0) or 0)
        engagement = float(getattr(row, 'avg_engagement', 0) or 0) / 100
        revenue = min(1.0, float(getattr(row, 'avg_revenue', 0) or 0) / 1000)
        
        return (retention * 0.4 + engagement * 0.3 + revenue * 0.3)

    def _calculate_content_retention(self, row) -> float:
        """Calculate content cohort retention"""
        engagement = float(getattr(row, 'cohort_engagement', 0) or 0)
        return min(1.0, max(0.0, engagement / 100))

    def _calculate_content_churn(self, row) -> float:
        """Calculate content churn rate"""
        return 1.0 - self._calculate_content_retention(row)

    def _estimate_content_value(self, row) -> float:
        """Estimate content monetary value"""
        views = float(getattr(row, 'cohort_views', 0) or 0)
        engagement = float(getattr(row, 'cohort_engagement', 0) or 0)
        return views * engagement * 0.001  # Simplified value estimation

    def _calculate_content_growth(self, row) -> float:
        """Calculate content growth rate"""
        return min(1.0, max(-1.0, float(getattr(row, 'cohort_engagement', 0) or 0) / 100))

    def _calculate_content_quality(self, row) -> float:
        """Calculate content quality score"""
        engagement = float(getattr(row, 'cohort_engagement', 0) or 0) / 100
        like_rate = float(getattr(row, 'like_rate', 0) or 0)
        share_rate = float(getattr(row, 'share_rate', 0) or 0)
        
        return (engagement * 0.5 + like_rate * 0.3 + share_rate * 0.2)

    def _calculate_revenue_retention(self, row) -> float:
        """Calculate revenue cohort retention"""
        monetization_rate = float(getattr(row, 'monetization_rate', 0) or 0)
        return min(1.0, max(0.0, monetization_rate))

    def _calculate_revenue_engagement(self, row) -> float:
        """Calculate revenue engagement score"""
        transactions = float(getattr(row, 'avg_transactions', 0) or 0)
        return min(1.0, transactions / 10)  # Normalized to 0-1

    def _predict_revenue_ltv(self, row) -> float:
        """Predict revenue lifetime value"""
        avg_revenue = float(getattr(row, 'avg_revenue_per_user', 0) or 0)
        monetization_rate = float(getattr(row, 'monetization_rate', 0) or 0)
        period = float(getattr(row, 'avg_monetization_period', 0) or 0)
        
        # LTV prediction based on current metrics
        if period > 0:
            return avg_revenue * (365 / max(1, period)) * monetization_rate
        return avg_revenue * monetization_rate

    def _calculate_revenue_growth(self, row) -> float:
        """Calculate revenue growth rate"""
        # Simplified growth based on monetization rate
        return float(getattr(row, 'monetization_rate', 0) or 0)

    def _calculate_revenue_quality(self, row) -> float:
        """Calculate revenue quality score"""
        monetization_rate = float(getattr(row, 'monetization_rate', 0) or 0)
        avg_revenue = min(1.0, float(getattr(row, 'avg_revenue_per_user', 0) or 0) / 1000)
        avg_transactions = min(1.0, float(getattr(row, 'avg_transactions', 0) or 0) / 10)
        
        return (monetization_rate * 0.5 + avg_revenue * 0.3 + avg_transactions * 0.2)

    async def generate_cohort_report(
        self,
        cohort_type: CohortType = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        📊 Generate comprehensive cohort analysis report
        """
        try:
            logger.info(f"📊 Generating cohort report for {cohort_type or 'all types'}")
            
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'analysis_summary': {},
                'cohort_details': {},
                'clustering_results': {},
                'recommendations': []
            }
            
            # Include specific cohort type or all
            cohort_types = [cohort_type] if cohort_type else list(CohortType)
            
            for ctype in cohort_types:
                if ctype.value in self.analysis_results:
                    cohorts = self.analysis_results[ctype.value]
                    
                    # Summary statistics
                    if cohorts:
                        report['analysis_summary'][ctype.value] = {
                            'total_cohorts': len(cohorts),
                            'avg_retention_rate': np.mean([c.retention_rate for c in cohorts]),
                            'avg_revenue_per_user': np.mean([c.revenue_per_user for c in cohorts]),
                            'avg_engagement_score': np.mean([c.engagement_score for c in cohorts]),
                            'avg_quality_score': np.mean([c.quality_score for c in cohorts])
                        }
                        
                        # Detailed cohort data
                        report['cohort_details'][ctype.value] = [
                            {
                                'cohort_id': c.cohort_id,
                                'cohort_size': c.cohort_size,
                                'retention_rate': c.retention_rate,
                                'revenue_per_user': c.revenue_per_user,
                                'engagement_score': c.engagement_score,
                                'conversion_rate': c.conversion_rate,
                                'churn_rate': c.churn_rate,
                                'lifetime_value': c.lifetime_value,
                                'growth_rate': c.growth_rate,
                                'quality_score': c.quality_score
                            }
                            for c in cohorts
                        ]
                        
                        # Perform clustering for insights
                        clustering_result = await self.perform_cohort_clustering(ctype)
                        if clustering_result:
                            report['clustering_results'][ctype.value] = clustering_result
            
            # Generate recommendations
            report['recommendations'] = self._generate_recommendations(report)
            
            logger.info("✅ Cohort analysis report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating cohort report: {e}")
            return {}

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on cohort analysis"""
        recommendations = []
        
        try:
            # Analyze each cohort type for recommendations
            for cohort_type, summary in report.get('analysis_summary', {}).items():
                avg_retention = summary.get('avg_retention_rate', 0)
                avg_engagement = summary.get('avg_engagement_score', 0)
                avg_quality = summary.get('avg_quality_score', 0)
                
                if avg_retention < 0.3:
                    recommendations.append(f"🚨 Low retention in {cohort_type} cohorts ({avg_retention:.1%}). Implement retention campaigns.")
                
                if avg_engagement < 0.5:
                    recommendations.append(f"📈 Boost engagement for {cohort_type} cohorts. Current: {avg_engagement:.1%}")
                
                if avg_quality < 0.6:
                    recommendations.append(f"⭐ Focus on quality improvement for {cohort_type}. Current score: {avg_quality:.2f}")
            
            # Add general recommendations
            if len(recommendations) == 0:
                recommendations.append("✅ Cohort performance looks healthy. Continue monitoring trends.")
            
            recommendations.append("🔄 Schedule weekly cohort analysis for trend detection")
            recommendations.append("🎯 Implement predictive churn prevention based on cohort patterns")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("⚠️ Unable to generate specific recommendations. Review cohort data manually.")
        
        return recommendations

# Usage example for testing
async def main():
    """Test the cohort analysis monitor"""
    try:
        # Initialize monitor (would use real DB in production)
        monitor = CohortAnalysisMonitor("postgresql://user:pass@localhost/ainflue")
        
        # Analyze different cohort types
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Creator acquisition cohorts
        creator_cohorts = await monitor.analyze_creator_acquisition_cohorts(
            start_date, end_date, CohortPeriod.MONTHLY
        )
        print(f"Analyzed {len(creator_cohorts)} creator cohorts")
        
        # Content engagement cohorts
        content_cohorts = await monitor.analyze_content_engagement_cohorts("audio")
        print(f"Analyzed {len(content_cohorts)} content cohorts")
        
        # Revenue cohorts
        revenue_cohorts = await monitor.analyze_revenue_cohorts(CohortPeriod.MONTHLY)
        print(f"Analyzed {len(revenue_cohorts)} revenue cohorts")
        
        # Generate comprehensive report
        report = await monitor.generate_cohort_report()
        print(f"Generated report with {len(report.get('recommendations', []))} recommendations")
        
    except Exception as e:
        print(f"Error in cohort analysis: {e}")

if __name__ == "__main__":
    asyncio.run(main())