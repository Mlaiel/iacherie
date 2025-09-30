package com.ainflue.sdk;

/**
 * Main Ainflue SDK Client for Java
 * 
 * Multi-expert implementation:
 * - Backend Senior: Robust Java client architecture with enterprise patterns
 * - Security: Secure authentication and request handling
 * - DevOps: Monitoring and metrics integration
 * - Lead Dev IA: Intelligent retry logic and connection management
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @version 1.0.0
 */

import com.ainflue.sdk.auth.AuthenticationManager;
import com.ainflue.sdk.client.HttpClientAdapter;
import com.ainflue.sdk.config.SdkConfiguration;
import com.ainflue.sdk.exceptions.AinflueSdkException;
import com.ainflue.sdk.exceptions.ConfigurationException;
import com.ainflue.sdk.models.ApiResponse;
import com.ainflue.sdk.models.ContentItem;
import com.ainflue.sdk.models.UserProfile;
import com.ainflue.sdk.services.ContentService;
import com.ainflue.sdk.services.AnalyticsService;
import com.ainflue.sdk.services.AIService;
import com.ainflue.sdk.utils.Constants;
import com.ainflue.sdk.utils.Logger;
import com.ainflue.sdk.metrics.SdkMetrics;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.io.Closeable;
import java.time.Instant;

/**
 * Main SDK client providing access to all Ainflue platform features
 */
public class AinflueSdk implements Closeable {
    
    private static final String SDK_VERSION = "1.0.0";
    private static final String USER_AGENT = "Ainflue-Java-SDK/" + SDK_VERSION;
    
    private final SdkConfiguration configuration;
    private final AuthenticationManager authManager;
    private final HttpClientAdapter httpClient;
    private final Logger logger;
    private final SdkMetrics metrics;
    
    // Service instances (Backend Senior - Service layer pattern)
    private final ContentService contentService;
    private final AnalyticsService analyticsService;
    private final AIService aiService;
    
    private volatile boolean isInitialized = false;
    private volatile boolean isClosed = false;
    
    /**
     * Constructor with configuration
     */
    public AinflueSdk(SdkConfiguration configuration) {
        validateConfiguration(configuration);
        
        this.configuration = configuration;
        this.logger = new Logger(AinflueSdk.class);
        this.metrics = new SdkMetrics();
        
        // Initialize core components
        this.authManager = new AuthenticationManager(configuration);
        this.httpClient = new HttpClientAdapter(configuration, authManager);
        
        // Initialize services
        this.contentService = new ContentService(httpClient, metrics);
        this.analyticsService = new AnalyticsService(httpClient, metrics);
        this.aiService = new AIService(httpClient, metrics);
        
        logger.info("Ainflue SDK initialized with version " + SDK_VERSION);
    }
    
    /**
     * Builder pattern for SDK configuration (Backend Senior expertise)
     */
    public static class Builder {
        private String apiKey;
        private String baseUrl = Constants.DEFAULT_BASE_URL;
        private int timeout = Constants.DEFAULT_TIMEOUT;
        private int maxRetries = Constants.DEFAULT_MAX_RETRIES;
        private boolean enableMetrics = true;
        private boolean enableLogging = true;
        private String environment = "production";
        
        public Builder apiKey(String apiKey) {
            this.apiKey = apiKey;
            return this;
        }
        
        public Builder baseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }
        
        public Builder timeout(int timeout, TimeUnit unit) {
            this.timeout = (int) unit.toMillis(timeout);
            return this;
        }
        
        public Builder maxRetries(int maxRetries) {
            this.maxRetries = maxRetries;
            return this;
        }
        
        public Builder enableMetrics(boolean enableMetrics) {
            this.enableMetrics = enableMetrics;
            return this;
        }
        
        public Builder enableLogging(boolean enableLogging) {
            this.enableLogging = enableLogging;
            return this;
        }
        
        public Builder environment(String environment) {
            this.environment = environment;
            return this;
        }
        
        public AinflueSdk build() {
            SdkConfiguration config = SdkConfiguration.builder()
                .apiKey(apiKey)
                .baseUrl(baseUrl)
                .timeout(timeout)
                .maxRetries(maxRetries)
                .enableMetrics(enableMetrics)
                .enableLogging(enableLogging)
                .environment(environment)
                .build();
                
            return new AinflueSdk(config);
        }
    }
    
    /**
     * Create SDK builder
     */
    public static Builder builder() {
        return new Builder();
    }
    
    /**
     * Initialize SDK with authentication (Security expertise)
     */
    public CompletableFuture<Void> initialize() {
        if (isInitialized) {
            return CompletableFuture.completedFuture(null);
        }
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                logger.info("Initializing Ainflue SDK...");
                
                // Initialize authentication
                authManager.initialize();
                
                // Verify API connectivity
                verifyConnectivity();
                
                // Start metrics collection if enabled
                if (configuration.isMetricsEnabled()) {
                    metrics.startCollection();
                }
                
                isInitialized = true;
                logger.info("Ainflue SDK initialization completed successfully");
                
                return null;
                
            } catch (Exception e) {
                logger.error("SDK initialization failed", e);
                throw new AinflueSdkException("SDK initialization failed: " + e.getMessage(), e);
            }
        });
    }
    
    /**
     * Get current user profile
     */
    public CompletableFuture<UserProfile> getCurrentUser() {
        ensureInitialized();
        
        return httpClient.get("/auth/me", UserProfile.class)
            .thenApply(response -> {
                metrics.recordApiCall("getCurrentUser", true);
                return response.getData();
            })
            .exceptionally(throwable -> {
                metrics.recordApiCall("getCurrentUser", false);
                throw new AinflueSdkException("Failed to get current user", throwable);
            });
    }
    
    /**
     * Upload content with intelligent processing (Audio Engineer + ML Engineer expertise)
     */
    public CompletableFuture<ContentItem> uploadContent(byte[] content, 
                                                       String filename, 
                                                       String contentType,
                                                       Map<String, Object> metadata) {
        ensureInitialized();
        return contentService.uploadContent(content, filename, contentType, metadata);
    }
    
    /**
     * Get content by ID
     */
    public CompletableFuture<ContentItem> getContent(String contentId) {
        ensureInitialized();
        return contentService.getContent(contentId);
    }
    
    /**
     * List user content with pagination
     */
    public CompletableFuture<List<ContentItem>> listContent(int page, int limit) {
        ensureInitialized();
        return contentService.listContent(page, limit);
    }
    
    /**
     * Search content with AI-powered search
     */
    public CompletableFuture<List<ContentItem>> searchContent(String query, Map<String, Object> filters) {
        ensureInitialized();
        return contentService.searchContent(query, filters);
    }
    
    /**
     * Process content with AI (ML Engineer expertise)
     */
    public CompletableFuture<String> processWithAI(String contentId, String processorType, Map<String, Object> options) {
        ensureInitialized();
        return aiService.processContent(contentId, processorType, options);
    }
    
    /**
     * Get processing status
     */
    public CompletableFuture<Map<String, Object>> getProcessingStatus(String jobId) {
        ensureInitialized();
        return aiService.getProcessingStatus(jobId);
    }
    
    /**
     * Analyze content for copyright (Lead Dev IA expertise)
     */
    public CompletableFuture<Map<String, Object>> analyzeCopyright(String contentId) {
        ensureInitialized();
        return aiService.analyzeCopyright(contentId);
    }
    
    /**
     * Get analytics data (DevOps expertise)
     */
    public CompletableFuture<Map<String, Object>> getAnalytics(String timeframe) {
        ensureInitialized();
        return analyticsService.getAnalytics(timeframe);
    }
    
    /**
     * Get content analytics
     */
    public CompletableFuture<Map<String, Object>> getContentAnalytics(String contentId, String timeframe) {
        ensureInitialized();
        return analyticsService.getContentAnalytics(contentId, timeframe);
    }
    
    /**
     * Track custom event
     */
    public CompletableFuture<Void> trackEvent(String eventType, Map<String, Object> properties) {
        ensureInitialized();
        return analyticsService.trackEvent(eventType, properties);
    }
    
    /**
     * Get SDK metrics (DevOps expertise)
     */
    public Map<String, Object> getMetrics() {
        return metrics.getMetrics();
    }
    
    /**
     * Get SDK health status
     */
    public CompletableFuture<Map<String, Object>> getHealthStatus() {
        return httpClient.get("/health", Map.class)
            .thenApply(response -> {
                Map<String, Object> health = response.getData();
                health.put("sdk_version", SDK_VERSION);
                health.put("sdk_metrics", getMetrics());
                return health;
            });
    }
    
    /**
     * Refresh authentication token
     */
    public CompletableFuture<Void> refreshToken() {
        ensureInitialized();
        return authManager.refreshToken();
    }
    
    /**
     * Check if SDK is authenticated
     */
    public boolean isAuthenticated() {
        return authManager.isAuthenticated();
    }
    
    /**
     * Get configuration
     */
    public SdkConfiguration getConfiguration() {
        return configuration;
    }
    
    /**
     * Get authentication manager
     */
    public AuthenticationManager getAuthManager() {
        return authManager;
    }
    
    /**
     * Close SDK and cleanup resources
     */
    @Override
    public void close() {
        if (isClosed) {
            return;
        }
        
        try {
            logger.info("Closing Ainflue SDK...");
            
            // Stop metrics collection
            if (metrics != null) {
                metrics.stopCollection();
            }
            
            // Close HTTP client
            if (httpClient != null) {
                httpClient.close();
            }
            
            // Close authentication manager
            if (authManager != null) {
                authManager.close();
            }
            
            isClosed = true;
            logger.info("Ainflue SDK closed successfully");
            
        } catch (Exception e) {
            logger.error("Error closing SDK", e);
        }
    }
    
    /**
     * Private helper methods
     */
    
    private void validateConfiguration(SdkConfiguration configuration) {
        if (configuration == null) {
            throw new ConfigurationException("Configuration cannot be null");
        }
        
        if (configuration.getApiKey() == null || configuration.getApiKey().trim().isEmpty()) {
            throw new ConfigurationException("API key is required");
        }
        
        if (configuration.getBaseUrl() == null || configuration.getBaseUrl().trim().isEmpty()) {
            throw new ConfigurationException("Base URL is required");
        }
        
        if (configuration.getTimeout() <= 0) {
            throw new ConfigurationException("Timeout must be positive");
        }
        
        if (configuration.getMaxRetries() < 0) {
            throw new ConfigurationException("Max retries cannot be negative");
        }
    }
    
    private void ensureInitialized() {
        if (!isInitialized) {
            throw new IllegalStateException("SDK must be initialized before use. Call initialize() first.");
        }
        
        if (isClosed) {
            throw new IllegalStateException("SDK has been closed and cannot be used");
        }
    }
    
    private void verifyConnectivity() {
        try {
            // Simple connectivity test
            CompletableFuture<ApiResponse<Map>> healthCheck = httpClient.get("/health", Map.class);
            healthCheck.get(5, TimeUnit.SECONDS); // 5 second timeout for health check
            
            logger.info("API connectivity verified successfully");
            
        } catch (Exception e) {
            logger.warn("API connectivity verification failed: " + e.getMessage());
            // Don't fail initialization for connectivity issues
        }
    }
    
    /**
     * Static utility methods
     */
    
    public static String getVersion() {
        return SDK_VERSION;
    }
    
    public static String getUserAgent() {
        return USER_AGENT;
    }
    
    /**
     * Create SDK instance with minimal configuration
     */
    public static AinflueSdk create(String apiKey) {
        return builder()
            .apiKey(apiKey)
            .build();
    }
    
    /**
     * Create SDK instance with custom base URL
     */
    public static AinflueSdk create(String apiKey, String baseUrl) {
        return builder()
            .apiKey(apiKey)
            .baseUrl(baseUrl)
            .build();
    }
    
    /**
     * Example usage method for documentation
     */
    public static void exampleUsage() {
        // Example 1: Basic usage
        AinflueSdk sdk = AinflueSdk.create("your-api-key");
        
        try {
            // Initialize SDK
            sdk.initialize().get();
            
            // Get current user
            UserProfile user = sdk.getCurrentUser().get();
            System.out.println("Current user: " + user.getUsername());
            
            // Upload content
            byte[] content = "Hello, World!".getBytes();
            ContentItem item = sdk.uploadContent(
                content, 
                "hello.txt", 
                "text/plain", 
                Map.of("description", "Test upload")
            ).get();
            
            System.out.println("Uploaded content: " + item.getId());
            
            // Process with AI
            String jobId = sdk.processWithAI(
                item.getId(), 
                "auto_tagging", 
                Map.of("confidence_threshold", 0.8)
            ).get();
            
            System.out.println("Processing job: " + jobId);
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            // Always close SDK
            sdk.close();
        }
        
        // Example 2: Advanced configuration
        AinflueSdk advancedSdk = AinflueSdk.builder()
            .apiKey("your-api-key")
            .baseUrl("https://api-staging.ainflue.com")
            .timeout(60, TimeUnit.SECONDS)
            .maxRetries(5)
            .enableMetrics(true)
            .environment("staging")
            .build();
    }
}