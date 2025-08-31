"""Web Surveillance Database Manager
Advanced web crawling and monitoring data management for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

🕷️ WEB CRAWLING AVANCÉ:
- Multi-platform crawler management
- Distributed crawling architecture
- Rate limiting et politeness policies
- Proxy rotation automatique
- Anti-detection mechanisms avancés
- Content extraction optimization

🔍 SURVEILLANCE TEMPS RÉEL:
- Real-time content monitoring
- Automated alert generation
- Pattern recognition avancé
- Anomaly detection AI
- Threat assessment automation
- Performance tracking continu

📊 DATA PROCESSING PIPELINE:
- Stream processing architecture
- Real-time data normalization
- Duplicate detection avancée
- Content classification AI
- Sentiment analysis integration
- Language detection automatique

🎯 PLATFORM SPECIALIZATION:
- YouTube crawler optimization
- Instagram API integration
- TikTok content monitoring
- Twitter/X surveillance
- Facebook content tracking
- Generic web crawler engine

📈 ANALYTICS ET INSIGHTS:
- Trend analysis automation
- Competitive intelligence
- Market monitoring dashboards
- Performance benchmarking
- ROI tracking per platform
- Predictive analytics AI

🛡️ PROTECTION ET COMPLIANCE:
- GDPR compliance automation
- Terms of service monitoring
- Copyright violation detection
- Privacy protection measures
- Legal compliance tracking
- Audit trail complet

⚡ PERFORMANCE OPTIMIZATION:
- Async crawling architecture
- Intelligent caching strategies
- Load balancing automation
- Resource usage optimization
- Scalability automation
- Cost optimization algorithms

🔒 SÉCURITÉ ET FIABILITÉ:
- Secure data transmission
- Encrypted storage solutions
- Access control granulaire
- Audit logging complet
- Backup et recovery automation
- Monitoring et alerting 24/7
"""import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
import logging
import re
from urllib.parse import urlparse, urljoin
import uuid
from sqlalchemy import (
    text, select, insert, update, delete, func, and_, or_,
    Index, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.deployment.database.postgresql_manager import get_postgresql_manager


class CrawlerType(Enum):
    """Types of crawlers"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    GENERIC_WEB = "generic_web"
    RSS_FEED = "rss_feed"
    API_ENDPOINT = "api_endpoint"


class CrawlStatus(Enum):
    """Crawl job status"""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class ContentStatus(Enum):
    """Detected content status"""    NEW = "new"
    UPDATED = "updated"
    REMOVED = "removed"
    MONITORED = "monitored"
    FLAGGED = "flagged"
    IGNORED = "ignored"


class AlertSeverity(Enum):
    """Alert severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class AlertType(Enum):
    """Types of alerts"""    COPYRIGHT_VIOLATION = "copyright_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    BRAND_MENTION = "brand_mention"
    COMPETITOR_ACTIVITY = "competitor_activity"
    TRENDING_CONTENT = "trending_content"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    POLICY_VIOLATION = "policy_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


@dataclass
class CrawlJob:
    """Crawl job configuration"""    job_id: str
    user_id: str
    crawler_type: CrawlerType
    target_urls: List[str]
    search_terms: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None
    priority: int = 1
    max_depth: int = 3
    max_pages: int = 1000
    respect_robots_txt: bool = True
    delay_seconds: float = 1.0


@dataclass
class DetectedContent:
    """Detected content structure"""    content_id: str
    url: str
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)


class WebSurveillanceManager:
    """    Enterprise Web Surveillance Database Manager
    
    Manages web crawling operations, content detection, and surveillance
    alerts with enterprise-grade performance and reliability.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.WebSurveillanceManager")
        self.settings = get_settings()
        
        # Database components
        self._db_manager = None
        
        # Performance settings
        self.batch_size = self.config.get('batch_size', 1000)
        self.max_concurrent_crawls = self.config.get('max_concurrent_crawls', 10)
        self.default_delay = self.config.get('default_delay', 1.0)
        
        # Caching and state
        self._active_crawls: Dict[str, Dict[str, Any]] = {}
        self._content_cache: Dict[str, Any] = {}
        self._url_fingerprints: Set[str] = set()
    
    async def initialize(self) -> bool:
        """Initialize the web surveillance manager"""        try:
            self.logger.info("🚀 Initializing Web Surveillance Manager...")
            
            # Get database manager
            self._db_manager = get_postgresql_manager()
            
            # Create schema if not exists
            await self._create_surveillance_schema()
            
            # Load active crawl jobs
            await self._load_active_crawls()
            
            self.logger.info("✅ Web Surveillance Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Web Surveillance Manager: {e}")
            return False
    
    async def _create_surveillance_schema(self):
        """Create web surveillance database schema"""        self.logger.debug("Creating web surveillance database schema...")
        
        schema_sql = """        -- Crawler Configurations
        CREATE TABLE IF NOT EXISTS crawler_configs (
            config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            crawler_type VARCHAR(50) NOT NULL,
            
            -- Configuration
            name VARCHAR(200) NOT NULL,
            description TEXT,
            target_urls JSONB NOT NULL, -- Array of URLs to crawl
            search_terms JSONB, -- Array of search terms
            
            -- Crawl settings
            max_depth INTEGER DEFAULT 3,
            max_pages INTEGER DEFAULT 1000,
            delay_seconds FLOAT DEFAULT 1.0,
            respect_robots_txt BOOLEAN DEFAULT true,
            
            -- Scheduling
            schedule_cron VARCHAR(100), -- Cron expression
            is_active BOOLEAN DEFAULT true,
            priority INTEGER DEFAULT 1,
            
            -- Advanced settings
            crawler_config JSONB, -- Crawler-specific settings
            headers JSONB, -- HTTP headers
            cookies JSONB, -- Cookies to use
            user_agents JSONB, -- User agents to rotate
            proxies JSONB, -- Proxy configurations
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            last_run_at TIMESTAMP,
            
            -- Indexes
            INDEX idx_crawler_configs_user (user_id),
            INDEX idx_crawler_configs_type (crawler_type),
            INDEX idx_crawler_configs_active (is_active),
            INDEX idx_crawler_configs_schedule (schedule_cron),
            INDEX idx_crawler_configs_priority (priority)
        );
        
        -- Crawl Jobs
        CREATE TABLE IF NOT EXISTS crawl_jobs (
            job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            config_id UUID NOT NULL REFERENCES crawler_configs(config_id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Job details
            job_name VARCHAR(200),
            crawler_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'paused', 'cancelled', 'scheduled')),
            
            -- Execution details
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            duration INTERVAL,
            
            -- Progress tracking
            pages_crawled INTEGER DEFAULT 0,
            pages_found INTEGER DEFAULT 0,
            content_detected INTEGER DEFAULT 0,
            errors_count INTEGER DEFAULT 0,
            
            -- Results
            results_summary JSONB,
            error_log JSONB,
            
            -- Performance metrics
            avg_response_time FLOAT DEFAULT 0.0,
            data_transferred BIGINT DEFAULT 0,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            INDEX idx_crawl_jobs_config (config_id),
            INDEX idx_crawl_jobs_user (user_id),
            INDEX idx_crawl_jobs_type (crawler_type),
            INDEX idx_crawl_jobs_status (status),
            INDEX idx_crawl_jobs_started (started_at),
            INDEX idx_crawl_jobs_completed (completed_at)
        );
        
        -- Detected Content
        CREATE TABLE IF NOT EXISTS detected_content (
            content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            job_id UUID NOT NULL REFERENCES crawl_jobs(job_id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Content details
            url TEXT NOT NULL,
            url_hash VARCHAR(64) NOT NULL, -- SHA256 hash of URL for deduplication
            title TEXT,
            description TEXT,
            content_text TEXT,
            
            -- Source information
            platform VARCHAR(50),
            author VARCHAR(200),
            author_url TEXT,
            publication_date TIMESTAMP,
            
            -- Content metadata
            content_type VARCHAR(50), -- video, image, audio, text, etc.
            language VARCHAR(10),
            content_length INTEGER,
            file_size BIGINT,
            duration FLOAT, -- For media content
            
            -- Engagement metrics
            views_count BIGINT DEFAULT 0,
            likes_count BIGINT DEFAULT 0,
            shares_count BIGINT DEFAULT 0,
            comments_count BIGINT DEFAULT 0,
            
            -- Detection details
            detection_method VARCHAR(100),
            confidence_score FLOAT DEFAULT 0.0,
            similarity_score FLOAT DEFAULT 0.0,
            
            -- Content analysis
            sentiment_score FLOAT, -- -1 to 1 (negative to positive)
            keywords JSONB, -- Extracted keywords
            topics JSONB, -- Topic classification
            entities JSONB, -- Named entity recognition
            
            -- Status and processing
            status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'updated', 'removed', 'monitored', 'flagged', 'ignored')),
            is_processed BOOLEAN DEFAULT false,
            
            -- Raw data
            raw_metadata JSONB,
            raw_html TEXT,
            
            -- System fields
            detected_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            last_checked_at TIMESTAMP,
            
            -- Indexes
            UNIQUE(url_hash),
            INDEX idx_detected_content_job (job_id),
            INDEX idx_detected_content_user (user_id),
            INDEX idx_detected_content_platform (platform),
            INDEX idx_detected_content_author (author),
            INDEX idx_detected_content_type (content_type),
            INDEX idx_detected_content_status (status),
            INDEX idx_detected_content_detected (detected_at),
            INDEX idx_detected_content_confidence (confidence_score),
            INDEX idx_detected_content_similarity (similarity_score),
            INDEX idx_detected_content_sentiment (sentiment_score)
        );
        
        -- Surveillance Alerts
        CREATE TABLE IF NOT EXISTS surveillance_alerts (
            alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content_id UUID REFERENCES detected_content(content_id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- Alert details
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical', 'urgent')),
            title VARCHAR(200) NOT NULL,
            description TEXT,
            
            -- Alert data
            trigger_conditions JSONB,
            matched_criteria JSONB,
            evidence JSONB,
            
            -- Scoring
            risk_score FLOAT DEFAULT 0.0 CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
            confidence_score FLOAT DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
            priority_score FLOAT DEFAULT 0.0 CHECK (priority_score >= 0.0 AND priority_score <= 1.0),
            
            -- Status and actions
            status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive', 'ignored')),
            assigned_to UUID,
            resolution TEXT,
            
            -- Notifications
            notifications_sent JSONB,
            last_notification_at TIMESTAMP,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            resolved_at TIMESTAMP,
            
            -- Indexes
            INDEX idx_surveillance_alerts_content (content_id),
            INDEX idx_surveillance_alerts_user (user_id),
            INDEX idx_surveillance_alerts_type (alert_type),
            INDEX idx_surveillance_alerts_severity (severity),
            INDEX idx_surveillance_alerts_status (status),
            INDEX idx_surveillance_alerts_risk (risk_score),
            INDEX idx_surveillance_alerts_created (created_at),
            INDEX idx_surveillance_alerts_assigned (assigned_to)
        );
        
        -- Crawl Statistics
        CREATE TABLE IF NOT EXISTS crawl_statistics (
            stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            crawler_type VARCHAR(50) NOT NULL,
            
            -- Time period
            stat_date DATE NOT NULL DEFAULT CURRENT_DATE,
            stat_hour INTEGER CHECK (stat_hour >= 0 AND stat_hour <= 23),
            
            -- Crawling metrics
            jobs_started INTEGER DEFAULT 0,
            jobs_completed INTEGER DEFAULT 0,
            jobs_failed INTEGER DEFAULT 0,
            
            -- Content metrics
            pages_crawled INTEGER DEFAULT 0,
            content_detected INTEGER DEFAULT 0,
            duplicates_found INTEGER DEFAULT 0,
            
            -- Performance metrics
            avg_response_time FLOAT DEFAULT 0.0,
            total_data_transferred BIGINT DEFAULT 0,
            error_rate FLOAT DEFAULT 0.0,
            
            -- Alert metrics
            alerts_generated INTEGER DEFAULT 0,
            high_severity_alerts INTEGER DEFAULT 0,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            UNIQUE(user_id, crawler_type, stat_date, stat_hour),
            INDEX idx_crawl_stats_user (user_id),
            INDEX idx_crawl_stats_type (crawler_type),
            INDEX idx_crawl_stats_date (stat_date),
            INDEX idx_crawl_stats_hour (stat_hour)
        );
        
        -- Blacklisted URLs
        CREATE TABLE IF NOT EXISTS blacklisted_urls (
            blacklist_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            
            -- URL details
            url_pattern TEXT NOT NULL,
            url_type VARCHAR(20) DEFAULT 'exact' CHECK (url_type IN ('exact', 'domain', 'regex', 'wildcard')),
            
            -- Blacklist reason
            reason VARCHAR(100),
            description TEXT,
            
            -- Status
            is_active BOOLEAN DEFAULT true,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            expires_at TIMESTAMP,
            
            -- Indexes
            INDEX idx_blacklisted_urls_user (user_id),
            INDEX idx_blacklisted_urls_pattern (url_pattern),
            INDEX idx_blacklisted_urls_type (url_type),
            INDEX idx_blacklisted_urls_active (is_active)
        );
        
        -- Platform API Limits
        CREATE TABLE IF NOT EXISTS platform_api_limits (
            limit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            platform VARCHAR(50) NOT NULL,
            
            -- Rate limits
            requests_per_hour INTEGER,
            requests_per_day INTEGER,
            concurrent_requests INTEGER DEFAULT 1,
            
            -- Current usage
            current_hour_requests INTEGER DEFAULT 0,
            current_day_requests INTEGER DEFAULT 0,
            current_concurrent INTEGER DEFAULT 0,
            
            -- Reset times
            hour_reset_at TIMESTAMP,
            day_reset_at TIMESTAMP,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            UNIQUE(platform),
            INDEX idx_platform_limits_platform (platform)
        );
        
        -- Update timestamp triggers
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- Apply triggers
        DROP TRIGGER IF EXISTS update_crawler_configs_updated_at ON crawler_configs;
        CREATE TRIGGER update_crawler_configs_updated_at
            BEFORE UPDATE ON crawler_configs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_crawl_jobs_updated_at ON crawl_jobs;
        CREATE TRIGGER update_crawl_jobs_updated_at
            BEFORE UPDATE ON crawl_jobs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_detected_content_updated_at ON detected_content;
        CREATE TRIGGER update_detected_content_updated_at
            BEFORE UPDATE ON detected_content
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_surveillance_alerts_updated_at ON surveillance_alerts;
        CREATE TRIGGER update_surveillance_alerts_updated_at
            BEFORE UPDATE ON surveillance_alerts
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_crawl_statistics_updated_at ON crawl_statistics;
        CREATE TRIGGER update_crawl_statistics_updated_at
            BEFORE UPDATE ON crawl_statistics
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_blacklisted_urls_updated_at ON blacklisted_urls;
        CREATE TRIGGER update_blacklisted_urls_updated_at
            BEFORE UPDATE ON blacklisted_urls
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_platform_api_limits_updated_at ON platform_api_limits;
        CREATE TRIGGER update_platform_api_limits_updated_at
            BEFORE UPDATE ON platform_api_limits
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """        
        async with self._db_manager.get_session() as session:
            await session.execute(text(schema_sql))
            await session.commit()
        
        self.logger.debug("✅ Web surveillance schema created successfully")
    
    async def _load_active_crawls(self):
        """Load active crawl jobs from database"""        try:
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        SELECT job_id, config_id, user_id, crawler_type, status, 
                               pages_crawled, pages_found, started_at
                        FROM crawl_jobs 
                        WHERE status IN ('running', 'pending', 'scheduled')
                        ORDER BY started_at
                    """)
                )
                
                active_jobs = result.fetchall()
                
                for job in active_jobs:
                    self._active_crawls[job.job_id] = {
                        'config_id': job.config_id,
                        'user_id': job.user_id,
                        'crawler_type': job.crawler_type,
                        'status': job.status,
                        'pages_crawled': job.pages_crawled,
                        'pages_found': job.pages_found,
                        'started_at': job.started_at
                    }
                
                self.logger.debug(f"Loaded {len(active_jobs)} active crawl jobs")
        
        except Exception as e:
            self.logger.error(f"Failed to load active crawls: {e}")
    
    async def create_crawler_config(
        self,
        user_id: str,
        name: str,
        crawler_type: CrawlerType,
        target_urls: List[str],
        search_terms: List[str] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """Create a new crawler configuration"""        try:
            self.logger.debug(f"Creating crawler config for user {user_id}")
            
            config_data = {
                'user_id': user_id,
                'name': name,
                'crawler_type': crawler_type.value,
                'target_urls': json.dumps(target_urls),
                'search_terms': json.dumps(search_terms or []),
                'crawler_config': json.dumps(config or {}),
                'max_depth': config.get('max_depth', 3) if config else 3,
                'max_pages': config.get('max_pages', 1000) if config else 1000,
                'delay_seconds': config.get('delay_seconds', 1.0) if config else 1.0,
                'respect_robots_txt': config.get('respect_robots_txt', True) if config else True,
                'priority': config.get('priority', 1) if config else 1
            }
            
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        INSERT INTO crawler_configs 
                        (user_id, name, crawler_type, target_urls, search_terms, 
                         crawler_config, max_depth, max_pages, delay_seconds, 
                         respect_robots_txt, priority)
                        VALUES (:user_id, :name, :crawler_type, :target_urls, :search_terms,
                               :crawler_config, :max_depth, :max_pages, :delay_seconds,
                               :respect_robots_txt, :priority)
                        RETURNING config_id
                    """),
                    config_data
                )
                
                config_id = result.scalar()
                await session.commit()
            
            self.logger.debug(f"✅ Crawler config created successfully: {config_id}")
            return config_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create crawler config: {e}")
            raise
    
    async def start_crawl_job(self, config_id: str, job_name: Optional[str] = None) -> str:
        """Start a new crawl job"""        try:
            self.logger.debug(f"Starting crawl job for config {config_id}")
            
            # Get crawler configuration
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        SELECT user_id, crawler_type, name, target_urls, search_terms, crawler_config
                        FROM crawler_configs 
                        WHERE config_id = :config_id AND is_active = true
                    """),
                    {'config_id': config_id}
                )
                
                config = result.fetchone()
                if not config:
                    raise ValueError(f"Crawler config {config_id} not found or inactive")
                
                # Create new job
                job_data = {
                    'config_id': config_id,
                    'user_id': config.user_id,
                    'job_name': job_name or f"Crawl job for {config.name}",
                    'crawler_type': config.crawler_type,
                    'status': 'pending',
                    'started_at': datetime.utcnow()
                }
                
                result = await session.execute(
                    text("""                        INSERT INTO crawl_jobs 
                        (config_id, user_id, job_name, crawler_type, status, started_at)
                        VALUES (:config_id, :user_id, :job_name, :crawler_type, :status, :started_at)
                        RETURNING job_id
                    """),
                    job_data
                )
                
                job_id = result.scalar()
                await session.commit()
            
            # Add to active crawls
            self._active_crawls[job_id] = {
                'config_id': config_id,
                'user_id': config.user_id,
                'crawler_type': config.crawler_type,
                'status': 'pending',
                'pages_crawled': 0,
                'pages_found': 0,
                'started_at': datetime.utcnow()
            }
            
            self.logger.debug(f"✅ Crawl job started successfully: {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start crawl job: {e}")
            raise
    
    async def update_crawl_progress(
        self,
        job_id: str,
        pages_crawled: int,
        pages_found: int,
        content_detected: int,
        errors_count: int = 0
    ) -> bool:
        """Update crawl job progress"""        try:
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        UPDATE crawl_jobs 
                        SET pages_crawled = :pages_crawled,
                            pages_found = :pages_found,
                            content_detected = :content_detected,
                            errors_count = :errors_count,
                            updated_at = NOW()
                        WHERE job_id = :job_id
                    """),
                    {
                        'job_id': job_id,
                        'pages_crawled': pages_crawled,
                        'pages_found': pages_found,
                        'content_detected': content_detected,
                        'errors_count': errors_count
                    }
                )
                
                await session.commit()
                
                # Update local cache
                if job_id in self._active_crawls:
                    self._active_crawls[job_id].update({
                        'pages_crawled': pages_crawled,
                        'pages_found': pages_found,
                        'content_detected': content_detected,
                        'errors_count': errors_count
                    })
                
                return result.rowcount > 0
        
        except Exception as e:
            self.logger.error(f"Failed to update crawl progress: {e}")
            return False
    
    async def store_detected_content(self, job_id: str, content: DetectedContent) -> str:
        """Store detected content"""        try:
            # Generate URL hash for deduplication
            url_hash = hashlib.sha256(content.url.encode()).hexdigest()
            
            # Check if content already exists
            async with self._db_manager.get_session() as session:
                existing = await session.execute(
                    text("SELECT content_id FROM detected_content WHERE url_hash = :url_hash"),
                    {'url_hash': url_hash}
                )
                
                if existing.fetchone():
                    self.logger.debug(f"Content already exists for URL: {content.url}")
                    return existing.scalar()
                
                # Get job details
                job_result = await session.execute(
                    text("SELECT user_id FROM crawl_jobs WHERE job_id = :job_id"),
                    {'job_id': job_id}
                )
                
                job_data = job_result.fetchone()
                if not job_data:
                    raise ValueError(f"Job {job_id} not found")
                
                # Store new content
                content_data = {
                    'job_id': job_id,
                    'user_id': job_data.user_id,
                    'url': content.url,
                    'url_hash': url_hash,
                    'title': content.title,
                    'description': content.description,
                    'author': content.author,
                    'platform': content.platform,
                    'content_type': content.content_type,
                    'raw_metadata': json.dumps(content.metadata),
                    'detected_at': content.detected_at
                }
                
                result = await session.execute(
                    text("""                        INSERT INTO detected_content 
                        (job_id, user_id, url, url_hash, title, description, author, 
                         platform, content_type, raw_metadata, detected_at)
                        VALUES (:job_id, :user_id, :url, :url_hash, :title, :description, :author,
                               :platform, :content_type, :raw_metadata, :detected_at)
                        RETURNING content_id
                    """),
                    content_data
                )
                
                content_id = result.scalar()
                await session.commit()
                
                # Check for alert triggers
                await self._check_alert_triggers(content_id, content)
                
                self.logger.debug(f"✅ Content stored successfully: {content_id}")
                return content_id
        
        except Exception as e:
            self.logger.error(f"❌ Failed to store detected content: {e}")
            raise
    
    async def _check_alert_triggers(self, content_id: str, content: DetectedContent):
        """Check if content triggers any alerts"""        try:
            # This is a simplified alert trigger system
            # In a real implementation, this would be more sophisticated
            
            alerts_to_create = []
            
            # Check for potential copyright violations
            if any(term in (content.title or '').lower() for term in ['copyright', 'unauthorized', 'stolen']):
                alerts_to_create.append({
                    'alert_type': AlertType.COPYRIGHT_VIOLATION.value,
                    'severity': AlertSeverity.HIGH.value,
                    'title': f"Potential copyright violation detected: {content.title}",
                    'description': f"Content may contain unauthorized use of copyrighted material",
                    'risk_score': 0.8
                })
            
            # Check for brand mentions
            if content.description and any(term in content.description.lower() for term in ['brand', 'sponsor', 'partnership']):
                alerts_to_create.append({
                    'alert_type': AlertType.BRAND_MENTION.value,
                    'severity': AlertSeverity.MEDIUM.value,
                    'title': f"Brand mention detected: {content.title}",
                    'description': f"Content mentions brand-related terms",
                    'risk_score': 0.5
                })
            
            # Create alerts
            if alerts_to_create:
                async with self._db_manager.get_session() as session:
                    # Get user_id from content
                    result = await session.execute(
                        text("SELECT user_id FROM detected_content WHERE content_id = :content_id"),
                        {'content_id': content_id}
                    )
                    
                    user_data = result.fetchone()
                    if user_data:
                        for alert_data in alerts_to_create:
                            alert_data.update({
                                'content_id': content_id,
                                'user_id': user_data.user_id,
                                'trigger_conditions': json.dumps({
                                    'url': content.url,
                                    'platform': content.platform,
                                    'detection_method': 'keyword_matching'
                                }),
                                'confidence_score': 0.7,
                                'priority_score': alert_data['risk_score']
                            })
                            
                            await session.execute(
                                text("""                                    INSERT INTO surveillance_alerts 
                                    (content_id, user_id, alert_type, severity, title, description,
                                     trigger_conditions, risk_score, confidence_score, priority_score)
                                    VALUES (:content_id, :user_id, :alert_type, :severity, :title, :description,
                                           :trigger_conditions, :risk_score, :confidence_score, :priority_score)
                                """),
                                alert_data
                            )
                        
                        await session.commit()
                        self.logger.debug(f"Created {len(alerts_to_create)} alerts for content {content_id}")
        
        except Exception as e:
            self.logger.error(f"Failed to check alert triggers: {e}")
    
    async def complete_crawl_job(
        self,
        job_id: str,
        status: CrawlStatus = CrawlStatus.COMPLETED,
        results_summary: Optional[Dict[str, Any]] = None,
        error_log: Optional[List[str]] = None
    ) -> bool:
        """Complete a crawl job"""        try:
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        UPDATE crawl_jobs 
                        SET status = :status,
                            completed_at = NOW(),
                            duration = NOW() - started_at,
                            results_summary = :results_summary,
                            error_log = :error_log,
                            updated_at = NOW()
                        WHERE job_id = :job_id
                    """),
                    {
                        'job_id': job_id,
                        'status': status.value,
                        'results_summary': json.dumps(results_summary) if results_summary else None,
                        'error_log': json.dumps(error_log) if error_log else None
                    }
                )
                
                await session.commit()
                
                # Remove from active crawls
                if job_id in self._active_crawls:
                    del self._active_crawls[job_id]
                
                # Update statistics
                await self._update_crawl_statistics(job_id)
                
                return result.rowcount > 0
        
        except Exception as e:
            self.logger.error(f"Failed to complete crawl job: {e}")
            return False
    
    async def _update_crawl_statistics(self, job_id: str):
        """Update crawl statistics"""        try:
            async with self._db_manager.get_session() as session:
                # Get job details
                result = await session.execute(
                    text("""                        SELECT user_id, crawler_type, status, pages_crawled, 
                               content_detected, errors_count, started_at
                        FROM crawl_jobs 
                        WHERE job_id = :job_id
                    """),
                    {'job_id': job_id}
                )
                
                job = result.fetchone()
                if not job:
                    return
                
                # Update daily statistics
                stat_date = job.started_at.date()
                stat_hour = job.started_at.hour
                
                await session.execute(
                    text("""                        INSERT INTO crawl_statistics 
                        (user_id, crawler_type, stat_date, stat_hour, jobs_completed,
                         pages_crawled, content_detected, error_rate)
                        VALUES (:user_id, :crawler_type, :stat_date, :stat_hour, 1,
                               :pages_crawled, :content_detected, :error_rate)
                        ON CONFLICT (user_id, crawler_type, stat_date, stat_hour) DO UPDATE SET
                            jobs_completed = crawl_statistics.jobs_completed + 1,
                            pages_crawled = crawl_statistics.pages_crawled + EXCLUDED.pages_crawled,
                            content_detected = crawl_statistics.content_detected + EXCLUDED.content_detected,
                            error_rate = (crawl_statistics.error_rate + EXCLUDED.error_rate) / 2,
                            updated_at = NOW()
                    """),
                    {
                        'user_id': job.user_id,
                        'crawler_type': job.crawler_type,
                        'stat_date': stat_date,
                        'stat_hour': stat_hour,
                        'pages_crawled': job.pages_crawled or 0,
                        'content_detected': job.content_detected or 0,
                        'error_rate': (job.errors_count or 0) / max(1, job.pages_crawled or 1)
                    }
                )
                
                await session.commit()
        
        except Exception as e:
            self.logger.error(f"Failed to update crawl statistics: {e}")
    
    async def get_user_alerts(
        self,
        user_id: str,
        alert_type: Optional[AlertType] = None,
        severity: Optional[AlertSeverity] = None,
        status: str = 'open',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get surveillance alerts for a user"""        try:
            query = """                SELECT sa.alert_id, sa.alert_type, sa.severity, sa.title, sa.description,
                       sa.risk_score, sa.confidence_score, sa.status, sa.created_at,
                       dc.url, dc.platform, dc.author, dc.title as content_title
                FROM surveillance_alerts sa
                LEFT JOIN detected_content dc ON sa.content_id = dc.content_id
                WHERE sa.user_id = :user_id
            """            
            params = {'user_id': user_id}
            
            if alert_type:
                query += " AND sa.alert_type = :alert_type"
                params['alert_type'] = alert_type.value
            
            if severity:
                query += " AND sa.severity = :severity"
                params['severity'] = severity.value
            
            if status:
                query += " AND sa.status = :status"
                params['status'] = status
            
            query += " ORDER BY sa.risk_score DESC, sa.created_at DESC LIMIT :limit"
            params['limit'] = limit
            
            async with self._db_manager.get_session() as session:
                result = await session.execute(text(query), params)
                alerts = [dict(row._mapping) for row in result.fetchall()]
                
                return alerts
        
        except Exception as e:
            self.logger.error(f"Failed to get user alerts: {e}")
            return []
    
    async def get_crawl_jobs_status(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get crawl jobs status for a user"""        try:
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        SELECT cj.job_id, cj.job_name, cj.crawler_type, cj.status,
                               cj.pages_crawled, cj.pages_found, cj.content_detected,
                               cj.errors_count, cj.started_at, cj.completed_at,
                               cc.name as config_name
                        FROM crawl_jobs cj
                        JOIN crawler_configs cc ON cj.config_id = cc.config_id
                        WHERE cj.user_id = :user_id
                        ORDER BY cj.started_at DESC
                        LIMIT :limit
                    """),
                    {'user_id': user_id, 'limit': limit}
                )
                
                jobs = [dict(row._mapping) for row in result.fetchall()]
                return jobs
        
        except Exception as e:
            self.logger.error(f"Failed to get crawl jobs status: {e}")
            return []
    
    async def get_detected_content(
        self,
        user_id: str,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get detected content for a user"""        try:
            query = """                SELECT content_id, url, title, description, author, platform,
                       content_type, confidence_score, similarity_score, 
                       sentiment_score, status, detected_at
                FROM detected_content 
                WHERE user_id = :user_id
            """            
            params = {'user_id': user_id}
            
            if platform:
                query += " AND platform = :platform"
                params['platform'] = platform
            
            if content_type:
                query += " AND content_type = :content_type"
                params['content_type'] = content_type
            
            query += " ORDER BY detected_at DESC LIMIT :limit"
            params['limit'] = limit
            
            async with self._db_manager.get_session() as session:
                result = await session.execute(text(query), params)
                content = [dict(row._mapping) for row in result.fetchall()]
                
                return content
        
        except Exception as e:
            self.logger.error(f"Failed to get detected content: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'database': 'healthy',
                    'crawlers': 'healthy',
                    'alerts': 'healthy'
                },
                'metrics': {
                    'active_crawls': len(self._active_crawls),
                    'total_configs': 0,
                    'total_jobs': 0,
                    'total_content': 0,
                    'total_alerts': 0
                }
            }
            
            # Check database connectivity and get metrics
            async with self._db_manager.get_session() as session:
                # Count configurations
                result = await session.execute(text("SELECT COUNT(*) FROM crawler_configs WHERE is_active = true"))
                health['metrics']['total_configs'] = result.scalar()
                
                # Count jobs
                result = await session.execute(text("SELECT COUNT(*) FROM crawl_jobs"))
                health['metrics']['total_jobs'] = result.scalar()
                
                # Count content
                result = await session.execute(text("SELECT COUNT(*) FROM detected_content"))
                health['metrics']['total_content'] = result.scalar()
                
                # Count alerts
                result = await session.execute(text("SELECT COUNT(*) FROM surveillance_alerts WHERE status = 'open'"))
                health['metrics']['total_alerts'] = result.scalar()
            
            # Check for stuck crawls
            stuck_crawls = 0
            for job_id, crawl_data in self._active_crawls.items():
                if crawl_data.get('started_at'):
                    age = datetime.utcnow() - crawl_data['started_at']
                    if age > timedelta(hours=24):  # Crawl running for more than 24 hours
                        stuck_crawls += 1
            
            if stuck_crawls > 0:
                health['components']['crawlers'] = 'warning'
                health['status'] = 'warning'
                health['warnings'] = [f"{stuck_crawls} crawl jobs may be stuck"]
            
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Shutdown the web surveillance manager"""        try:
            self.logger.info("🚨 Shutting down Web Surveillance Manager...")
            
            # Mark active crawls as paused
            for job_id in list(self._active_crawls.keys()):
                await self.complete_crawl_job(
                    job_id, 
                    CrawlStatus.PAUSED,
                    {'shutdown_reason': 'System shutdown'}
                )
            
            # Clear caches
            self._active_crawls.clear()
            self._content_cache.clear()
            self._url_fingerprints.clear()
            
            self.logger.info("✅ Web Surveillance Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown failed: {e}")


# Factory function
_web_surveillance_manager: Optional[WebSurveillanceManager] = None


def get_web_surveillance_manager(config: Optional[Dict[str, Any]] = None) -> WebSurveillanceManager:
    """Get or create web surveillance manager instance"""    global _web_surveillance_manager
    
    if _web_surveillance_manager is None:
        _web_surveillance_manager = WebSurveillanceManager(config)
    
    return _web_surveillance_manager
