"""IA Influencer Agent - Logging System Usage Examples
Complete examples of logging system implementation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from . import (
    LogAggregator,
    LogEntry,
    LogLevel,
    ElasticsearchManager,
    ElasticsearchConfig,
    FluentdManager,
    FluentdConfig,
    LogRetentionManager,
    LogAnalyticsEngine,
    LogMonitoringService,
    NotificationChannel
)


class LoggingSystemExample:
    """
Complete example of IA Influencer Agent logging system"""
    
    def __init__(self):
        self.aggregator = None
        self.es_manager = None
        self.fluentd_manager = None
        self.retention_manager = None
        self.analytics_engine = None
        self.monitoring_service = None
    
    async def setup_complete_system(self):
        """
Setup complete logging system with all components"""
        
        # 1. Setup Log Aggregator
        aggregator_config = {
            'buffer_size': 1000,
            'flush_interval': 30,
            'elasticsearch': {
                'enabled': True,
                'hosts': ['localhost:9200'],
                'index_pattern': 'ia-influencer-logs-%Y.%m.%d'
            },
            'redis': {
                'enabled': True,
                'url': 'redis://localhost:6379',
                'stream_name': 'ia-influencer-logs'
            },
            'file': {
                'enabled': True,
                'directory': '/var/log/ia-influencer',
                'rotation_size': 100 * 1024 * 1024  # 100MB
            },
            'sentry_dsn': 'your-sentry-dsn-here'
        }
        
        self.aggregator = LogAggregator(aggregator_config)
        await self.aggregator.start()
        
        # 2. Setup Elasticsearch Manager
        es_config = ElasticsearchConfig(
            hosts=['localhost:9200'],
            username='elastic',
            password='password',
            use_ssl=False,
            verify_certs=False
        )
        
        self.es_manager = ElasticsearchManager(es_config)
        await self.es_manager.connect()
        
        # 3. Setup Fluentd Manager
        fluentd_config = FluentdConfig(
            host='localhost',
            port=24224,
            buffer_chunk_limit='2M',
            flush_interval='60s'
        )
        
        self.fluentd_manager = FluentdManager(fluentd_config)
        await self.fluentd_manager.start()
        
        # 4. Setup Retention Manager
        self.retention_manager = LogRetentionManager()
        await self.retention_manager.load_config()
        
        # 5. Setup Analytics Engine
        self.analytics_engine = LogAnalyticsEngine(self.es_manager)
        
        # 6. Setup Monitoring Service
        self.monitoring_service = LogMonitoringService(
            self.analytics_engine,
            redis_url='redis://localhost:6379'
        )
        
        # Configure notification channels
        email_config = {
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password',
            'from_email': 'alerts@ia-influencer.com',
            'to_emails': ['admin@ia-influencer.com'],
            'use_tls': True
        }
        
        slack_config = {
            'token': 'your-slack-bot-token',
            'channel': '#alerts'
        }
        
        self.monitoring_service.configure_notification_channel(
            NotificationChannel.EMAIL, email_config
        )
        self.monitoring_service.configure_notification_channel(
            NotificationChannel.SLACK, slack_config
        )
        
        await self.monitoring_service.start()
        
        logging.info("Complete logging system setup completed")
    
    async def example_ai_processing_logs(self):
        """Example of AI processing logs"""
        
        # Fingerprinting success
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="Audio fingerprint generated successfully",
            service="fingerprinting",
            module="audio_processor",
            user_id="user_123",
            session_id="session_456",
            trace_id="trace_789",
            metadata={
                "content_type": "audio",
                "algorithm": "chromaprint",
                "processing_time_ms": 1250,
                "fingerprint_hash": "abc123def456",
                "file_size_mb": 3.2,
                "duration_seconds": 185
            }
        )
        
        # AI model inference
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="AI model inference completed",
            service="ai_engine",
            module="recommendation_engine",
            user_id="user_123",
            metadata={
                "model_name": "recommendation_v2.1",
                "inference_time_ms": 45,
                "input_features": 128,
                "confidence_score": 0.92,
                "recommendations_count": 10
            }
        )
        
        # Similarity matching
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="Content similarity search completed",
            service="matching",
            module="vector_search",
            user_id="user_123",
            metadata={
                "query_type": "audio_similarity",
                "search_time_ms": 23,
                "results_count": 5,
                "similarity_threshold": 0.85,
                "database_size": 1000000
            }
        )
    
    async def example_error_logs(self):
        """Example of error logging scenarios"""
        
        # AI processing error
        await self.aggregator.log(
            level=LogLevel.ERROR,
            message="AI model inference failed due to invalid input format",
            service="ai_engine",
            module="content_analyzer",
            user_id="user_456",
            metadata={
                "error_code": "AI_INVALID_INPUT",
                "model_name": "content_analysis_v1.5",
                "input_type": "video",
                "file_format": "unknown",
                "stack_trace": "Traceback (most recent call last)...",
                "retry_count": 3
            }
        )
        
        # Database connection error
        await self.aggregator.log(
            level=LogLevel.CRITICAL,
            message="Database connection pool exhausted",
            service="database",
            module="connection_manager",
            metadata={
                "error_code": "DB_POOL_EXHAUSTED",
                "pool_size": 20,
                "active_connections": 20,
                "pending_requests": 45,
                "database_host": "db-primary.internal"
            }
        )
        
        # Revenue processing error
        await self.aggregator.log(
            level=LogLevel.CRITICAL,
            message="Revenue calculation failed for user payment",
            service="monetization",
            module="revenue_processor",
            user_id="user_789",
            metadata={
                "error_code": "REVENUE_CALC_FAILED",
                "payment_id": "pay_123456",
                "amount": 25.50,
                "currency": "EUR",
                "platform": "youtube",
                "calculation_method": "view_based"
            }
        )
    
    async def example_user_activity_logs(self):
        """Example of user activity logging"""
        
        # User upload
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="User uploaded new content",
            service="content_upload",
            module="upload_handler",
            user_id="user_123",
            session_id="session_abc",
            metadata={
                "content_type": "audio",
                "file_size_mb": 5.2,
                "duration_seconds": 240,
                "format": "mp3",
                "upload_time_seconds": 12.5,
                "storage_location": "s3://bucket/user_123/audio_001.mp3"
            }
        )
        
        # User collaboration request
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="User sent collaboration request",
            service="collaboration",
            module="request_handler",
            user_id="user_123",
            metadata={
                "target_user_id": "user_456",
                "collaboration_type": "music_production",
                "project_genre": "electronic",
                "proposed_terms": "50/50 split",
                "message_length": 150
            }
        )
        
        # User authentication
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="User authentication successful",
            service="auth",
            module="jwt_manager",
            user_id="user_123",
            session_id="session_xyz",
            metadata={
                "auth_method": "oauth2",
                "provider": "google",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "location": "Berlin, Germany"
            }
        )
    
    async def example_performance_logs(self):
        """Example of performance monitoring logs"""
        
        # API response time
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="API request processed",
            service="api_gateway",
            module="request_handler",
            user_id="user_123",
            metadata={
                "endpoint": "/api/v1/content/upload",
                "method": "POST",
                "response_time_ms": 1250,
                "status_code": 200,
                "request_size_kb": 128,
                "response_size_kb": 2.1
            }
        )
        
        # Database query performance
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="Database query executed",
            service="database",
            module="query_executor",
            metadata={
                "query_type": "SELECT",
                "table": "user_content",
                "execution_time_ms": 45,
                "rows_returned": 25,
                "index_used": "idx_user_timestamp",
                "cache_hit": True
            }
        )
        
        # Background job performance
        await self.aggregator.log(
            level=LogLevel.INFO,
            message="Background job completed",
            service="job_scheduler",
            module="content_processor",
            metadata={
                "job_type": "fingerprint_generation",
                "job_id": "job_123456",
                "execution_time_seconds": 125,
                "files_processed": 10,
                "success_rate": 0.95,
                "queue_size": 150
            }
        )
    
    async def run_analytics_examples(self):
        """Example of analytics operations"""
        
        # Compute metrics
        metrics = await self.analytics_engine.compute_metrics(24)
        print("Current Metrics:")
        for metric in metrics:
            print(f"- {metric.metric_name}: {metric.value}")
        
        # Check alerts
        triggered_alerts = await self.analytics_engine.check_alerts()
        if triggered_alerts:
            print(f"\nTriggered Alerts: {len(triggered_alerts)}")
            for alert in triggered_alerts:
                print(f"- {alert['alert']['name']}: {alert['current_value']}")
        
        # Detect anomalies
        anomalies = await self.analytics_engine.detect_anomalies(24)
        if anomalies:
            print(f"\nAnomalies Detected: {len(anomalies)}")
            for anomaly in anomalies[:3]:  # Show first 3
                print(f"- Score: {anomaly['anomaly_score']:.3f}, Service: {anomaly.get('service')}")
        
        # Analyze error patterns
        error_patterns = await self.analytics_engine.analyze_error_patterns(24)
        print(f"\nError Analysis:")
        print(f"- Total errors: {error_patterns.get('total_errors', 0)}")
        print(f"- Unique patterns: {error_patterns.get('unique_patterns', 0)}")
        
        # Generate dashboard data
        dashboard_data = await self.analytics_engine.generate_dashboard_data()
        print(f"\nDashboard Summary:")
        print(f"- Metrics computed: {len(dashboard_data['metrics'])}")
        print(f"- Active alerts: {len(dashboard_data['active_alerts'])}")
        print(f"- Anomalies: {dashboard_data['anomalies']['count']}")
    
    async def run_retention_examples(self):
        """Example of retention operations"""
        
        # Run retention policies
        log_directory = "/var/log/ia-influencer"
        retention_results = await self.retention_manager.run_retention(log_directory)
        
        print("Retention Results:")
        print(f"- Files processed: {retention_results['total_processed']}")
        print(f"- Files compressed: {retention_results['total_compressed']}")
        print(f"- Files archived: {retention_results['total_archived']}")
        print(f"- Files deleted: {retention_results['total_deleted']}")
        print(f"- Space freed: {retention_results['total_size_freed'] / 1024 / 1024:.1f} MB")
        
        # Get retention statistics
        stats = await self.retention_manager.get_retention_statistics(log_directory)
        print(f"\nRetention Statistics:")
        print(f"- Total files: {stats['total_files']}")
        print(f"- Total size: {stats['total_size_mb']:.1f} MB")
        print(f"- Compressed ratio: {stats['compression_ratio']:.2%}")
    
    async def cleanup_system(self):
        """Cleanup and shutdown logging system"""
        
        if self.monitoring_service:
            await self.monitoring_service.stop()
        
        if self.retention_manager:
            await self.retention_manager.stop_scheduler()
        
        if self.fluentd_manager:
            await self.fluentd_manager.stop()
        
        if self.es_manager:
            await self.es_manager.disconnect()
        
        if self.aggregator:
            await self.aggregator.stop()
        
        logging.info("Logging system cleanup completed")


async def main():
    """Main example execution"""
    
    # Initialize logging system
    example = LoggingSystemExample()
    
    try:
        # Setup complete system
        await example.setup_complete_system()
        
        # Generate example logs
        await example.example_ai_processing_logs()
        await example.example_error_logs()
        await example.example_user_activity_logs()
        await example.example_performance_logs()
        
        # Wait for logs to be processed
        await asyncio.sleep(5)
        
        # Run analytics
        await example.run_analytics_examples()
        
        # Run retention examples
        await example.run_retention_examples()
        
        # Keep system running for demonstration
        print("\nLogging system running... Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(60)
                
                # Log system health
                await example.aggregator.log(
                    level=LogLevel.INFO,
                    message="System health check",
                    service="monitoring",
                    module="health_checker",
                    metadata={
                        "cpu_usage": 15.2,
                        "memory_usage": 68.5,
                        "disk_usage": 45.1,
                        "active_connections": 125
                    }
                )
        
        except KeyboardInterrupt:
            print("\nShutting down...")
    
    finally:
        # Cleanup
        await example.cleanup_system()


if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(main())
