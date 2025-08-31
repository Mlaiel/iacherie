"""Database Connections Usage Example - IA Influencer Agent Platform

This example demonstrates how to use the comprehensive database connections module
for the IA Influencer Agent platform supporting content creators, AI processing,
protection, and monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

# Import the database connections components
from backend.database.connections import (
    get_database_index,
    DatabaseConnectionsIndex,
    TenantType,
    ContentProtectionConnections,
    MonetizationConnections,
    ContentType,
    PlatformType,
    RevenueType,
    PaymentMethod
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_usage():
    """Basic usage example for database connections"""
    
    logger.info("=== Basic Database Connections Usage ===")
    
    # 1. Get the global database index
    db_index = await get_database_index()
    
    try:
        # 2. Register a content creator tenant
        tenant_config = await db_index.register_tenant(
            tenant_id="artist_12345",
            tenant_type=TenantType.INDIVIDUAL_ARTIST,
            config_overrides={
                "connection_limits": {
                    "postgresql": 15,
                    "redis": 8,
                    "mongodb": 10
                }
            }
        )
        logger.info(f"Registered tenant: {tenant_config.tenant_id}")
        
        # 3. Basic database operations with tenant isolation
        async with db_index.session("postgresql", "artist_12345") as pg_session:
            # Execute a tenant-isolated query
            result = await pg_session.execute("SELECT NOW() as current_time")
            logger.info(f"PostgreSQL current time: {result}")
        
        async with db_index.session("redis", "artist_12345") as redis_session:
            # Cache some artist data
            await redis_session.set("artist_profile", "{'name': 'John Artist', 'genre': 'Electronic'}")
            cached_profile = await redis_session.get("artist_profile")
            logger.info(f"Cached artist profile: {cached_profile}")
        
        async with db_index.session("mongodb", "artist_12345") as mongo_session:
            # Store content metadata
            content_doc = {
                "title": "Epic Electronic Track",
                "duration": 240,
                "genre": "Electronic",
                "created_at": datetime.utcnow(),
                "tags": ["electronic", "dance", "upbeat"]
            }
            result = await mongo_session.content_metadata.insert_one(content_doc)
            logger.info(f"Stored content metadata with ID: {result.inserted_id}")
        
        # 4. Check database health
        health_status = await db_index.get_health_status()
        logger.info(f"Database health status: {health_status['status']}")
        
    except Exception as e:
        logger.error(f"Basic usage failed: {e}")
        raise


async def example_content_protection_workflow():
    """Example of content protection workflow"""
    
    logger.info("=== Content Protection Workflow ===")
    
    # Initialize database connections
    db_index = await get_database_index()
    
    # Get connection handlers for protection operations
    handlers = {
        "postgresql": await db_index.get_connection("postgresql"),
        "mongodb": await db_index.get_connection("mongodb"),
        "redis": await db_index.get_connection("redis"),
        "vector_store": await db_index.get_connection("vector_store"),
        "object_storage": await db_index.get_connection("object_storage"),
        "elasticsearch": await db_index.get_connection("elasticsearch")
    }
    
    # Initialize content protection connections
    protection = ContentProtectionConnections(handlers)
    
    try:
        # 1. Store content fingerprint for protection
        fake_content = b"This is fake audio content for demonstration"
        fake_ai_fingerprint = b"fake_ai_generated_fingerprint_data"
        fake_vector_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dim vector
        
        fingerprint_id = await protection.store_content_fingerprint(
            tenant_id="artist_12345",
            content_type=ContentType.AUDIO,
            original_filename="epic_track.mp3",
            file_content=fake_content,
            ai_fingerprint=fake_ai_fingerprint,
            vector_embedding=fake_vector_embedding,
            metadata={
                "genre": "Electronic",
                "bpm": 128,
                "key": "C major",
                "duration": 240
            }
        )
        logger.info(f"Stored content fingerprint: {fingerprint_id}")
        
        # 2. Simulate content violation detection
        alert_id = await protection.create_protection_alert(
            fingerprint_id=fingerprint_id,
            detected_url="https://youtube.com/watch?v=fake_video_id",
            platform="youtube",
            similarity_score=0.92,
            evidence_data={
                "video_title": "Stolen Epic Track",
                "channel_name": "MusicThief",
                "upload_date": datetime.utcnow().isoformat(),
                "view_count": 50000
            }
        )
        logger.info(f"Created protection alert: {alert_id}")
        
        # 3. Search for similar content
        query_vector = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # Similar vector
        similar_content = await protection.search_similar_content(
            tenant_id="artist_12345",
            query_vector=query_vector,
            similarity_threshold=0.80,
            max_results=10
        )
        logger.info(f"Found {len(similar_content)} similar content items")
        
        # 4. Get protection summary
        protection_summary = await protection.get_tenant_protection_summary(
            tenant_id="artist_12345",
            days_back=30
        )
        logger.info(f"Protection summary: {protection_summary['metrics']}")
        
        # 5. Update alert status
        success = await protection.update_alert_status(
            alert_id=alert_id,
            new_status="resolved",
            resolution_notes="Takedown request successfully processed"
        )
        logger.info(f"Alert status updated: {success}")
        
    except Exception as e:
        logger.error(f"Content protection workflow failed: {e}")
        raise


async def example_monetization_workflow():
    """Example of monetization workflow"""
    
    logger.info("=== Monetization Workflow ===")
    
    # Initialize database connections
    db_index = await get_database_index()
    
    # Get connection handlers for monetization operations
    handlers = {
        "postgresql": await db_index.get_connection("postgresql"),
        "mongodb": await db_index.get_connection("mongodb"),
        "redis": await db_index.get_connection("redis"),
        "elasticsearch": await db_index.get_connection("elasticsearch")
    }
    
    # Initialize monetization connections
    monetization = MonetizationConnections(handlers)
    
    try:
        # 1. Record revenue from YouTube
        youtube_revenue_id = await monetization.record_revenue(
            tenant_id="artist_12345",
            platform=PlatformType.YOUTUBE,
            revenue_type=RevenueType.ADVERTISING,
            gross_amount=Decimal("1250.00"),
            currency="USD",
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            platform_metadata={
                "video_id": "abc123xyz",
                "views": 500000,
                "cpm": Decimal("2.50"),
                "channel_id": "artist_channel_123"
            }
        )
        logger.info(f"Recorded YouTube revenue: {youtube_revenue_id}")
        
        # 2. Record revenue from Spotify
        spotify_revenue_id = await monetization.record_revenue(
            tenant_id="artist_12345",
            platform=PlatformType.SPOTIFY,
            revenue_type=RevenueType.ROYALTIES,
            gross_amount=Decimal("890.50"),
            currency="USD",
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            platform_metadata={
                "track_id": "spotify_track_456",
                "streams": 750000,
                "rate_per_stream": Decimal("0.003"),
                "playlist_adds": 15000
            }
        )
        logger.info(f"Recorded Spotify revenue: {spotify_revenue_id}")
        
        # 3. Create license agreement
        license_id = await monetization.create_license_agreement(
            tenant_id="artist_12345",
            content_id="epic_track_001",
            licensee_info={
                "company": "AdAgency Inc",
                "contact_email": "licensing@adagency.com",
                "contact_phone": "+1-555-0123"
            },
            license_type="non_exclusive",
            license_terms={
                "usage": "commercial_advertising",
                "territory": "worldwide",
                "media": ["television", "online", "radio"],
                "duration_months": 12
            },
            revenue_share=Decimal("0.15"),  # 15% revenue share
            duration_days=365
        )
        logger.info(f"Created license agreement: {license_id}")
        
        # 4. Create payout request
        payout_id = await monetization.create_payout_request(
            tenant_id="artist_12345",
            amount=Decimal("1500.00"),
            currency="USD",
            payment_method=PaymentMethod.STRIPE,
            payment_details={
                "stripe_account_id": "acct_artist_12345",
                "destination_account": "bank_account_789",
                "description": "Monthly revenue payout"
            }
        )
        logger.info(f"Created payout request: {payout_id}")
        
        # 5. Get revenue analytics
        analytics = await monetization.get_revenue_analytics(
            tenant_id="artist_12345",
            start_date=datetime.utcnow() - timedelta(days=90),
            end_date=datetime.utcnow(),
            group_by="platform"
        )
        logger.info(f"Revenue analytics: {analytics['total_stats']}")
        
        # 6. Process automatic payouts (admin function)
        payout_results = await monetization.process_automatic_payouts()
        logger.info(f"Automatic payout processing: {payout_results}")
        
    except Exception as e:
        logger.error(f"Monetization workflow failed: {e}")
        raise


async def example_multi_tenant_collaboration():
    """Example of multi-tenant collaboration"""
    
    logger.info("=== Multi-Tenant Collaboration ===")
    
    db_index = await get_database_index()
    
    try:
        # 1. Register multiple content creators
        artist1_config = await db_index.register_tenant(
            tenant_id="artist_primary",
            tenant_type=TenantType.INDIVIDUAL_ARTIST
        )
        
        artist2_config = await db_index.register_tenant(
            tenant_id="artist_collaborator1", 
            tenant_type=TenantType.INDIVIDUAL_ARTIST
        )
        
        producer_config = await db_index.register_tenant(
            tenant_id="producer_feature",
            tenant_type=TenantType.INDIVIDUAL_ARTIST
        )
        
        logger.info("Registered collaboration participants")
        
        # 2. Create collaboration for remix project
        collaboration_id = await db_index.create_collaboration(
            primary_tenant_id="artist_primary",
            collaborator_tenant_ids=["artist_collaborator1", "producer_feature"],
            collaboration_type="remix_project",
            permissions={
                "artist_collaborator1": ["read", "write"],
                "producer_feature": ["read", "write", "export"]
            }
        )
        logger.info(f"Created collaboration: {collaboration_id}")
        
        # 3. Use distributed transaction across multiple tenants
        async with db_index.distributed_transaction(
            tenant_id="artist_primary",
            databases=["postgresql", "mongodb", "redis"]
        ) as tx:
            # Operations will be coordinated across all databases
            await tx.postgresql.execute(
                "INSERT INTO collaborations (id, name, type) VALUES ($1, $2, $3)",
                collaboration_id, "Epic Remix Project", "remix"
            )
            
            await tx.mongodb.collaboration_metadata.insert_one({
                "collaboration_id": collaboration_id,
                "participants": ["artist_primary", "artist_collaborator1", "producer_feature"],
                "project_details": {
                    "genre": "Electronic/Hip-Hop Fusion",
                    "target_duration": 210,
                    "release_date": "2025-12-01"
                }
            })
            
            await tx.redis.set(
                f"active_collaboration:{collaboration_id}",
                "true",
                expire=86400
            )
            
            # All operations committed together
        
        logger.info("Distributed transaction completed successfully")
        
        # 4. Get collaboration metrics
        collaboration_metrics = await db_index.get_connection_metrics(
            tenant_id="artist_primary"
        )
        logger.info(f"Collaboration metrics: {collaboration_metrics}")
        
    except Exception as e:
        logger.error(f"Multi-tenant collaboration failed: {e}")
        raise


async def example_performance_monitoring():
    """Example of performance monitoring and optimization"""
    
    logger.info("=== Performance Monitoring & Optimization ===")
    
    db_index = await get_database_index()
    
    try:
        # 1. Get comprehensive health status
        health_status = await db_index.get_health_status()
        logger.info(f"Overall system health: {health_status['status']}")
        
        for db_type, db_health in health_status["databases"].items():
            logger.info(f"{db_type} health: {db_health}")
        
        # 2. Get detailed performance metrics
        performance_metrics = await db_index.get_connection_metrics()
        logger.info(f"Performance metrics: {performance_metrics['performance_metrics']}")
        
        # 3. Run connection optimization
        optimization_results = await db_index.optimize_connections()
        logger.info(f"Optimization completed: {optimization_results}")
        
        for recommendation in optimization_results["recommendations"]:
            logger.info(f"Recommendation: {recommendation}")
        
        # 4. Monitor specific tenant performance
        tenant_metrics = await db_index.get_connection_metrics("artist_12345")
        logger.info(f"Tenant metrics: {tenant_metrics['tenant_metrics']}")
        
    except Exception as e:
        logger.error(f"Performance monitoring failed: {e}")
        raise


async def example_business_logic_integration():
    """Example showing complete business logic integration"""
    
    logger.info("=== Complete Business Logic Integration ===")
    
    db_index = await get_database_index()
    
    try:
        # Simulate complete content creator workflow:
        # Upload → Process → Protect → Monitor → Monetize → Collaborate
        
        # 1. Content Creator Registration & Setup
        creator_id = "content_creator_demo"
        await db_index.register_tenant(
            tenant_id=creator_id,
            tenant_type=TenantType.INDIVIDUAL_ARTIST,
            config_overrides={
                "storage_quota_gb": 500,
                "api_rate_limit": 5000
            }
        )
        logger.info(f"Registered content creator: {creator_id}")
        
        # 2. Content Upload & Fingerprinting
        protection_handlers = {
            "postgresql": await db_index.get_connection("postgresql"),
            "mongodb": await db_index.get_connection("mongodb"),
            "redis": await db_index.get_connection("redis"),
            "vector_store": await db_index.get_connection("vector_store"),
            "object_storage": await db_index.get_connection("object_storage")
        }
        protection = ContentProtectionConnections(protection_handlers)
        
        # Simulate content upload
        content_data = b"Simulated music content data"
        ai_fingerprint = b"ai_generated_fingerprint"
        vector_embedding = [0.1] * 512  # 512-dimensional vector
        
        fingerprint_id = await protection.store_content_fingerprint(
            tenant_id=creator_id,
            content_type=ContentType.AUDIO,
            original_filename="new_hit_song.mp3",
            file_content=content_data,
            ai_fingerprint=ai_fingerprint,
            vector_embedding=vector_embedding,
            metadata={
                "title": "My New Hit Song",
                "genre": "Pop",
                "duration": 180,
                "release_date": "2025-09-01"
            }
        )
        logger.info(f"Content protected with fingerprint: {fingerprint_id}")
        
        # 3. Revenue Generation & Tracking
        monetization_handlers = {
            "postgresql": await db_index.get_connection("postgresql"),
            "mongodb": await db_index.get_connection("mongodb"),
            "redis": await db_index.get_connection("redis"),
            "elasticsearch": await db_index.get_connection("elasticsearch")
        }
        monetization = MonetizationConnections(monetization_handlers)
        
        # Simulate revenue from multiple platforms
        platforms_revenue = [
            (PlatformType.YOUTUBE, Decimal("2500.00"), RevenueType.ADVERTISING),
            (PlatformType.SPOTIFY, Decimal("1200.00"), RevenueType.ROYALTIES),
            (PlatformType.INSTAGRAM, Decimal("800.00"), RevenueType.SPONSORSHIPS)
        ]
        
        for platform, amount, revenue_type in platforms_revenue:
            revenue_id = await monetization.record_revenue(
                tenant_id=creator_id,
                platform=platform,
                revenue_type=revenue_type,
                gross_amount=amount,
                currency="USD",
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow()
            )
            logger.info(f"Recorded {platform.value} revenue: {revenue_id}")
        
        # 4. Analytics & Reporting
        analytics = await monetization.get_revenue_analytics(
            tenant_id=creator_id,
            start_date=datetime.utcnow() - timedelta(days=90),
            end_date=datetime.utcnow()
        )
        
        logger.info(f"Total Revenue Analytics:")
        logger.info(f"- Total Revenue: ${analytics['total_stats']['total_revenue']}")
        logger.info(f"- Platform Breakdown: {analytics['platform_breakdown']}")
        logger.info(f"- Growth Metrics: {analytics['growth_metrics']}")
        
        # 5. Protection Summary
        protection_summary = await protection.get_tenant_protection_summary(
            tenant_id=creator_id,
            days_back=30
        )
        
        logger.info(f"Protection Summary:")
        logger.info(f"- Fingerprints: {protection_summary['metrics']['total_fingerprints']}")
        logger.info(f"- Alerts: {protection_summary['metrics']['total_alerts']}")
        logger.info(f"- Effectiveness: {protection_summary['metrics']['effectiveness_score']}")
        
        logger.info("Complete business logic integration successful!")
        
    except Exception as e:
        logger.error(f"Business logic integration failed: {e}")
        raise


async def main():
    """Run all examples"""
    try:
        # Run all example workflows
        await example_basic_usage()
        await example_content_protection_workflow()
        await example_monetization_workflow()
        await example_multi_tenant_collaboration()
        await example_performance_monitoring()
        await example_business_logic_integration()
        
        logger.info("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}")
        raise
    
    finally:
        # Cleanup
        db_index = await get_database_index()
        await db_index.shutdown()
        logger.info("Database connections shut down")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
            host="localhost",
            port=5432,
            database="tenant1_db",
            username="tenant1_user",
            password="secure_password"
        ),
        redis_config=RedisConfig(
            host="localhost",
            port=6379,
            db=1
        ),
        max_connections=50,
        features_enabled=["content_protection", "monetization", "analytics"]
    )
    
    tenant2_config = TenantConfig(
        tenant_id="creator_platform_2", 
        name="Content Creator Platform 2",
        database_config=DatabaseConfig(
            host="localhost",
            port=5432,
            database="tenant2_db",
            username="tenant2_user",
            password="secure_password"
        ),
        redis_config=RedisConfig(
            host="localhost",
            port=6379,
            db=2
        ),
        max_connections=30,
        features_enabled=["content_protection", "collaboration"]
    )
    
    # Add tenants
    await config_manager.add_tenant(tenant1_config)
    await config_manager.add_tenant(tenant2_config)
    
    # Initialize connection factory
    factory = DatabaseConnectionFactory(Environment.DEVELOPMENT)
    await factory.initialize()
    
    try:
        # Create connections for tenant 1
        tenant1_connections = await factory.create_tenant_connections("creator_platform_1")
        logger.info(f"Created connections for tenant 1: {list(tenant1_connections.keys())}")
        
        # Create connections for tenant 2
        tenant2_connections = await factory.create_tenant_connections("creator_platform_2")
        logger.info(f"Created connections for tenant 2: {list(tenant2_connections.keys())}")
        
        # Use tenant-specific connections
        if "postgresql" in tenant1_connections:
            pg_handler = tenant1_connections["postgresql"]
            # This will use tenant1's database
            await pg_handler.execute_query(
                "CREATE TABLE IF NOT EXISTS creators (id SERIAL PRIMARY KEY, name VARCHAR(255))"
            )
            logger.info("Created creators table for tenant 1")
        
        if "redis" in tenant1_connections:
            redis_handler = tenant1_connections["redis"]
            # This will use tenant1's Redis database
            await redis_handler.set("tenant1:setting", "value", expire=3600)
            logger.info("Set tenant-specific setting in Redis")
        
        # Test all connections
        test_results = await factory.test_all_connections()
        logger.info(f"Connection test results: {test_results}")
        
        # Get metrics
        metrics = await factory.get_metrics()
        logger.info(f"Factory metrics: {metrics['factory_statistics']}")
        
    finally:
        await factory.shutdown()
        await config_manager.shutdown()


async def example_transaction_management():
    """Transaction management example"""
    
    logger.info("=== Transaction Management Example ===")
    
    manager = DatabaseConnectionManager()
    await manager.initialize()
    
    try:
        # Start a distributed transaction
        transaction_manager = manager.transaction_manager
        
        transaction_id = await transaction_manager.begin_transaction(
            databases=["postgresql", "mongodb"],
            tenant_id="creator_platform_1"
        )
        
        try:
            # Execute operations in transaction
            pg_handler = await manager.get_connection("postgresql", "creator_platform_1")
            if pg_handler:
                await pg_handler.execute_query(
                    "INSERT INTO creators (name) VALUES (%s)",
                    ("New Creator",),
                    transaction_id=transaction_id
                )
            
            mongo_handler = await manager.get_connection("mongodb", "creator_platform_1")
            if mongo_handler:
                await mongo_handler.insert_one(
                    "creator_profiles",
                    {
                        "name": "New Creator",
                        "created_at": datetime.utcnow(),
                        "status": "active"
                    },
                    transaction_id=transaction_id
                )
            
            # Commit transaction
            await transaction_manager.commit_transaction(transaction_id)
            logger.info("Transaction committed successfully")
            
        except Exception as e:
            # Rollback on error
            await transaction_manager.rollback_transaction(transaction_id)
            logger.error(f"Transaction rolled back due to error: {e}")
            
    finally:
        await manager.shutdown()


async def example_content_protection_workflow():
    """Content protection workflow example"""
    
    logger.info("=== Content Protection Workflow ===")
    
    manager = DatabaseConnectionManager()
    await manager.initialize()
    
    try:
        # Simulate content creator uploading content
        content_data = {
            "title": "My Original Music Track",
            "creator_id": "creator_123",
            "file_path": "/uploads/music/track_001.mp3",
            "duration": 180.5,
            "created_at": datetime.utcnow()
        }
        
        # 1. Store content metadata in MongoDB
        mongo_handler = await manager.get_connection("mongodb")
        if mongo_handler:
            content_id = await mongo_handler.insert_one("content", content_data)
            logger.info(f"Stored content metadata with ID: {content_id}")
        
        # 2. Store content fingerprint for protection
        fingerprint_data = {
            "content_id": str(content_id),
            "audio_fingerprint": "af123456789abcdef",  # Simulated fingerprint
            "video_fingerprint": None,
            "text_fingerprint": None,
            "created_at": datetime.utcnow()
        }
        
        if mongo_handler:
            fingerprint_id = await mongo_handler.insert_one("fingerprints", fingerprint_data)
            logger.info(f"Stored content fingerprint with ID: {fingerprint_id}")
        
        # 3. Create vector embedding for similarity search
        vector_handler = await manager.get_connection("vector_store")
        if vector_handler:
            # Simulated audio feature vector
            audio_vector = [0.1, 0.2, 0.3] * 256  # 768-dimensional vector
            
            await vector_handler.add_vectors(
                vectors=[audio_vector],
                metadata=[{"content_id": str(content_id), "type": "audio"}],
                ids=[f"content_{content_id}"]
            )
            logger.info("Added content vector for similarity search")
        
        # 4. Index content for search in Elasticsearch
        elasticsearch_handler = await manager.get_connection("elasticsearch")
        if elasticsearch_handler:
            search_doc = {
                "content_id": str(content_id),
                "title": content_data["title"],
                "creator_id": content_data["creator_id"],
                "tags": ["music", "original", "audio"],
                "duration": content_data["duration"],
                "created_at": content_data["created_at"].isoformat()
            }
            
            await elasticsearch_handler.index_document(
                index="content_search",
                document=search_doc,
                document_id=str(content_id)
            )
            logger.info("Indexed content for search")
        
        # 5. Store upload tracking in PostgreSQL
        pg_handler = await manager.get_connection("postgresql")
        if pg_handler:
            await pg_handler.execute_query("""
                INSERT INTO content_uploads (content_id, creator_id, status, upload_time)
                VALUES (%s, %s, %s, %s)
            """, (str(content_id), content_data["creator_id"], "completed", datetime.utcnow()))
            logger.info("Recorded upload tracking")
        
        # 6. Cache recent uploads in Redis
        redis_handler = await manager.get_connection("redis")
        if redis_handler:
            cache_key = f"recent_uploads:{content_data['creator_id']}"
            await redis_handler.lpush(cache_key, str(content_id))
            await redis_handler.ltrim(cache_key, 0, 99)  # Keep last 100
            await redis_handler.expire(cache_key, 86400)  # 24 hours
            logger.info("Cached recent upload")
        
        logger.info("Content protection workflow completed successfully")
        
        # Simulate content monitoring (checking for unauthorized usage)
        logger.info("Starting content monitoring...")
        
        # Search for similar content
        if vector_handler:
            similar_results = await vector_handler.search_similar(
                query_vector=audio_vector,
                k=5,
                threshold=0.8
            )
            logger.info(f"Found {len(similar_results)} similar content items")
        
        # Search for potential matches
        if elasticsearch_handler:
            search_results = await elasticsearch_handler.search(
                index="content_search",
                query={
                    "match": {
                        "title": content_data["title"]
                    }
                }
            )
            logger.info(f"Found {len(search_results.get('hits', {}).get('hits', []))} search matches")
        
    finally:
        await manager.shutdown()


async def example_monetization_tracking():
    """Monetization tracking example"""
    
    logger.info("=== Monetization Tracking Example ===")
    
    manager = DatabaseConnectionManager()
    await manager.initialize()
    
    try:
        # Simulate revenue events
        revenue_events = [
            {
                "content_id": "content_123",
                "creator_id": "creator_123",
                "platform": "youtube",
                "revenue_type": "ad_revenue",
                "amount": 25.50,
                "currency": "USD",
                "timestamp": datetime.utcnow()
            },
            {
                "content_id": "content_123", 
                "creator_id": "creator_123",
                "platform": "spotify",
                "revenue_type": "streaming",
                "amount": 3.25,
                "currency": "USD", 
                "timestamp": datetime.utcnow()
            }
        ]
        
        # Store revenue data in PostgreSQL for ACID compliance
        pg_handler = await manager.get_connection("postgresql")
        if pg_handler:
            for event in revenue_events:
                await pg_handler.execute_query("""
                    INSERT INTO revenue_events (content_id, creator_id, platform, revenue_type, 
                                              amount, currency, event_timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    event["content_id"], event["creator_id"], event["platform"],
                    event["revenue_type"], event["amount"], event["currency"],
                    event["timestamp"]
                ))
            logger.info(f"Stored {len(revenue_events)} revenue events")
        
        # Update real-time analytics in Redis
        redis_handler = await manager.get_connection("redis")
        if redis_handler:
            total_revenue = sum(event["amount"] for event in revenue_events)
            
            # Update creator's total revenue
            await redis_handler.incrbyfloat("revenue:creator_123:total", total_revenue)
            
            # Update daily revenue
            today = datetime.utcnow().strftime("%Y-%m-%d")
            await redis_handler.incrbyfloat(f"revenue:daily:{today}", total_revenue)
            
            # Update platform-specific revenue
            for event in revenue_events:
                platform_key = f"revenue:platform:{event['platform']}"
                await redis_handler.incrbyfloat(platform_key, event["amount"])
            
            logger.info("Updated real-time revenue analytics")
        
        # Store detailed analytics in MongoDB
        mongo_handler = await manager.get_connection("mongodb")
        if mongo_handler:
            analytics_doc = {
                "creator_id": "creator_123",
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_revenue": total_revenue,
                "platform_breakdown": {
                    "youtube": 25.50,
                    "spotify": 3.25
                },
                "content_performance": {
                    "content_123": total_revenue
                },
                "updated_at": datetime.utcnow()
            }
            
            # Upsert analytics document
            await mongo_handler.update_one(
                "daily_analytics",
                {"creator_id": "creator_123", "date": analytics_doc["date"]},
                {"$set": analytics_doc},
                upsert=True
            )
            logger.info("Updated analytics in MongoDB")
        
        # Index for revenue reporting
        elasticsearch_handler = await manager.get_connection("elasticsearch")
        if elasticsearch_handler:
            for event in revenue_events:
                report_doc = {
                    "creator_id": event["creator_id"],
                    "content_id": event["content_id"],
                    "platform": event["platform"],
                    "revenue_type": event["revenue_type"],
                    "amount": event["amount"],
                    "currency": event["currency"],
                    "timestamp": event["timestamp"].isoformat(),
                    "year": event["timestamp"].year,
                    "month": event["timestamp"].month,
                    "day": event["timestamp"].day
                }
                
                await elasticsearch_handler.index_document(
                    index="revenue_reports",
                    document=report_doc
                )
            
            logger.info("Indexed revenue events for reporting")
        
        logger.info("Monetization tracking completed successfully")
        
    finally:
        await manager.shutdown()


async def main():
    """Run all examples"""
    
    logger.info("Starting IA Influencer Agent Database Connections Examples")
    
    try:
        await example_basic_usage()
        await asyncio.sleep(1)
        
        await example_multi_tenant_usage()
        await asyncio.sleep(1)
        
        await example_transaction_management()
        await asyncio.sleep(1)
        
        await example_content_protection_workflow()
        await asyncio.sleep(1)
        
        await example_monetization_tracking()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise
    
    logger.info("All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
