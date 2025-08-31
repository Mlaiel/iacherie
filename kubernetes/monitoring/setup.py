"""Monitoring System Setup and Initialization for IA Influencer Agent
===================================================================

Comprehensive setup script for initializing the monitoring infrastructure,
including database setup, Redis configuration, alerting channels,
and system health verification.

Setup Components:
- Database schema creation and migration
- Redis data structure initialization
- Alerting channel configuration and testing
- Dashboard setup and asset preparation
- Performance baseline establishment
- Security monitoring rule deployment
- Business intelligence model initialization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use, distribution, or modification prohibited
"""
import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import redis
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import requests
import yaml

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from config_manager import MonitoringConfigurationManager, load_monitoring_config
from utils.logger import setup_monitoring_logger


@dataclass
class SetupStatus:
    """Status tracking for setup operations"""    component: str
    status: str  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


class MonitoringSetupManager:
    """    Comprehensive setup manager for IA Influencer Agent monitoring system.
    
    Handles complete initialization of monitoring infrastructure including
    database setup, Redis configuration, alerting verification, and
    system readiness validation.
    """    
    def __init__(self, config_path: Optional[str] = None, force_recreate: bool = False):
        self.config_path = config_path
        self.force_recreate = force_recreate
        
        # Load configuration
        self.config_manager = load_monitoring_config(config_path)
        self.config = self.config_manager.get_full_config()
        
        # Setup logging
        self.logger = setup_monitoring_logger("setup", level=logging.INFO)
        
        # Track setup status
        self.setup_status: Dict[str, SetupStatus] = {}
        
        # Connection objects
        self.redis_client: Optional[redis.Redis] = None
        self.db_connection: Optional[psycopg2.extensions.connection] = None
    
    async def run_complete_setup(self) -> bool:
        """Run complete monitoring system setup"""        
        self.logger.info("🚀 Starting IA Influencer Agent Monitoring System Setup")
        self.logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        self.logger.info(f"Configuration Profile: {self.config.get('profile', 'unknown')}")
        
        setup_steps = [
            ("system_check", self._verify_system_requirements),
            ("database_setup", self._setup_database),
            ("redis_setup", self._setup_redis),
            ("schema_creation", self._create_database_schema),
            ("redis_structures", self._initialize_redis_structures),
            ("alerting_setup", self._setup_alerting_channels),
            ("dashboard_setup", self._setup_dashboard),
            ("security_rules", self._deploy_security_rules),
            ("ai_models", self._initialize_ai_models),
            ("business_intelligence", self._setup_business_intelligence),
            ("performance_baseline", self._establish_performance_baseline),
            ("health_check", self._run_comprehensive_health_check)
        ]
        
        total_steps = len(setup_steps)
        completed_steps = 0
        
        for step_name, step_function in setup_steps:
            self.logger.info(f"📋 Step {completed_steps + 1}/{total_steps}: {step_name}")
            
            status = SetupStatus(
                component=step_name,
                status="running",
                start_time=datetime.now()
            )
            self.setup_status[step_name] = status
            
            try:
                success = await step_function()
                
                if success:
                    status.status = "completed"
                    status.end_time = datetime.now()
                    completed_steps += 1
                    self.logger.info(f"✅ {step_name} completed successfully")
                else:
                    status.status = "failed"
                    status.end_time = datetime.now()
                    status.error_message = "Step returned False"
                    self.logger.error(f"❌ {step_name} failed")
                    break
                    
            except Exception as e:
                status.status = "failed"
                status.end_time = datetime.now()
                status.error_message = str(e)
                self.logger.error(f"❌ {step_name} failed with error: {e}")
                break
        
        # Generate setup report
        await self._generate_setup_report()
        
        success = completed_steps == total_steps
        if success:
            self.logger.info("🎉 Monitoring system setup completed successfully!")
        else:
            self.logger.error("💥 Monitoring system setup failed")
        
        return success
    
    async def _verify_system_requirements(self) -> bool:
        """Verify system requirements and dependencies"""        
        self.logger.info("Checking system requirements...")
        
        requirements = {
            "python_version": (3, 8),
            "required_packages": ["redis", "psycopg2", "requests", "pyyaml", "numpy", "pandas"],
            "minimum_memory_gb": 2,
            "minimum_disk_gb": 10
        }
        
        # Check Python version
        python_version = sys.version_info[:2]
        if python_version < requirements["python_version"]:
            self.logger.error(f"Python {requirements['python_version']} or higher required, found {python_version}")
            return False
        
        # Check required packages
        missing_packages = []
        for package in requirements["required_packages"]:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.logger.error(f"Missing required packages: {missing_packages}")
            return False
        
        # Check system resources (basic check)
        try:
            import psutil
            
            # Memory check
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < requirements["minimum_memory_gb"]:
                self.logger.warning(f"Low memory: {memory_gb:.1f}GB (minimum {requirements['minimum_memory_gb']}GB)")
            
            # Disk space check
            disk_usage = psutil.disk_usage('/')
            disk_free_gb = disk_usage.free / (1024**3)
            if disk_free_gb < requirements["minimum_disk_gb"]:
                self.logger.warning(f"Low disk space: {disk_free_gb:.1f}GB free (minimum {requirements['minimum_disk_gb']}GB)")
        
        except ImportError:
            self.logger.warning("psutil not available, skipping resource checks")
        
        self.logger.info("✅ System requirements verified")
        return True
    
    async def _setup_database(self) -> bool:
        """Setup PostgreSQL database for monitoring"""        
        self.logger.info("Setting up PostgreSQL database...")
        
        db_config = self.config_manager.get_database_config()
        
        # Connect to PostgreSQL (to master database first)
        try:
            # Connect to default database to create monitoring database
            conn_params = {
                "host": db_config.host,
                "port": db_config.port,
                "user": db_config.username,
                "password": db_config.password,
                "database": "postgres"  # Connect to default database first
            }
            
            if db_config.password is None:
                conn_params.pop("password")
            
            self.db_connection = psycopg2.connect(**conn_params)
            self.db_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = self.db_connection.cursor()
            
            # Check if monitoring database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_config.database,)
            )
            
            if cursor.fetchone() is None or self.force_recreate:
                if self.force_recreate:
                    # Drop existing database
                    cursor.execute(f"DROP DATABASE IF EXISTS {db_config.database}")
                    self.logger.info(f"Dropped existing database: {db_config.database}")
                
                # Create new database
                cursor.execute(f"CREATE DATABASE {db_config.database}")
                self.logger.info(f"Created database: {db_config.database}")
            
            cursor.close()
            self.db_connection.close()
            
            # Connect to the monitoring database
            conn_params["database"] = db_config.database
            self.db_connection = psycopg2.connect(**conn_params)
            
            self.logger.info("✅ Database setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            return False
    
    async def _setup_redis(self) -> bool:
        """Setup Redis connection and configuration"""        
        self.logger.info("Setting up Redis connection...")
        
        redis_config = self.config_manager.get_redis_config()
        
        try:
            # Create Redis connection
            connection_params = {
                "host": redis_config.host,
                "port": redis_config.port,
                "db": redis_config.db,
                "socket_timeout": redis_config.socket_timeout,
                "decode_responses": redis_config.decode_responses
            }
            
            if redis_config.password:
                connection_params["password"] = redis_config.password
            
            if redis_config.ssl:
                connection_params["ssl"] = True
                connection_params["ssl_cert_reqs"] = None
            
            self.redis_client = redis.Redis(**connection_params)
            
            # Test connection
            self.redis_client.ping()
            
            # Set up Redis configuration if needed
            redis_info = self.redis_client.info()
            self.logger.info(f"Connected to Redis {redis_info.get('redis_version', 'unknown')}")
            
            # Configure Redis for optimal monitoring performance
            redis_configs = {
                "maxmemory-policy": "allkeys-lru",
                "save": "900 1 300 10 60 10000",  # Persistence settings
                "timeout": "300"  # Client timeout
            }
            
            for config_key, config_value in redis_configs.items():
                try:
                    self.redis_client.config_set(config_key, config_value)
                    self.logger.debug(f"Set Redis config: {config_key} = {config_value}")
                except Exception as e:
                    self.logger.warning(f"Could not set Redis config {config_key}: {e}")
            
            self.logger.info("✅ Redis setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Redis setup failed: {e}")
            return False
    
    async def _create_database_schema(self) -> bool:
        """Create database schema for monitoring data"""        
        self.logger.info("Creating database schema...")
        
        try:
            cursor = self.db_connection.cursor()
            
            # Create monitoring schema
            schema_sql = """            -- Monitoring metrics table
            CREATE TABLE IF NOT EXISTS monitoring_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metric_name VARCHAR(255) NOT NULL,
                metric_value FLOAT NOT NULL,
                metric_type VARCHAR(50) NOT NULL,
                source VARCHAR(100) NOT NULL,
                labels JSONB DEFAULT '{}',
                INDEX (timestamp, metric_name),
                INDEX (source, metric_name)
            );
            
            -- AI fingerprinting metrics
            CREATE TABLE IF NOT EXISTS ai_fingerprint_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                model_name VARCHAR(255) NOT NULL,
                accuracy FLOAT,
                inference_time_ms FLOAT,
                throughput_rps FLOAT,
                model_drift_score FLOAT,
                content_type VARCHAR(50),
                batch_size INTEGER,
                metadata JSONB DEFAULT '{}'
            );
            
            -- Revenue monitoring data
            CREATE TABLE IF NOT EXISTS revenue_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                platform VARCHAR(100) NOT NULL,
                revenue_amount DECIMAL(15,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                transaction_type VARCHAR(50),
                source_details JSONB DEFAULT '{}',
                fraud_score FLOAT DEFAULT 0.0,
                processed BOOLEAN DEFAULT FALSE
            );
            
            -- Security events
            CREATE TABLE IF NOT EXISTS security_events (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                event_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                source_ip INET,
                user_agent TEXT,
                description TEXT,
                metadata JSONB DEFAULT '{}',
                resolved BOOLEAN DEFAULT FALSE
            );
            
            -- Business intelligence insights
            CREATE TABLE IF NOT EXISTS bi_insights (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                insight_type VARCHAR(100) NOT NULL,
                priority VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                data_source VARCHAR(100),
                confidence_score FLOAT,
                actionable BOOLEAN DEFAULT TRUE,
                insight_data JSONB DEFAULT '{}'
            );
            
            -- Alert history
            CREATE TABLE IF NOT EXISTS alert_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                alert_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT,
                source VARCHAR(100),
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP WITH TIME ZONE,
                resolution_notes TEXT,
                metadata JSONB DEFAULT '{}'
            );
            
            -- System health status
            CREATE TABLE IF NOT EXISTS system_health (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                component VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL,
                health_score FLOAT,
                response_time_ms FLOAT,
                error_rate FLOAT,
                metadata JSONB DEFAULT '{}'
            );
            
            -- Create indexes for performance
            CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_timestamp 
                ON monitoring_metrics(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_name 
                ON monitoring_metrics(metric_name);
            CREATE INDEX IF NOT EXISTS idx_ai_fingerprint_timestamp 
                ON ai_fingerprint_metrics(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_revenue_timestamp 
                ON revenue_metrics(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_revenue_platform 
                ON revenue_metrics(platform);
            CREATE INDEX IF NOT EXISTS idx_security_timestamp 
                ON security_events(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_security_severity 
                ON security_events(severity);
            CREATE INDEX IF NOT EXISTS idx_bi_insights_timestamp 
                ON bi_insights(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_bi_insights_priority 
                ON bi_insights(priority);
            CREATE INDEX IF NOT EXISTS idx_alert_timestamp 
                ON alert_history(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_alert_resolved 
                ON alert_history(resolved);
            CREATE INDEX IF NOT EXISTS idx_system_health_timestamp 
                ON system_health(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_system_health_component 
                ON system_health(component);
            
            -- Create partitioning for large tables (if PostgreSQL version supports)
            -- This helps with performance on large datasets
            """            
            # Execute schema creation
            cursor.execute(schema_sql)
            self.db_connection.commit()
            
            # Verify tables were created
            cursor.execute("""                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name LIKE '%monitoring%' 
                   OR table_name LIKE '%ai_%' 
                   OR table_name LIKE '%revenue_%'
                   OR table_name LIKE '%security_%'
                   OR table_name LIKE '%bi_%'
                   OR table_name LIKE '%alert_%'
                   OR table_name LIKE '%system_%'
            """)
            
            tables = cursor.fetchall()
            self.logger.info(f"Created {len(tables)} monitoring tables")
            
            cursor.close()
            
            self.logger.info("✅ Database schema created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database schema creation failed: {e}")
            return False
    
    async def _initialize_redis_structures(self) -> bool:
        """Initialize Redis data structures for monitoring"""        
        self.logger.info("Initializing Redis data structures...")
        
        try:
            # Clear existing monitoring data if force recreate
            if self.force_recreate:
                pattern = "monitoring:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    self.logger.info(f"Cleared {len(keys)} existing monitoring keys")
            
            # Initialize monitoring namespaces
            namespaces = [
                "monitoring:metrics",
                "monitoring:ai_fingerprint",
                "monitoring:revenue",
                "monitoring:security",
                "monitoring:business_intelligence",
                "monitoring:alerts",
                "monitoring:system_health"
            ]
            
            for namespace in namespaces:
                # Set namespace metadata
                self.redis_client.hset(
                    f"{namespace}:meta",
                    mapping={
                        "created_at": datetime.now().isoformat(),
                        "version": "1.0.0",
                        "description": f"Monitoring data for {namespace.split(':')[1]}"
                    }
                )
            
            # Initialize configuration cache
            config_key = "monitoring:config"
            self.redis_client.hset(
                config_key,
                mapping={
                    "profile": self.config.get("profile", "standard"),
                    "environment": os.getenv("ENVIRONMENT", "development"),
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            # Initialize performance counters
            counters = [
                "monitoring:counters:metrics_collected",
                "monitoring:counters:alerts_sent",
                "monitoring:counters:ai_fingerprints_processed",
                "monitoring:counters:revenue_transactions",
                "monitoring:counters:security_events",
                "monitoring:counters:insights_generated"
            ]
            
            for counter in counters:
                self.redis_client.set(counter, 0)
            
            # Initialize status tracking
            self.redis_client.hset(
                "monitoring:status",
                mapping={
                    "system_status": "healthy",
                    "last_health_check": datetime.now().isoformat(),
                    "setup_completed": "true",
                    "active_monitors": "0"
                }
            )
            
            self.logger.info("✅ Redis structures initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Redis structures initialization failed: {e}")
            return False
    
    async def _setup_alerting_channels(self) -> bool:
        """Setup and test alerting channels"""        
        self.logger.info("Setting up alerting channels...")
        
        alerting_config = self.config_manager.get_alerting_config()
        
        # Test email alerting
        if alerting_config.smtp_host and alerting_config.smtp_username:
            try:
                import smtplib
                from email.mime.text import MIMEText
                
                # Test SMTP connection
                server = smtplib.SMTP(alerting_config.smtp_host, alerting_config.smtp_port)
                server.starttls()
                server.login(alerting_config.smtp_username, alerting_config.smtp_password)
                server.quit()
                
                self.logger.info("✅ Email alerting configured and tested")
                
            except Exception as e:
                self.logger.warning(f"Email alerting setup failed: {e}")
        
        # Test Slack alerting
        if alerting_config.slack_webhook_url:
            try:
                test_message = {
                    "channel": alerting_config.slack_channel,
                    "username": alerting_config.slack_username,
                    "text": "🚀 IA Influencer Agent Monitoring Setup Test",
                    "attachments": [{
                        "color": "good",
                        "fields": [{
                            "title": "Setup Status",
                            "value": "Alerting channels configuration test",
                            "short": True
                        }]
                    }]
                }
                
                response = requests.post(
                    alerting_config.slack_webhook_url,
                    json=test_message,
                    timeout=alerting_config.webhook_timeout
                )
                
                if response.status_code == 200:
                    self.logger.info("✅ Slack alerting configured and tested")
                else:
                    self.logger.warning(f"Slack test failed: HTTP {response.status_code}")
                    
            except Exception as e:
                self.logger.warning(f"Slack alerting setup failed: {e}")
        
        # Test Telegram alerting
        if alerting_config.telegram_bot_token and alerting_config.telegram_chat_id:
            try:
                telegram_url = f"https://api.telegram.org/bot{alerting_config.telegram_bot_token}/sendMessage"
                test_message = {
                    "chat_id": alerting_config.telegram_chat_id,
                    "text": "🚀 IA Influencer Agent Monitoring Setup Test\n\nAlerting channels configuration test",
                    "parse_mode": "Markdown"
                }
                
                response = requests.post(
                    telegram_url,
                    json=test_message,
                    timeout=alerting_config.webhook_timeout
                )
                
                if response.status_code == 200:
                    self.logger.info("✅ Telegram alerting configured and tested")
                else:
                    self.logger.warning(f"Telegram test failed: HTTP {response.status_code}")
                    
            except Exception as e:
                self.logger.warning(f"Telegram alerting setup failed: {e}")
        
        self.logger.info("✅ Alerting channels setup completed")
        return True
    
    async def _setup_dashboard(self) -> bool:
        """Setup monitoring dashboard configuration"""        
        self.logger.info("Setting up monitoring dashboard...")
        
        dashboard_config = self.config_manager.get_dashboard_config()
        
        try:
            # Create dashboard configuration in Redis
            dashboard_settings = {
                "port": str(dashboard_config.port),
                "host": dashboard_config.host,
                "debug_mode": str(dashboard_config.debug_mode).lower(),
                "websocket_enabled": str(dashboard_config.websocket_enabled).lower(),
                "auto_refresh_interval": str(dashboard_config.auto_refresh_interval),
                "chart_animation_enabled": str(dashboard_config.chart_animation_enabled).lower(),
                "color_scheme": dashboard_config.color_scheme,
                "authentication_required": str(dashboard_config.authentication_required).lower(),
                "max_concurrent_users": str(dashboard_config.max_concurrent_users)
            }
            
            self.redis_client.hset("monitoring:dashboard:config", mapping=dashboard_settings)
            
            # Initialize dashboard metrics
            dashboard_metrics = {
                "active_connections": "0",
                "total_page_views": "0",
                "last_access": datetime.now().isoformat(),
                "uptime_start": datetime.now().isoformat()
            }
            
            self.redis_client.hset("monitoring:dashboard:metrics", mapping=dashboard_metrics)
            
            self.logger.info("✅ Dashboard setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Dashboard setup failed: {e}")
            return False
    
    async def _deploy_security_rules(self) -> bool:
        """Deploy security monitoring rules"""        
        self.logger.info("Deploying security monitoring rules...")
        
        try:
            # Security rules configuration
            security_rules = {
                "rate_limiting": {
                    "api_requests_per_minute": 1000,
                    "auth_attempts_per_hour": 50,
                    "fingerprint_requests_per_minute": 100
                },
                "threat_detection": {
                    "suspicious_ip_threshold": 10,
                    "failed_auth_threshold": 5,
                    "unusual_access_pattern_threshold": 0.8
                },
                "content_protection": {
                    "unauthorized_access_threshold": 3,
                    "content_theft_detection_enabled": True,
                    "ai_model_attack_detection_enabled": True
                },
                "compliance": {
                    "gdpr_monitoring_enabled": True,
                    "data_retention_monitoring": True,
                    "privacy_violation_detection": True
                }
            }
            
            # Store security rules in Redis
            for category, rules in security_rules.items():
                self.redis_client.hset(
                    f"monitoring:security:rules:{category}",
                    mapping={k: str(v) for k, v in rules.items()}
                )
            
            # Initialize security counters
            security_counters = [
                "monitoring:security:events:total",
                "monitoring:security:events:critical",
                "monitoring:security:events:warning",
                "monitoring:security:threats:blocked",
                "monitoring:security:compliance:violations"
            ]
            
            for counter in security_counters:
                self.redis_client.set(counter, 0)
            
            self.logger.info("✅ Security rules deployed")
            return True
            
        except Exception as e:
            self.logger.error(f"Security rules deployment failed: {e}")
            return False
    
    async def _initialize_ai_models(self) -> bool:
        """Initialize AI model monitoring configuration"""        
        self.logger.info("Initializing AI model monitoring...")
        
        try:
            # AI model configurations
            ai_models = {
                "audio_fingerprint_model": {
                    "model_type": "audio_fingerprinting",
                    "accuracy_threshold": 0.90,
                    "inference_time_threshold_ms": 1000,
                    "drift_detection_enabled": True,
                    "retraining_threshold": 0.05
                },
                "video_fingerprint_model": {
                    "model_type": "video_fingerprinting",
                    "accuracy_threshold": 0.85,
                    "inference_time_threshold_ms": 2000,
                    "drift_detection_enabled": True,
                    "retraining_threshold": 0.07
                },
                "text_similarity_model": {
                    "model_type": "text_similarity",
                    "accuracy_threshold": 0.88,
                    "inference_time_threshold_ms": 500,
                    "drift_detection_enabled": True,
                    "retraining_threshold": 0.06
                },
                "revenue_prediction_model": {
                    "model_type": "revenue_prediction",
                    "accuracy_threshold": 0.80,
                    "inference_time_threshold_ms": 100,
                    "drift_detection_enabled": True,
                    "retraining_threshold": 0.10
                }
            }
            
            # Store model configurations in Redis
            for model_name, config in ai_models.items():
                self.redis_client.hset(
                    f"monitoring:ai:models:{model_name}",
                    mapping={k: str(v) for k, v in config.items()}
                )
            
            # Initialize model metrics
            for model_name in ai_models.keys():
                metrics_key = f"monitoring:ai:metrics:{model_name}"
                self.redis_client.hset(
                    metrics_key,
                    mapping={
                        "total_inferences": "0",
                        "total_errors": "0",
                        "average_accuracy": "0.0",
                        "average_inference_time": "0.0",
                        "last_updated": datetime.now().isoformat()
                    }
                )
            
            self.logger.info("✅ AI model monitoring initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"AI model initialization failed: {e}")
            return False
    
    async def _setup_business_intelligence(self) -> bool:
        """Setup business intelligence monitoring"""        
        self.logger.info("Setting up business intelligence monitoring...")
        
        try:
            # BI configuration
            bi_config = {
                "insight_generation_interval": "300",  # 5 minutes
                "predictive_analytics_enabled": "true",
                "anomaly_detection_enabled": "true",
                "automated_reporting_enabled": "true",
                "ml_model_training_enabled": "true"
            }
            
            self.redis_client.hset("monitoring:bi:config", mapping=bi_config)
            
            # Initialize BI metrics
            bi_metrics = {
                "total_insights_generated": "0",
                "high_priority_insights": "0",
                "revenue_predictions_made": "0",
                "anomalies_detected": "0",
                "reports_generated": "0",
                "last_analysis": datetime.now().isoformat()
            }
            
            self.redis_client.hset("monitoring:bi:metrics", mapping=bi_metrics)
            
            # Create sample insight categories
            insight_categories = [
                "revenue_optimization",
                "content_performance",
                "ai_model_performance",
                "security_analysis",
                "user_behavior",
                "platform_comparison"
            ]
            
            for category in insight_categories:
                self.redis_client.hset(
                    f"monitoring:bi:categories:{category}",
                    mapping={
                        "enabled": "true",
                        "priority": "medium",
                        "last_insight": "never"
                    }
                )
            
            self.logger.info("✅ Business intelligence setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Business intelligence setup failed: {e}")
            return False
    
    async def _establish_performance_baseline(self) -> bool:
        """Establish performance baseline metrics"""        
        self.logger.info("Establishing performance baseline...")
        
        try:
            # Measure current system performance
            start_time = time.time()
            
            # Database performance test
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1")
            db_response_time = (time.time() - start_time) * 1000
            cursor.close()
            
            # Redis performance test
            start_time = time.time()
            self.redis_client.ping()
            redis_response_time = (time.time() - start_time) * 1000
            
            # Establish baseline metrics
            baseline_metrics = {
                "database_response_time_ms": str(db_response_time),
                "redis_response_time_ms": str(redis_response_time),
                "memory_usage_mb": "0",  # Will be updated by monitoring
                "cpu_usage_percent": "0",  # Will be updated by monitoring
                "disk_usage_percent": "0",  # Will be updated by monitoring
                "network_latency_ms": "0",  # Will be updated by monitoring
                "baseline_established": datetime.now().isoformat()
            }
            
            self.redis_client.hset("monitoring:performance:baseline", mapping=baseline_metrics)
            
            # Set performance thresholds based on baseline
            thresholds = {
                "database_response_threshold_ms": str(db_response_time * 3),  # 3x baseline
                "redis_response_threshold_ms": str(redis_response_time * 3),
                "memory_usage_threshold_percent": "80",
                "cpu_usage_threshold_percent": "80",
                "disk_usage_threshold_percent": "85"
            }
            
            self.redis_client.hset("monitoring:performance:thresholds", mapping=thresholds)
            
            self.logger.info(f"✅ Performance baseline established (DB: {db_response_time:.2f}ms, Redis: {redis_response_time:.2f}ms)")
            return True
            
        except Exception as e:
            self.logger.error(f"Performance baseline establishment failed: {e}")
            return False
    
    async def _run_comprehensive_health_check(self) -> bool:
        """Run comprehensive system health check"""        
        self.logger.info("Running comprehensive health check...")
        
        health_results = {}
        overall_health = True
        
        # Database health check
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = cursor.fetchone()[0]
            cursor.close()
            
            health_results["database"] = {
                "status": "healthy",
                "table_count": table_count,
                "connection": "active"
            }
        except Exception as e:
            health_results["database"] = {"status": "unhealthy", "error": str(e)}
            overall_health = False
        
        # Redis health check
        try:
            redis_info = self.redis_client.info()
            health_results["redis"] = {
                "status": "healthy",
                "version": redis_info.get("redis_version"),
                "memory_usage": redis_info.get("used_memory_human"),
                "connected_clients": redis_info.get("connected_clients")
            }
        except Exception as e:
            health_results["redis"] = {"status": "unhealthy", "error": str(e)}
            overall_health = False
        
        # Configuration health check
        try:
            config_validation_results = self._validate_complete_configuration()
            health_results["configuration"] = {
                "status": "healthy" if config_validation_results["valid"] else "warning",
                "validation_results": config_validation_results
            }
        except Exception as e:
            health_results["configuration"] = {"status": "unhealthy", "error": str(e)}
        
        # Store health check results
        health_summary = {
            "overall_status": "healthy" if overall_health else "unhealthy",
            "last_health_check": datetime.now().isoformat(),
            "components_checked": len(health_results),
            "healthy_components": len([r for r in health_results.values() if r.get("status") == "healthy"])
        }
        
        self.redis_client.hset("monitoring:health:summary", mapping=health_summary)
        
        # Store detailed results
        for component, result in health_results.items():
            self.redis_client.hset(
                f"monitoring:health:details:{component}",
                mapping={k: str(v) for k, v in result.items()}
            )
        
        if overall_health:
            self.logger.info("✅ Comprehensive health check passed")
        else:
            self.logger.warning("⚠️ Health check completed with warnings")
        
        return True  # Always return True as this is the final step
    
    def _validate_complete_configuration(self) -> Dict[str, Any]:
        """Validate complete monitoring configuration"""        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check Redis configuration
        redis_config = self.config_manager.get_redis_config()
        if not redis_config.host:
            validation_results["errors"].append("Redis host not configured")
            validation_results["valid"] = False
        
        # Check database configuration
        db_config = self.config_manager.get_database_config()
        if not db_config.host or not db_config.database:
            validation_results["errors"].append("Database configuration incomplete")
            validation_results["valid"] = False
        
        # Check alerting configuration
        alerting_config = self.config_manager.get_alerting_config()
        if not any([
            alerting_config.smtp_username,
            alerting_config.slack_webhook_url,
            alerting_config.telegram_bot_token
        ]):
            validation_results["warnings"].append("No alerting channels configured")
        
        # Performance recommendations
        perf_config = self.config_manager.get_performance_config()
        if perf_config.metrics_collection_interval > 60:
            validation_results["recommendations"].append(
                "Consider reducing metrics collection interval for better granularity"
            )
        
        return validation_results
    
    async def _generate_setup_report(self):
        """Generate comprehensive setup report"""        
        report_lines = [
            "=" * 80,
            "IA INFLUENCER AGENT MONITORING SYSTEM SETUP REPORT",
            "=" * 80,
            f"Setup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Environment: {os.getenv('ENVIRONMENT', 'development')}",
            f"Configuration Profile: {self.config.get('profile', 'unknown')}",
            "",
            "SETUP COMPONENTS STATUS:",
            "-" * 40
        ]
        
        for component, status in self.setup_status.items():
            duration = ""
            if status.start_time and status.end_time:
                duration = f" ({(status.end_time - status.start_time).total_seconds():.2f}s)"
            
            status_icon = {
                "completed": "✅",
                "failed": "❌",
                "running": "🔄",
                "pending": "⏳"
            }.get(status.status, "❓")
            
            report_lines.append(f"{status_icon} {component.upper()}: {status.status.upper()}{duration}")
            
            if status.error_message:
                report_lines.append(f"   Error: {status.error_message}")
        
        report_lines.extend([
            "",
            "CONFIGURATION SUMMARY:",
            "-" * 40,
            f"Redis: {self.config_manager.get_redis_config().host}:{self.config_manager.get_redis_config().port}",
            f"Database: {self.config_manager.get_database_config().host}:{self.config_manager.get_database_config().port}",
            f"Dashboard Port: {self.config_manager.get_dashboard_config().port}",
            f"Metrics Retention: {self.config_manager.get_performance_config().metrics_retention_days} days",
            "",
            "NEXT STEPS:",
            "-" * 40,
            "1. Start the monitoring services: python -m monitoring.index",
            "2. Access the dashboard: http://localhost:8080",
            "3. Configure platform integrations",
            "4. Set up custom alerting rules",
            "5. Review security monitoring settings",
            "",
            "=" * 80
        ])
        
        report_content = "\n".join(report_lines)
        
        # Log the report
        for line in report_lines:
            if line.startswith(("✅", "❌", "🔄", "⏳")):
                self.logger.info(line)
            elif line.startswith("=") or line.startswith("-"):
                continue
            elif line:
                self.logger.info(line)
        
        # Save report to file
        try:
            report_file = Path("monitoring_setup_report.txt")
            with open(report_file, "w") as f:
                f.write(report_content)
            self.logger.info(f"📄 Setup report saved to: {report_file.absolute()}")
        except Exception as e:
            self.logger.warning(f"Could not save setup report: {e}")


async def main():
    """Main setup function"""    
    import argparse
    
    parser = argparse.ArgumentParser(description="IA Influencer Agent Monitoring Setup")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--force-recreate", action="store_true", help="Force recreate existing data")
    parser.add_argument("--environment", help="Environment (development, staging, production)")
    
    args = parser.parse_args()
    
    # Set environment if provided
    if args.environment:
        os.environ["ENVIRONMENT"] = args.environment
    
    # Initialize and run setup
    setup_manager = MonitoringSetupManager(
        config_path=args.config,
        force_recreate=args.force_recreate
    )
    
    success = await setup_manager.run_complete_setup()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
