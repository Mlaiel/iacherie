"""🔍 SEO Agent Schema - Enterprise AI Search Engine Optimization
================================================================
Module: alembic/seo_agent_schema.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Enterprise SEO Agent Database Schema - Ultra-Industrial AI-Powered
Responsibility: Database schema for AI-powered SEO optimization, keyword research, and ranking management
================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

SEO Agent Database Schema for:
- Intelligent keyword research and analysis
- Multi-platform SEO optimization
- Content ranking monitoring and improvement
- Competitor analysis and benchmarking
- Automated SEO strategy implementation
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime, timezone
import uuid

# revision identifiers
revision = 'seo_agent_001'
down_revision = 'content_protection_001'
branch_labels = ('seo_agent',)
depends_on = None


def upgrade() -> None:
    """Upgrade: Create SEO agent tables"""
    
    # SEO Agents Configuration
    op.create_table(
        'seo_agents',
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_name', sa.String(255), nullable=False),
        sa.Column('agent_type', sa.String(100), nullable=False),  # keyword_researcher, content_optimizer, rank_tracker, competitor_analyzer
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('specialization', sa.String(100)),  # youtube_seo, google_seo, social_media_seo, ecommerce_seo
        
        # SEO capabilities and configuration
        sa.Column('seo_capabilities', postgresql.JSONB, nullable=False),
        sa.Column('supported_platforms', postgresql.JSONB, nullable=False),
        sa.Column('supported_languages', postgresql.JSONB, nullable=False),
        sa.Column('supported_regions', postgresql.JSONB),
        sa.Column('optimization_strategies', postgresql.JSONB),
        
        # AI/ML model configuration
        sa.Column('model_config', postgresql.JSONB, nullable=False),
        sa.Column('training_data_sources', postgresql.JSONB),
        sa.Column('algorithm_version', sa.String(50)),
        sa.Column('confidence_threshold', sa.Float, default=0.7),
        
        # Performance metrics
        sa.Column('accuracy_rate', sa.Float),
        sa.Column('prediction_accuracy', sa.Float),
        sa.Column('processing_speed_kw_per_hour', sa.Float),  # Keywords processed per hour
        sa.Column('success_rate', sa.Float),  # Successful optimizations / total attempts
        
        # Status and monitoring
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('last_health_check', sa.TIMESTAMP(timezone=True)),
        sa.Column('performance_metrics', postgresql.JSONB),
        sa.Column('error_rate', sa.Float, default=0.0),
        sa.Column('api_quota_usage', postgresql.JSONB),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_seo_agents_type', 'agent_type'),
        sa.Index('idx_seo_agents_specialization', 'specialization'),
        sa.Index('idx_seo_agents_active', 'is_active'),
        sa.Index('idx_seo_agents_performance', 'success_rate'),
    )
    
    # Keyword Research and Analysis
    op.create_table(
        'keyword_research',
        sa.Column('research_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seo_agents.agent_id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Research parameters
        sa.Column('seed_keywords', postgresql.JSONB, nullable=False),
        sa.Column('target_language', sa.String(10), default='en', nullable=False),
        sa.Column('target_region', sa.String(10)),
        sa.Column('target_platform', sa.String(100), nullable=False),
        sa.Column('content_type', sa.String(100)),  # video, article, product, etc.
        sa.Column('industry_category', sa.String(100)),
        
        # Research scope and filters
        sa.Column('search_volume_min', sa.Integer),
        sa.Column('search_volume_max', sa.Integer),
        sa.Column('keyword_difficulty_max', sa.Float),
        sa.Column('cost_per_click_max', sa.Numeric(8, 2)),
        sa.Column('competition_level', sa.String(20)),  # low, medium, high
        sa.Column('commercial_intent', sa.String(20)),  # informational, commercial, transactional
        
        # Research results summary
        sa.Column('total_keywords_found', sa.Integer, default=0),
        sa.Column('primary_keywords_count', sa.Integer, default=0),
        sa.Column('long_tail_keywords_count', sa.Integer, default=0),
        sa.Column('question_keywords_count', sa.Integer, default=0),
        sa.Column('branded_keywords_count', sa.Integer, default=0),
        
        # Analysis metrics
        sa.Column('average_search_volume', sa.Float),
        sa.Column('average_keyword_difficulty', sa.Float),
        sa.Column('average_cost_per_click', sa.Numeric(8, 2)),
        sa.Column('total_market_potential', sa.BigInteger),
        sa.Column('estimated_traffic_potential', sa.Integer),
        
        # Status and processing
        sa.Column('status', sa.String(50), default='pending', nullable=False),
        sa.Column('processing_time_seconds', sa.Float),
        sa.Column('data_sources_used', postgresql.JSONB),
        sa.Column('api_calls_made', sa.Integer),
        sa.Column('error_message', sa.Text),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        
        # Indexes
        sa.Index('idx_keyword_research_agent', 'agent_id'),
        sa.Index('idx_keyword_research_user', 'user_id'),
        sa.Index('idx_keyword_research_tenant', 'tenant_id'),
        sa.Index('idx_keyword_research_platform', 'target_platform'),
        sa.Index('idx_keyword_research_status', 'status'),
        sa.Index('idx_keyword_research_created', 'created_at'),
    )
    
    # Individual Keyword Data
    op.create_table(
        'keywords',
        sa.Column('keyword_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('research_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('keyword_research.research_id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Keyword details
        sa.Column('keyword_text', sa.String(500), nullable=False),
        sa.Column('keyword_type', sa.String(50), nullable=False),  # short_tail, long_tail, question, branded
        sa.Column('language', sa.String(10), nullable=False),
        sa.Column('region', sa.String(10)),
        sa.Column('platform', sa.String(100), nullable=False),
        
        # Search metrics
        sa.Column('search_volume_monthly', sa.Integer),
        sa.Column('search_volume_trend', postgresql.JSONB),  # 12-month trend data
        sa.Column('seasonal_patterns', postgresql.JSONB),
        sa.Column('search_volume_growth_rate', sa.Float),
        
        # Competition and difficulty
        sa.Column('keyword_difficulty', sa.Float),  # 0-100 scale
        sa.Column('competition_level', sa.String(20)),
        sa.Column('top_ranking_pages_count', sa.Integer),
        sa.Column('average_page_authority', sa.Float),
        sa.Column('serp_features', postgresql.JSONB),  # Featured snippets, PAA, etc.
        
        # Commercial metrics
        sa.Column('cost_per_click', sa.Numeric(8, 2)),
        sa.Column('commercial_intent_score', sa.Float),  # 0-1 scale
        sa.Column('buyer_intent_signals', postgresql.JSONB),
        sa.Column('monetization_potential', sa.String(20)),  # low, medium, high
        
        # Content relevance
        sa.Column('relevance_score', sa.Float),  # How relevant to user's content
        sa.Column('content_gaps_identified', postgresql.JSONB),
        sa.Column('suggested_content_angles', postgresql.JSONB),
        sa.Column('related_keywords', postgresql.JSONB),
        
        # SERP analysis
        sa.Column('top_10_competitors', postgresql.JSONB),
        sa.Column('ranking_opportunity_score', sa.Float),
        sa.Column('content_optimization_suggestions', postgresql.JSONB),
        sa.Column('backlink_requirements_estimate', sa.Integer),
        
        # Performance tracking
        sa.Column('is_targeted', sa.Boolean, default=False),
        sa.Column('current_ranking_position', sa.Integer),
        sa.Column('ranking_history', postgresql.JSONB),
        sa.Column('traffic_generated', sa.Integer, default=0),
        sa.Column('conversions_generated', sa.Integer, default=0),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_keywords_research', 'research_id'),
        sa.Index('idx_keywords_user', 'user_id'),
        sa.Index('idx_keywords_text', 'keyword_text'),
        sa.Index('idx_keywords_platform', 'platform'),
        sa.Index('idx_keywords_volume', 'search_volume_monthly'),
        sa.Index('idx_keywords_difficulty', 'keyword_difficulty'),
        sa.Index('idx_keywords_targeted', 'is_targeted'),
        sa.Index('idx_keywords_ranking', 'current_ranking_position'),
        sa.Index('idx_keywords_type', 'keyword_type'),
        
        # Full-text search
        sa.Index('idx_keywords_text_search', 'keyword_text', postgresql_using='gin'),
    )
    
    # Content Optimization Projects
    op.create_table(
        'content_optimization_projects',
        sa.Column('project_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seo_agents.agent_id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Project details
        sa.Column('project_name', sa.String(255), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),  # video, article, product_page, etc.
        sa.Column('target_platform', sa.String(100), nullable=False),
        sa.Column('content_url', sa.String(1000)),
        sa.Column('target_audience', postgresql.JSONB),
        
        # SEO goals and targets
        sa.Column('primary_keywords', postgresql.JSONB, nullable=False),
        sa.Column('secondary_keywords', postgresql.JSONB),
        sa.Column('target_ranking_positions', postgresql.JSONB),
        sa.Column('target_traffic_increase', sa.Float),
        sa.Column('target_conversion_rate', sa.Float),
        
        # Current state analysis
        sa.Column('baseline_rankings', postgresql.JSONB),
        sa.Column('baseline_traffic', sa.Integer),
        sa.Column('baseline_conversion_rate', sa.Float),
        sa.Column('baseline_engagement_metrics', postgresql.JSONB),
        sa.Column('current_seo_score', sa.Float),
        
        # Optimization strategy
        sa.Column('optimization_strategy', postgresql.JSONB, nullable=False),
        sa.Column('recommended_actions', postgresql.JSONB),
        sa.Column('priority_order', postgresql.JSONB),
        sa.Column('estimated_effort_hours', sa.Float),
        sa.Column('estimated_timeline_days', sa.Integer),
        
        # Content analysis
        sa.Column('content_analysis', postgresql.JSONB),
        sa.Column('keyword_density_analysis', postgresql.JSONB),
        sa.Column('content_structure_analysis', postgresql.JSONB),
        sa.Column('readability_score', sa.Float),
        sa.Column('semantic_analysis', postgresql.JSONB),
        
        # Technical SEO analysis
        sa.Column('technical_seo_issues', postgresql.JSONB),
        sa.Column('metadata_optimization', postgresql.JSONB),
        sa.Column('schema_markup_suggestions', postgresql.JSONB),
        sa.Column('internal_linking_opportunities', postgresql.JSONB),
        
        # Status and progress
        sa.Column('status', sa.String(50), default='planning', nullable=False),
        sa.Column('progress_percentage', sa.Float, default=0),
        sa.Column('actions_completed', sa.Integer, default=0),
        sa.Column('actions_total', sa.Integer),
        sa.Column('current_phase', sa.String(100)),
        
        # Results tracking
        sa.Column('ranking_improvements', postgresql.JSONB),
        sa.Column('traffic_improvement', sa.Float),
        sa.Column('conversion_improvement', sa.Float),
        sa.Column('engagement_improvement', postgresql.JSONB),
        sa.Column('roi_calculation', sa.Numeric(10, 2)),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        sa.Column('deadline', sa.TIMESTAMP(timezone=True)),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        
        # Indexes
        sa.Index('idx_optimization_projects_agent', 'agent_id'),
        sa.Index('idx_optimization_projects_user', 'user_id'),
        sa.Index('idx_optimization_projects_tenant', 'tenant_id'),
        sa.Index('idx_optimization_projects_status', 'status'),
        sa.Index('idx_optimization_projects_platform', 'target_platform'),
        sa.Index('idx_optimization_projects_created', 'created_at'),
        sa.Index('idx_optimization_projects_progress', 'progress_percentage'),
    )
    
    # Ranking Tracking and Monitoring
    op.create_table(
        'ranking_tracking',
        sa.Column('tracking_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seo_agents.agent_id'), nullable=False),
        sa.Column('keyword_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('keywords.keyword_id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_optimization_projects.project_id')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Tracking configuration
        sa.Column('tracking_frequency', sa.String(20), default='daily'),  # hourly, daily, weekly
        sa.Column('search_engine', sa.String(50), nullable=False),  # google, bing, youtube, etc.
        sa.Column('location', sa.String(100)),  # Geographic location for local SEO
        sa.Column('device_type', sa.String(20), default='desktop'),  # desktop, mobile, tablet
        sa.Column('language', sa.String(10), nullable=False),
        
        # Current ranking data
        sa.Column('current_position', sa.Integer),
        sa.Column('current_url', sa.String(1000)),
        sa.Column('current_title', sa.String(500)),
        sa.Column('current_meta_description', sa.String(500)),
        sa.Column('featured_snippet_present', sa.Boolean, default=False),
        sa.Column('serp_features', postgresql.JSONB),
        
        # Historical tracking
        sa.Column('position_history', postgresql.JSONB),  # Time-series data
        sa.Column('highest_position', sa.Integer),
        sa.Column('lowest_position', sa.Integer),
        sa.Column('average_position_30d', sa.Float),
        sa.Column('position_volatility', sa.Float),
        sa.Column('trending_direction', sa.String(20)),  # up, down, stable
        
        # SERP analysis
        sa.Column('serp_snapshot', postgresql.JSONB),
        sa.Column('competitor_positions', postgresql.JSONB),
        sa.Column('top_10_analysis', postgresql.JSONB),
        sa.Column('serp_changes_detected', postgresql.JSONB),
        
        # Performance correlation
        sa.Column('traffic_correlation', sa.Float),
        sa.Column('click_through_rate', sa.Float),
        sa.Column('impressions', sa.BigInteger),
        sa.Column('clicks', sa.BigInteger),
        sa.Column('conversion_rate', sa.Float),
        
        # Alerts and notifications
        sa.Column('alert_thresholds', postgresql.JSONB),
        sa.Column('alerts_triggered', postgresql.JSONB),
        sa.Column('notification_settings', postgresql.JSONB),
        
        # Status and metadata
        sa.Column('tracking_status', sa.String(50), default='active'),
        sa.Column('last_checked', sa.TIMESTAMP(timezone=True)),
        sa.Column('check_frequency_actual', sa.Integer),  # Minutes between checks
        sa.Column('data_accuracy_score', sa.Float),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_ranking_tracking_agent', 'agent_id'),
        sa.Index('idx_ranking_tracking_keyword', 'keyword_id'),
        sa.Index('idx_ranking_tracking_project', 'project_id'),
        sa.Index('idx_ranking_tracking_user', 'user_id'),
        sa.Index('idx_ranking_tracking_engine', 'search_engine'),
        sa.Index('idx_ranking_tracking_position', 'current_position'),
        sa.Index('idx_ranking_tracking_status', 'tracking_status'),
        sa.Index('idx_ranking_tracking_checked', 'last_checked'),
    )
    
    # Competitor Analysis
    op.create_table(
        'competitor_analysis',
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seo_agents.agent_id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_optimization_projects.project_id')),
        
        # Competitor identification
        sa.Column('competitor_url', sa.String(1000), nullable=False),
        sa.Column('competitor_name', sa.String(255)),
        sa.Column('competitor_type', sa.String(50)),  # direct, indirect, aspirational
        sa.Column('competitor_size', sa.String(20)),  # small, medium, large, enterprise
        sa.Column('industry_category', sa.String(100)),
        
        # SEO metrics
        sa.Column('domain_authority', sa.Float),
        sa.Column('page_authority', sa.Float),
        sa.Column('organic_traffic_estimate', sa.BigInteger),
        sa.Column('organic_keywords_count', sa.Integer),
        sa.Column('backlinks_count', sa.BigInteger),
        sa.Column('referring_domains_count', sa.Integer),
        
        # Content analysis
        sa.Column('content_strategy_analysis', postgresql.JSONB),
        sa.Column('top_performing_content', postgresql.JSONB),
        sa.Column('content_gaps_identified', postgresql.JSONB),
        sa.Column('content_frequency', sa.String(50)),
        sa.Column('content_types_used', postgresql.JSONB),
        
        # Keyword analysis
        sa.Column('shared_keywords', postgresql.JSONB),
        sa.Column('keyword_gaps', postgresql.JSONB),
        sa.Column('keyword_opportunities', postgresql.JSONB),
        sa.Column('ranking_overlaps', postgresql.JSONB),
        sa.Column('competitive_keywords', postgresql.JSONB),
        
        # Technical SEO analysis
        sa.Column('technical_seo_score', sa.Float),
        sa.Column('page_speed_score', sa.Float),
        sa.Column('mobile_friendliness_score', sa.Float),
        sa.Column('schema_markup_usage', postgresql.JSONB),
        sa.Column('internal_linking_strategy', postgresql.JSONB),
        
        # Social and engagement metrics
        sa.Column('social_media_presence', postgresql.JSONB),
        sa.Column('engagement_metrics', postgresql.JSONB),
        sa.Column('brand_mention_analysis', postgresql.JSONB),
        sa.Column('user_experience_score', sa.Float),
        
        # Strategic insights
        sa.Column('competitive_advantages', postgresql.JSONB),
        sa.Column('competitive_weaknesses', postgresql.JSONB),
        sa.Column('strategic_recommendations', postgresql.JSONB),
        sa.Column('threat_level', sa.String(20)),  # low, medium, high
        sa.Column('opportunity_score', sa.Float),
        
        # Monitoring and updates
        sa.Column('monitoring_frequency', sa.String(20), default='weekly'),
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True)),
        sa.Column('change_detection', postgresql.JSONB),
        sa.Column('alert_triggers', postgresql.JSONB),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('analysis_date', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_competitor_analysis_agent', 'agent_id'),
        sa.Index('idx_competitor_analysis_user', 'user_id'),
        sa.Index('idx_competitor_analysis_project', 'project_id'),
        sa.Index('idx_competitor_analysis_url', 'competitor_url'),
        sa.Index('idx_competitor_analysis_type', 'competitor_type'),
        sa.Index('idx_competitor_analysis_date', 'analysis_date'),
        sa.Index('idx_competitor_analysis_authority', 'domain_authority'),
    )
    
    # SEO Performance Analytics
    op.create_table(
        'seo_analytics',
        sa.Column('analytics_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seo_agents.agent_id')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('content_optimization_projects.project_id')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Time dimensions
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('hour', sa.Integer),  # 0-23 for hourly analytics
        sa.Column('period_type', sa.String(20), default='daily'),  # hourly, daily, weekly, monthly
        
        # Platform and search engine
        sa.Column('platform', sa.String(100), nullable=False),
        sa.Column('search_engine', sa.String(50)),
        sa.Column('device_type', sa.String(20)),
        sa.Column('geographic_region', sa.String(100)),
        
        # Ranking metrics
        sa.Column('average_ranking_position', sa.Float),
        sa.Column('keywords_in_top_10', sa.Integer, default=0),
        sa.Column('keywords_in_top_3', sa.Integer, default=0),
        sa.Column('featured_snippets_won', sa.Integer, default=0),
        sa.Column('ranking_improvements', sa.Integer, default=0),
        sa.Column('ranking_declines', sa.Integer, default=0),
        
        # Traffic metrics
        sa.Column('organic_traffic', sa.BigInteger, default=0),
        sa.Column('organic_impressions', sa.BigInteger, default=0),
        sa.Column('organic_clicks', sa.BigInteger, default=0),
        sa.Column('click_through_rate', sa.Float),
        sa.Column('average_session_duration', sa.Float),
        sa.Column('bounce_rate', sa.Float),
        
        # Conversion metrics
        sa.Column('conversions', sa.Integer, default=0),
        sa.Column('conversion_rate', sa.Float),
        sa.Column('revenue_attributed', sa.Numeric(12, 2), default=0),
        sa.Column('goal_completions', sa.Integer, default=0),
        sa.Column('lead_generation', sa.Integer, default=0),
        
        # Content performance
        sa.Column('content_engagement_score', sa.Float),
        sa.Column('social_shares', sa.Integer, default=0),
        sa.Column('backlinks_earned', sa.Integer, default=0),
        sa.Column('brand_mentions', sa.Integer, default=0),
        sa.Column('user_generated_content', sa.Integer, default=0),
        
        # Technical metrics
        sa.Column('page_speed_score', sa.Float),
        sa.Column('core_web_vitals_score', sa.Float),
        sa.Column('mobile_usability_score', sa.Float),
        sa.Column('indexing_status', postgresql.JSONB),
        sa.Column('crawl_errors', sa.Integer, default=0),
        
        # Competitive metrics
        sa.Column('competitive_visibility', sa.Float),
        sa.Column('share_of_voice', sa.Float),
        sa.Column('competitor_gap_analysis', postgresql.JSONB),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_seo_analytics_agent', 'agent_id'),
        sa.Index('idx_seo_analytics_project', 'project_id'),
        sa.Index('idx_seo_analytics_user', 'user_id'),
        sa.Index('idx_seo_analytics_date', 'date'),
        sa.Index('idx_seo_analytics_platform', 'platform'),
        sa.Index('idx_seo_analytics_period', 'period_type', 'date'),
        sa.Index('idx_seo_analytics_traffic', 'organic_traffic'),
        sa.Index('idx_seo_analytics_ranking', 'average_ranking_position'),
    )
    
    # Add foreign key constraints
    op.create_foreign_key('fk_keyword_research_agent', 'keyword_research', 'seo_agents', ['agent_id'], ['agent_id'])
    op.create_foreign_key('fk_keywords_research', 'keywords', 'keyword_research', ['research_id'], ['research_id'])
    op.create_foreign_key('fk_optimization_projects_agent', 'content_optimization_projects', 'seo_agents', ['agent_id'], ['agent_id'])
    op.create_foreign_key('fk_ranking_tracking_agent', 'ranking_tracking', 'seo_agents', ['agent_id'], ['agent_id'])
    op.create_foreign_key('fk_ranking_tracking_keyword', 'ranking_tracking', 'keywords', ['keyword_id'], ['keyword_id'])
    op.create_foreign_key('fk_ranking_tracking_project', 'ranking_tracking', 'content_optimization_projects', ['project_id'], ['project_id'])
    op.create_foreign_key('fk_competitor_analysis_agent', 'competitor_analysis', 'seo_agents', ['agent_id'], ['agent_id'])
    op.create_foreign_key('fk_competitor_analysis_project', 'competitor_analysis', 'content_optimization_projects', ['project_id'], ['project_id'])
    op.create_foreign_key('fk_seo_analytics_agent', 'seo_analytics', 'seo_agents', ['agent_id'], ['agent_id'])
    op.create_foreign_key('fk_seo_analytics_project', 'seo_analytics', 'content_optimization_projects', ['project_id'], ['project_id'])


def downgrade() -> None:
    """Downgrade: Drop SEO agent tables"""
    
    # Drop tables in reverse order to handle foreign key dependencies
    op.drop_table('seo_analytics')
    op.drop_table('competitor_analysis')
    op.drop_table('ranking_tracking')
    op.drop_table('content_optimization_projects')
    op.drop_table('keywords')
    op.drop_table('keyword_research')
    op.drop_table('seo_agents')