// MongoDB Index Definitions for IA Influencer Agent Platform
// Comprehensive indexing strategy for optimal query performance
//
// Author: Fahed Mlaiel <mlaiel@live.de>
// Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

// =============================================================================
// DATABASE INITIALIZATION
// =============================================================================

// Connect to the IA Influencer database
use ia_influencer;

print("Creating indexes for IA Influencer Agent Platform...");

// =============================================================================
// USER COLLECTION INDEXES
// =============================================================================

print("Creating indexes for users collection...");

// Primary lookup indexes
db.users.createIndex({ "user_id": 1 }, { unique: true, name: "idx_users_user_id" });
db.users.createIndex({ "email": 1 }, { unique: true, sparse: true, name: "idx_users_email" });
db.users.createIndex({ "username": 1 }, { unique: true, name: "idx_users_username" });

// Profile and search indexes
db.users.createIndex({ "creator_type": 1 }, { name: "idx_users_creator_type" });
db.users.createIndex({ "subscription_tier": 1 }, { name: "idx_users_subscription_tier" });
db.users.createIndex({ "account_status": 1 }, { name: "idx_users_account_status" });
db.users.createIndex({ "location": 1 }, { name: "idx_users_location" });
db.users.createIndex({ "skills": 1 }, { name: "idx_users_skills" });

// Activity and engagement indexes
db.users.createIndex({ "last_activity": -1 }, { name: "idx_users_last_activity" });
db.users.createIndex({ "created_at": -1 }, { name: "idx_users_created_at" });
db.users.createIndex({ "follower_count": -1 }, { name: "idx_users_follower_count" });
db.users.createIndex({ "content_count": -1 }, { name: "idx_users_content_count" });

// Search and discovery indexes
db.users.createIndex({ 
  "display_name": "text", 
  "bio": "text", 
  "skills": "text", 
  "categories": "text" 
}, { 
  name: "idx_users_text_search",
  weights: { 
    "display_name": 10, 
    "skills": 5, 
    "bio": 2, 
    "categories": 3 
  }
});

// Geospatial indexes for location-based features
db.users.createIndex({ "location_coordinates": "2dsphere" }, { name: "idx_users_geospatial" });

// Compound indexes for common queries
db.users.createIndex({ "creator_type": 1, "subscription_tier": 1 }, { name: "idx_users_type_tier" });
db.users.createIndex({ "account_status": 1, "last_activity": -1 }, { name: "idx_users_status_activity" });
db.users.createIndex({ "location": 1, "creator_type": 1 }, { name: "idx_users_location_type" });

// =============================================================================
// MEDIA CONTENT COLLECTION INDEXES
// =============================================================================

print("Creating indexes for media_content collection...");

// Primary identification indexes
db.media_content.createIndex({ "content_id": 1 }, { unique: true, name: "idx_content_content_id" });
db.media_content.createIndex({ "user_id": 1 }, { name: "idx_content_user_id" });
db.media_content.createIndex({ "file_hash": 1 }, { name: "idx_content_file_hash" });

// Content classification indexes
db.media_content.createIndex({ "content_type": 1 }, { name: "idx_content_type" });
db.media_content.createIndex({ "category": 1 }, { name: "idx_content_category" });
db.media_content.createIndex({ "genre": 1 }, { name: "idx_content_genre" });
db.media_content.createIndex({ "tags": 1 }, { name: "idx_content_tags" });

// Status and visibility indexes
db.media_content.createIndex({ "status": 1 }, { name: "idx_content_status" });
db.media_content.createIndex({ "visibility": 1 }, { name: "idx_content_visibility" });
db.media_content.createIndex({ "processing_status": 1 }, { name: "idx_content_processing_status" });

// Temporal indexes
db.media_content.createIndex({ "created_at": -1 }, { name: "idx_content_created_at" });
db.media_content.createIndex({ "updated_at": -1 }, { name: "idx_content_updated_at" });
db.media_content.createIndex({ "published_at": -1 }, { name: "idx_content_published_at" });

// Performance and analytics indexes
db.media_content.createIndex({ "view_count": -1 }, { name: "idx_content_view_count" });
db.media_content.createIndex({ "like_count": -1 }, { name: "idx_content_like_count" });
db.media_content.createIndex({ "download_count": -1 }, { name: "idx_content_download_count" });
db.media_content.createIndex({ "rating": -1 }, { name: "idx_content_rating" });

// Content search indexes
db.media_content.createIndex({ 
  "title": "text", 
  "description": "text", 
  "tags": "text", 
  "keywords": "text" 
}, { 
  name: "idx_content_text_search",
  weights: { 
    "title": 10, 
    "tags": 5, 
    "keywords": 3, 
    "description": 2 
  }
});

// AI and analysis indexes
db.media_content.createIndex({ "ai_analysis.content_type": 1 }, { name: "idx_content_ai_type" });
db.media_content.createIndex({ "ai_analysis.mood": 1 }, { name: "idx_content_ai_mood" });
db.media_content.createIndex({ "fingerprint_hash": 1 }, { name: "idx_content_fingerprint" });

// Compound indexes for complex queries
db.media_content.createIndex({ "user_id": 1, "created_at": -1 }, { name: "idx_content_user_created" });
db.media_content.createIndex({ "content_type": 1, "category": 1 }, { name: "idx_content_type_category" });
db.media_content.createIndex({ "visibility": 1, "status": 1, "created_at": -1 }, { name: "idx_content_public_recent" });
db.media_content.createIndex({ "tags": 1, "view_count": -1 }, { name: "idx_content_tags_popular" });

// =============================================================================
// COLLABORATION PROJECTS COLLECTION INDEXES
// =============================================================================

print("Creating indexes for collaboration_projects collection...");

// Project identification
db.collaboration_projects.createIndex({ "project_id": 1 }, { unique: true, name: "idx_projects_project_id" });
db.collaboration_projects.createIndex({ "created_by": 1 }, { name: "idx_projects_created_by" });

// Project status and lifecycle
db.collaboration_projects.createIndex({ "status": 1 }, { name: "idx_projects_status" });
db.collaboration_projects.createIndex({ "project_type": 1 }, { name: "idx_projects_type" });
db.collaboration_projects.createIndex({ "priority": 1 }, { name: "idx_projects_priority" });

// Temporal indexes
db.collaboration_projects.createIndex({ "created_at": -1 }, { name: "idx_projects_created_at" });
db.collaboration_projects.createIndex({ "start_date": 1 }, { name: "idx_projects_start_date" });
db.collaboration_projects.createIndex({ "deadline": 1 }, { name: "idx_projects_deadline" });
db.collaboration_projects.createIndex({ "completed_at": -1 }, { name: "idx_projects_completed_at" });

// Participants and team indexes
db.collaboration_projects.createIndex({ "participants.user_id": 1 }, { name: "idx_projects_participants" });
db.collaboration_projects.createIndex({ "team_size": 1 }, { name: "idx_projects_team_size" });

// Budget and financial indexes
db.collaboration_projects.createIndex({ "budget": -1 }, { name: "idx_projects_budget" });
db.collaboration_projects.createIndex({ "revenue": -1 }, { name: "idx_projects_revenue" });

// Project search
db.collaboration_projects.createIndex({ 
  "title": "text", 
  "description": "text", 
  "skills_required": "text" 
}, { 
  name: "idx_projects_text_search",
  weights: { 
    "title": 10, 
    "skills_required": 5, 
    "description": 2 
  }
});

// Compound indexes
db.collaboration_projects.createIndex({ "created_by": 1, "status": 1 }, { name: "idx_projects_creator_status" });
db.collaboration_projects.createIndex({ "project_type": 1, "status": 1, "created_at": -1 }, { name: "idx_projects_type_status_date" });

// =============================================================================
// USER ANALYTICS COLLECTION INDEXES
// =============================================================================

print("Creating indexes for user_analytics collection...");

// User and time-based indexes
db.user_analytics.createIndex({ "user_id": 1 }, { name: "idx_analytics_user_id" });
db.user_analytics.createIndex({ "date": -1 }, { name: "idx_analytics_date" });
db.user_analytics.createIndex({ "timestamp": -1 }, { name: "idx_analytics_timestamp" });

// Event type indexes
db.user_analytics.createIndex({ "event_type": 1 }, { name: "idx_analytics_event_type" });
db.user_analytics.createIndex({ "category": 1 }, { name: "idx_analytics_category" });

// Performance metrics
db.user_analytics.createIndex({ "session_duration": -1 }, { name: "idx_analytics_session_duration" });
db.user_analytics.createIndex({ "page_views": -1 }, { name: "idx_analytics_page_views" });

// Compound indexes for time-series queries
db.user_analytics.createIndex({ "user_id": 1, "date": -1 }, { name: "idx_analytics_user_date" });
db.user_analytics.createIndex({ "event_type": 1, "timestamp": -1 }, { name: "idx_analytics_event_time" });
db.user_analytics.createIndex({ "user_id": 1, "event_type": 1, "timestamp": -1 }, { name: "idx_analytics_user_event_time" });

// =============================================================================
// CONTENT ANALYTICS COLLECTION INDEXES
// =============================================================================

print("Creating indexes for content_analytics collection...");

// Content and temporal indexes
db.content_analytics.createIndex({ "content_id": 1 }, { name: "idx_content_analytics_content_id" });
db.content_analytics.createIndex({ "date": -1 }, { name: "idx_content_analytics_date" });
db.content_analytics.createIndex({ "timestamp": -1 }, { name: "idx_content_analytics_timestamp" });

// Metrics indexes
db.content_analytics.createIndex({ "views": -1 }, { name: "idx_content_analytics_views" });
db.content_analytics.createIndex({ "engagement_rate": -1 }, { name: "idx_content_analytics_engagement" });
db.content_analytics.createIndex({ "conversion_rate": -1 }, { name: "idx_content_analytics_conversion" });

// Compound indexes
db.content_analytics.createIndex({ "content_id": 1, "date": -1 }, { name: "idx_content_analytics_content_date" });

// =============================================================================
// MESSAGES COLLECTION INDEXES
// =============================================================================

print("Creating indexes for messages collection...");

// Message identification and conversation
db.messages.createIndex({ "message_id": 1 }, { unique: true, name: "idx_messages_message_id" });
db.messages.createIndex({ "conversation_id": 1 }, { name: "idx_messages_conversation_id" });
db.messages.createIndex({ "sender_id": 1 }, { name: "idx_messages_sender_id" });
db.messages.createIndex({ "recipient_id": 1 }, { name: "idx_messages_recipient_id" });

// Temporal and status indexes
db.messages.createIndex({ "timestamp": -1 }, { name: "idx_messages_timestamp" });
db.messages.createIndex({ "read_status": 1 }, { name: "idx_messages_read_status" });
db.messages.createIndex({ "message_type": 1 }, { name: "idx_messages_type" });

// Message search
db.messages.createIndex({ "content": "text" }, { name: "idx_messages_text_search" });

// Compound indexes
db.messages.createIndex({ "conversation_id": 1, "timestamp": -1 }, { name: "idx_messages_conversation_time" });
db.messages.createIndex({ "recipient_id": 1, "read_status": 1 }, { name: "idx_messages_recipient_unread" });

// =============================================================================
// NOTIFICATIONS COLLECTION INDEXES
// =============================================================================

print("Creating indexes for notifications collection...");

// Notification identification and targeting
db.notifications.createIndex({ "notification_id": 1 }, { unique: true, name: "idx_notifications_notification_id" });
db.notifications.createIndex({ "user_id": 1 }, { name: "idx_notifications_user_id" });
db.notifications.createIndex({ "sender_id": 1 }, { name: "idx_notifications_sender_id" });

// Status and type indexes
db.notifications.createIndex({ "status": 1 }, { name: "idx_notifications_status" });
db.notifications.createIndex({ "notification_type": 1 }, { name: "idx_notifications_type" });
db.notifications.createIndex({ "priority": 1 }, { name: "idx_notifications_priority" });

// Temporal indexes
db.notifications.createIndex({ "created_at": -1 }, { name: "idx_notifications_created_at" });
db.notifications.createIndex({ "scheduled_at": 1 }, { name: "idx_notifications_scheduled_at" });
db.notifications.createIndex({ "expires_at": 1 }, { name: "idx_notifications_expires_at" });

// Compound indexes
db.notifications.createIndex({ "user_id": 1, "status": 1, "created_at": -1 }, { name: "idx_notifications_user_status_date" });
db.notifications.createIndex({ "user_id": 1, "notification_type": 1 }, { name: "idx_notifications_user_type" });

// =============================================================================
// ACTIVITY LOGS COLLECTION INDEXES
// =============================================================================

print("Creating indexes for activity_logs collection...");

// User and session tracking
db.activity_logs.createIndex({ "user_id": 1 }, { name: "idx_activity_user_id" });
db.activity_logs.createIndex({ "session_id": 1 }, { name: "idx_activity_session_id" });

// Activity classification
db.activity_logs.createIndex({ "activity_type": 1 }, { name: "idx_activity_type" });
db.activity_logs.createIndex({ "category": 1 }, { name: "idx_activity_category" });

// Temporal indexes
db.activity_logs.createIndex({ "timestamp": -1 }, { name: "idx_activity_timestamp" });

// IP and security indexes
db.activity_logs.createIndex({ "ip_address": 1 }, { name: "idx_activity_ip" });
db.activity_logs.createIndex({ "user_agent": 1 }, { name: "idx_activity_user_agent" });

// Compound indexes
db.activity_logs.createIndex({ "user_id": 1, "timestamp": -1 }, { name: "idx_activity_user_time" });
db.activity_logs.createIndex({ "activity_type": 1, "timestamp": -1 }, { name: "idx_activity_type_time" });

// =============================================================================
// SPECIAL ANALYTICS COLLECTIONS
// =============================================================================

print("Creating indexes for analytics database...");

// Switch to analytics database
use ia_influencer_analytics;

// Events collection
db.events.createIndex({ "user_id": 1 }, { name: "idx_events_user_id" });
db.events.createIndex({ "event_type": 1 }, { name: "idx_events_type" });
db.events.createIndex({ "timestamp": -1 }, { name: "idx_events_timestamp" });
db.events.createIndex({ "user_id": 1, "timestamp": -1 }, { name: "idx_events_user_time" });

// Metrics collection
db.metrics.createIndex({ "metric_type": 1 }, { name: "idx_metrics_type" });
db.metrics.createIndex({ "date": -1 }, { name: "idx_metrics_date" });
db.metrics.createIndex({ "metric_type": 1, "date": -1 }, { name: "idx_metrics_type_date" });

// Reports collection
db.reports.createIndex({ "user_id": 1 }, { name: "idx_reports_user_id" });
db.reports.createIndex({ "report_type": 1 }, { name: "idx_reports_type" });
db.reports.createIndex({ "report_date": -1 }, { name: "idx_reports_date" });
db.reports.createIndex({ "user_id": 1, "report_date": -1 }, { name: "idx_reports_user_date" });

// =============================================================================
// TTL INDEXES FOR DATA RETENTION
// =============================================================================

print("Creating TTL indexes for data retention...");

// Switch back to main database
use ia_influencer;

// Session data - expire after 8 hours
db.user_sessions.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0, name: "idx_sessions_ttl" });

// Temporary upload data - expire after 24 hours
db.temp_uploads.createIndex({ "created_at": 1 }, { expireAfterSeconds: 86400, name: "idx_temp_uploads_ttl" });

// Password reset tokens - expire after 1 hour
db.password_reset_tokens.createIndex({ "created_at": 1 }, { expireAfterSeconds: 3600, name: "idx_reset_tokens_ttl" });

// Email verification tokens - expire after 24 hours
db.email_verification_tokens.createIndex({ "created_at": 1 }, { expireAfterSeconds: 86400, name: "idx_email_tokens_ttl" });

// Analytics database TTL indexes
use ia_influencer_analytics;

// Raw events - expire after 90 days
db.events.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 7776000, name: "idx_events_ttl" });

// Activity logs - expire after 180 days
use ia_influencer;
db.activity_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 15552000, name: "idx_activity_logs_ttl" });

// =============================================================================
// BACKGROUND INDEX CREATION
// =============================================================================

print("Creating background indexes for large collections...");

// Large collections should have indexes created in background
use ia_influencer;

// Background indexes for potentially large collections
db.user_analytics.createIndex({ "user_id": 1, "event_type": 1, "date": -1 }, { background: true, name: "idx_analytics_user_event_date_bg" });
db.content_analytics.createIndex({ "content_id": 1, "metric_type": 1, "timestamp": -1 }, { background: true, name: "idx_content_analytics_content_metric_time_bg" });
db.activity_logs.createIndex({ "user_id": 1, "activity_type": 1, "timestamp": -1 }, { background: true, name: "idx_activity_user_type_time_bg" });

// =============================================================================
// SPARSE INDEXES FOR OPTIONAL FIELDS
// =============================================================================

print("Creating sparse indexes for optional fields...");

// Sparse indexes only include documents that have the indexed field
db.users.createIndex({ "social_profiles.instagram": 1 }, { sparse: true, name: "idx_users_instagram_sparse" });
db.users.createIndex({ "social_profiles.youtube": 1 }, { sparse: true, name: "idx_users_youtube_sparse" });
db.users.createIndex({ "phone_number": 1 }, { sparse: true, name: "idx_users_phone_sparse" });

db.media_content.createIndex({ "ai_analysis.sentiment_score": -1 }, { sparse: true, name: "idx_content_sentiment_sparse" });
db.media_content.createIndex({ "monetization.price": -1 }, { sparse: true, name: "idx_content_price_sparse" });

// =============================================================================
// PARTIAL INDEXES FOR FILTERED QUERIES
// =============================================================================

print("Creating partial indexes for filtered queries...");

// Partial indexes for active/published content only
db.media_content.createIndex(
  { "view_count": -1 }, 
  { 
    partialFilterExpression: { "visibility": "public", "status": "published" },
    name: "idx_content_public_views_partial"
  }
);

db.users.createIndex(
  { "last_activity": -1 }, 
  { 
    partialFilterExpression: { "account_status": "active" },
    name: "idx_users_active_last_activity_partial"
  }
);

// =============================================================================
// PERFORMANCE OPTIMIZATION
// =============================================================================

print("Optimizing indexes and running statistics...");

// Update collection statistics
use ia_influencer;
db.runCommand({ "planCacheClear": "users" });
db.runCommand({ "planCacheClear": "media_content" });
db.runCommand({ "planCacheClear": "collaboration_projects" });

use ia_influencer_analytics;
db.runCommand({ "planCacheClear": "events" });
db.runCommand({ "planCacheClear": "metrics" });

// =============================================================================
// INDEX VALIDATION AND REPORTING
// =============================================================================

print("Validating indexes and generating report...");

use ia_influencer;

// List all indexes for verification
var collections = [
  "users", 
  "media_content", 
  "collaboration_projects", 
  "user_analytics", 
  "content_analytics",
  "messages",
  "notifications", 
  "activity_logs"
];

collections.forEach(function(collectionName) {
  print("\n=== Indexes for " + collectionName + " ===");
  var indexes = db.getCollection(collectionName).getIndexes();
  indexes.forEach(function(index) {
    print("  " + index.name + ": " + JSON.stringify(index.key));
  });
});

use ia_influencer_analytics;
var analyticsCollections = ["events", "metrics", "reports"];

analyticsCollections.forEach(function(collectionName) {
  print("\n=== Analytics Indexes for " + collectionName + " ===");
  var indexes = db.getCollection(collectionName).getIndexes();
  indexes.forEach(function(index) {
    print("  " + index.name + ": " + JSON.stringify(index.key));
  });
});

print("\n=============================================================================");
print("MongoDB index creation completed successfully!");
print("Total indexes created: " + (collections.length + analyticsCollections.length) * 5 + "+ indexes");
print("=============================================================================");

// =============================================================================
// MONITORING QUERIES FOR INDEX USAGE
// =============================================================================

// Example queries to monitor index usage:
// db.users.find({}).explain("executionStats")
// db.media_content.find({"visibility": "public"}).sort({"view_count": -1}).explain("executionStats")
// db.collaboration_projects.find({"status": "active"}).explain("executionStats")

print("Index creation script completed. Monitor index usage with explain() commands.");