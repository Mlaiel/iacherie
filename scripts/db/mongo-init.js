// MongoDB initialization script for Ainflue Platform
// This script sets up collections and indexes for development

// Switch to ainflue_documents database
db = db.getSiblingDB('ainflue_documents');

// Create collections
db.createCollection('content_fingerprints');
db.createCollection('ai_analysis_results');
db.createCollection('protection_logs');
db.createCollection('analytics_data');

// Create indexes for content_fingerprints
db.content_fingerprints.createIndex({ "content_id": 1 });
db.content_fingerprints.createIndex({ "fingerprint_hash": 1 });
db.content_fingerprints.createIndex({ "content_type": 1 });
db.content_fingerprints.createIndex({ "created_at": 1 });

// Create indexes for ai_analysis_results
db.ai_analysis_results.createIndex({ "content_id": 1 });
db.ai_analysis_results.createIndex({ "analysis_type": 1 });
db.ai_analysis_results.createIndex({ "confidence": 1 });
db.ai_analysis_results.createIndex({ "created_at": 1 });

// Create indexes for protection_logs
db.protection_logs.createIndex({ "content_id": 1 });
db.protection_logs.createIndex({ "platform": 1 });
db.protection_logs.createIndex({ "action_type": 1 });
db.protection_logs.createIndex({ "timestamp": 1 });

// Create indexes for analytics_data
db.analytics_data.createIndex({ "user_id": 1 });
db.analytics_data.createIndex({ "metric_type": 1 });
db.analytics_data.createIndex({ "date": 1 });
db.analytics_data.createIndex({ "platform": 1 });

// Insert sample data for development
db.content_fingerprints.insertMany([
    {
        content_id: "sample-content-1",
        fingerprint_hash: "abcd1234567890",
        content_type: "audio",
        features: {
            duration: 180.5,
            sample_rate: 44100,
            channels: 2
        },
        created_at: new Date()
    },
    {
        content_id: "sample-content-2",
        fingerprint_hash: "efgh5678901234",
        content_type: "text",
        features: {
            word_count: 150,
            language: "en",
            sentiment: "positive"
        },
        created_at: new Date()
    }
]);

db.ai_analysis_results.insertMany([
    {
        content_id: "sample-content-1",
        analysis_type: "audio_fingerprinting",
        confidence: 0.95,
        results: {
            genre: "electronic",
            tempo: 128,
            key: "C major"
        },
        created_at: new Date()
    },
    {
        content_id: "sample-content-2",
        analysis_type: "text_analysis",
        confidence: 0.87,
        results: {
            topics: ["technology", "innovation"],
            readability_score: 7.2,
            entities: ["AI", "machine learning"]
        },
        created_at: new Date()
    }
]);

// Create user for application access
db.createUser({
    user: "ainflue_app",
    pwd: "app_mongo_password_123",
    roles: [
        {
            role: "readWrite",
            db: "ainflue_documents"
        }
    ]
});

print("MongoDB initialization completed successfully!");