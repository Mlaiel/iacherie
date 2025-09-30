package com.ainflue.sdk.config;

/**
 * SDK Configuration Class
 * 
 * Multi-expert implementation:
 * - Backend Senior: Robust configuration management with validation
 * - Security: Secure configuration handling with encryption support
 * - DevOps: Environment-specific configuration and monitoring settings
 * - DBA: Connection pooling and database-related configuration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 */

import com.ainflue.sdk.exceptions.ConfigurationException;

import java.time.Duration;
import java.util.Map;
import java.util.HashMap;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

/**
 * Immutable configuration class for the Ainflue SDK
 */
public final class SdkConfiguration {
    
    // Core API settings
    private final String apiKey;
    private final String baseUrl;
    private final String environment;
    private final String region;
    
    // Network and timeout settings (Backend Senior expertise)
    private final int timeout;
    private final int connectTimeout;
    private final int readTimeout;
    private final int writeTimeout;
    private final int maxRetries;
    private final Duration retryDelay;
    private final double retryBackoffMultiplier;
    
    // Connection pooling settings (DBA expertise)
    private final int maxConnections;
    private final int maxConnectionsPerRoute;
    private final Duration connectionKeepAlive;
    private final Duration connectionIdleTimeout;
    
    // Security settings (Security expertise)
    private final boolean enableTls;
    private final boolean validateCertificates;
    private final String[] tlsVersions;
    private final String[] cipherSuites;
    private final boolean enableTokenRefresh;
    private final Duration tokenRefreshBuffer;
    
    // Monitoring and metrics (DevOps expertise)
    private final boolean enableMetrics;
    private final boolean enableLogging;
    private final String logLevel;
    private final boolean enableTracing;
    private final String tracingEndpoint;
    private final Duration metricsCollectionInterval;
    
    // Feature flags (Lead Dev IA expertise)
    private final Map<String, Boolean> featureFlags;
    
    // Custom headers and user agent
    private final Map<String, String> customHeaders;
    private final String userAgent;
    
    // Rate limiting
    private final int rateLimitPerHour;
    private final boolean enableRateLimiting;
    
    // Caching settings
    private final boolean enableCaching;
    private final Duration cacheTimeout;
    private final int maxCacheSize;
    
    private SdkConfiguration(Builder builder) {
        // Core settings
        this.apiKey = builder.apiKey;
        this.baseUrl = builder.baseUrl;
        this.environment = builder.environment;
        this.region = builder.region;
        
        // Network settings
        this.timeout = builder.timeout;
        this.connectTimeout = builder.connectTimeout;
        this.readTimeout = builder.readTimeout;
        this.writeTimeout = builder.writeTimeout;
        this.maxRetries = builder.maxRetries;
        this.retryDelay = builder.retryDelay;
        this.retryBackoffMultiplier = builder.retryBackoffMultiplier;
        
        // Connection pooling
        this.maxConnections = builder.maxConnections;
        this.maxConnectionsPerRoute = builder.maxConnectionsPerRoute;
        this.connectionKeepAlive = builder.connectionKeepAlive;
        this.connectionIdleTimeout = builder.connectionIdleTimeout;
        
        // Security
        this.enableTls = builder.enableTls;
        this.validateCertificates = builder.validateCertificates;
        this.tlsVersions = builder.tlsVersions.clone();
        this.cipherSuites = builder.cipherSuites.clone();
        this.enableTokenRefresh = builder.enableTokenRefresh;
        this.tokenRefreshBuffer = builder.tokenRefreshBuffer;
        
        // Monitoring
        this.enableMetrics = builder.enableMetrics;
        this.enableLogging = builder.enableLogging;
        this.logLevel = builder.logLevel;
        this.enableTracing = builder.enableTracing;
        this.tracingEndpoint = builder.tracingEndpoint;
        this.metricsCollectionInterval = builder.metricsCollectionInterval;
        
        // Feature flags
        this.featureFlags = new HashMap<>(builder.featureFlags);
        
        // Headers
        this.customHeaders = new HashMap<>(builder.customHeaders);
        this.userAgent = builder.userAgent;
        
        // Rate limiting
        this.rateLimitPerHour = builder.rateLimitPerHour;
        this.enableRateLimiting = builder.enableRateLimiting;
        
        // Caching
        this.enableCaching = builder.enableCaching;
        this.cacheTimeout = builder.cacheTimeout;
        this.maxCacheSize = builder.maxCacheSize;
        
        // Validate configuration
        validate();
    }
    
    /**
     * Builder pattern for configuration (Backend Senior expertise)
     */
    public static class Builder {
        // Required fields
        private String apiKey;
        
        // Optional fields with defaults
        private String baseUrl = "https://api.ainflue.com";
        private String environment = "production";
        private String region = "us-east-1";
        
        // Network defaults
        private int timeout = 30000; // 30 seconds
        private int connectTimeout = 10000; // 10 seconds
        private int readTimeout = 30000; // 30 seconds
        private int writeTimeout = 30000; // 30 seconds
        private int maxRetries = 3;
        private Duration retryDelay = Duration.ofSeconds(1);
        private double retryBackoffMultiplier = 2.0;
        
        // Connection pooling defaults
        private int maxConnections = 100;
        private int maxConnectionsPerRoute = 20;
        private Duration connectionKeepAlive = Duration.ofMinutes(5);
        private Duration connectionIdleTimeout = Duration.ofMinutes(2);
        
        // Security defaults
        private boolean enableTls = true;
        private boolean validateCertificates = true;
        private String[] tlsVersions = {"TLSv1.2", "TLSv1.3"};
        private String[] cipherSuites = {}; // Use system defaults
        private boolean enableTokenRefresh = true;
        private Duration tokenRefreshBuffer = Duration.ofMinutes(5);
        
        // Monitoring defaults
        private boolean enableMetrics = true;
        private boolean enableLogging = true;
        private String logLevel = "INFO";
        private boolean enableTracing = false;
        private String tracingEndpoint = null;
        private Duration metricsCollectionInterval = Duration.ofMinutes(1);
        
        // Feature flags
        private Map<String, Boolean> featureFlags = new HashMap<>();
        
        // Headers
        private Map<String, String> customHeaders = new HashMap<>();
        private String userAgent = "Ainflue-Java-SDK/1.0.0";
        
        // Rate limiting defaults
        private int rateLimitPerHour = 10000;
        private boolean enableRateLimiting = true;
        
        // Caching defaults
        private boolean enableCaching = true;
        private Duration cacheTimeout = Duration.ofMinutes(5);
        private int maxCacheSize = 1000;
        
        public Builder apiKey(String apiKey) {
            this.apiKey = apiKey;
            return this;
        }
        
        public Builder baseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }
        
        public Builder environment(String environment) {
            this.environment = environment;
            return this;
        }
        
        public Builder region(String region) {
            this.region = region;
            return this;
        }
        
        public Builder timeout(int timeout) {
            this.timeout = timeout;
            return this;
        }
        
        public Builder timeout(int timeout, TimeUnit unit) {
            this.timeout = (int) unit.toMillis(timeout);
            return this;
        }
        
        public Builder connectTimeout(int connectTimeout) {
            this.connectTimeout = connectTimeout;
            return this;
        }
        
        public Builder readTimeout(int readTimeout) {
            this.readTimeout = readTimeout;
            return this;
        }
        
        public Builder writeTimeout(int writeTimeout) {
            this.writeTimeout = writeTimeout;
            return this;
        }
        
        public Builder maxRetries(int maxRetries) {
            this.maxRetries = maxRetries;
            return this;
        }
        
        public Builder retryDelay(Duration retryDelay) {
            this.retryDelay = retryDelay;
            return this;
        }
        
        public Builder retryBackoffMultiplier(double retryBackoffMultiplier) {
            this.retryBackoffMultiplier = retryBackoffMultiplier;
            return this;
        }
        
        public Builder maxConnections(int maxConnections) {
            this.maxConnections = maxConnections;
            return this;
        }
        
        public Builder maxConnectionsPerRoute(int maxConnectionsPerRoute) {
            this.maxConnectionsPerRoute = maxConnectionsPerRoute;
            return this;
        }
        
        public Builder connectionKeepAlive(Duration connectionKeepAlive) {
            this.connectionKeepAlive = connectionKeepAlive;
            return this;
        }
        
        public Builder connectionIdleTimeout(Duration connectionIdleTimeout) {
            this.connectionIdleTimeout = connectionIdleTimeout;
            return this;
        }
        
        public Builder enableTls(boolean enableTls) {
            this.enableTls = enableTls;
            return this;
        }
        
        public Builder validateCertificates(boolean validateCertificates) {
            this.validateCertificates = validateCertificates;
            return this;
        }
        
        public Builder tlsVersions(String... tlsVersions) {
            this.tlsVersions = tlsVersions.clone();
            return this;
        }
        
        public Builder cipherSuites(String... cipherSuites) {
            this.cipherSuites = cipherSuites.clone();
            return this;
        }
        
        public Builder enableTokenRefresh(boolean enableTokenRefresh) {
            this.enableTokenRefresh = enableTokenRefresh;
            return this;
        }
        
        public Builder tokenRefreshBuffer(Duration tokenRefreshBuffer) {
            this.tokenRefreshBuffer = tokenRefreshBuffer;
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
        
        public Builder logLevel(String logLevel) {
            this.logLevel = logLevel;
            return this;
        }
        
        public Builder enableTracing(boolean enableTracing) {
            this.enableTracing = enableTracing;
            return this;
        }
        
        public Builder tracingEndpoint(String tracingEndpoint) {
            this.tracingEndpoint = tracingEndpoint;
            return this;
        }
        
        public Builder metricsCollectionInterval(Duration metricsCollectionInterval) {
            this.metricsCollectionInterval = metricsCollectionInterval;
            return this;
        }
        
        public Builder featureFlag(String flag, boolean enabled) {
            this.featureFlags.put(flag, enabled);
            return this;
        }
        
        public Builder featureFlags(Map<String, Boolean> featureFlags) {
            this.featureFlags.putAll(featureFlags);
            return this;
        }
        
        public Builder customHeader(String name, String value) {
            this.customHeaders.put(name, value);
            return this;
        }
        
        public Builder customHeaders(Map<String, String> customHeaders) {
            this.customHeaders.putAll(customHeaders);
            return this;
        }
        
        public Builder userAgent(String userAgent) {
            this.userAgent = userAgent;
            return this;
        }
        
        public Builder rateLimitPerHour(int rateLimitPerHour) {
            this.rateLimitPerHour = rateLimitPerHour;
            return this;
        }
        
        public Builder enableRateLimiting(boolean enableRateLimiting) {
            this.enableRateLimiting = enableRateLimiting;
            return this;
        }
        
        public Builder enableCaching(boolean enableCaching) {
            this.enableCaching = enableCaching;
            return this;
        }
        
        public Builder cacheTimeout(Duration cacheTimeout) {
            this.cacheTimeout = cacheTimeout;
            return this;
        }
        
        public Builder maxCacheSize(int maxCacheSize) {
            this.maxCacheSize = maxCacheSize;
            return this;
        }
        
        public SdkConfiguration build() {
            return new SdkConfiguration(this);
        }
    }
    
    /**
     * Create builder instance
     */
    public static Builder builder() {
        return new Builder();
    }
    
    /**
     * Validation method (Security expertise)
     */
    private void validate() {
        if (apiKey == null || apiKey.trim().isEmpty()) {
            throw new ConfigurationException("API key is required");
        }
        
        if (baseUrl == null || baseUrl.trim().isEmpty()) {
            throw new ConfigurationException("Base URL is required");
        }
        
        if (!baseUrl.startsWith("http://") && !baseUrl.startsWith("https://")) {
            throw new ConfigurationException("Base URL must start with http:// or https://");
        }
        
        if (enableTls && baseUrl.startsWith("http://") && !baseUrl.contains("localhost")) {
            throw new ConfigurationException("TLS is enabled but base URL uses HTTP (not HTTPS)");
        }
        
        if (timeout <= 0) {
            throw new ConfigurationException("Timeout must be positive");
        }
        
        if (maxRetries < 0) {
            throw new ConfigurationException("Max retries cannot be negative");
        }
        
        if (retryBackoffMultiplier <= 1.0) {
            throw new ConfigurationException("Retry backoff multiplier must be greater than 1.0");
        }
        
        if (maxConnections <= 0) {
            throw new ConfigurationException("Max connections must be positive");
        }
        
        if (maxConnectionsPerRoute <= 0 || maxConnectionsPerRoute > maxConnections) {
            throw new ConfigurationException("Max connections per route must be positive and <= max connections");
        }
        
        if (!isValidLogLevel(logLevel)) {
            throw new ConfigurationException("Invalid log level: " + logLevel);
        }
        
        if (rateLimitPerHour <= 0) {
            throw new ConfigurationException("Rate limit per hour must be positive");
        }
        
        if (maxCacheSize <= 0) {
            throw new ConfigurationException("Max cache size must be positive");
        }
    }
    
    private boolean isValidLogLevel(String level) {
        return level != null && 
               (level.equals("TRACE") || level.equals("DEBUG") || level.equals("INFO") || 
                level.equals("WARN") || level.equals("ERROR") || level.equals("OFF"));
    }
    
    // Getter methods
    public String getApiKey() { return apiKey; }
    public String getBaseUrl() { return baseUrl; }
    public String getEnvironment() { return environment; }
    public String getRegion() { return region; }
    
    public int getTimeout() { return timeout; }
    public int getConnectTimeout() { return connectTimeout; }
    public int getReadTimeout() { return readTimeout; }
    public int getWriteTimeout() { return writeTimeout; }
    public int getMaxRetries() { return maxRetries; }
    public Duration getRetryDelay() { return retryDelay; }
    public double getRetryBackoffMultiplier() { return retryBackoffMultiplier; }
    
    public int getMaxConnections() { return maxConnections; }
    public int getMaxConnectionsPerRoute() { return maxConnectionsPerRoute; }
    public Duration getConnectionKeepAlive() { return connectionKeepAlive; }
    public Duration getConnectionIdleTimeout() { return connectionIdleTimeout; }
    
    public boolean isTlsEnabled() { return enableTls; }
    public boolean shouldValidateCertificates() { return validateCertificates; }
    public String[] getTlsVersions() { return tlsVersions.clone(); }
    public String[] getCipherSuites() { return cipherSuites.clone(); }
    public boolean isTokenRefreshEnabled() { return enableTokenRefresh; }
    public Duration getTokenRefreshBuffer() { return tokenRefreshBuffer; }
    
    public boolean isMetricsEnabled() { return enableMetrics; }
    public boolean isLoggingEnabled() { return enableLogging; }
    public String getLogLevel() { return logLevel; }
    public boolean isTracingEnabled() { return enableTracing; }
    public String getTracingEndpoint() { return tracingEndpoint; }
    public Duration getMetricsCollectionInterval() { return metricsCollectionInterval; }
    
    public Map<String, Boolean> getFeatureFlags() { return new HashMap<>(featureFlags); }
    public boolean isFeatureEnabled(String feature) { return featureFlags.getOrDefault(feature, false); }
    
    public Map<String, String> getCustomHeaders() { return new HashMap<>(customHeaders); }
    public String getUserAgent() { return userAgent; }
    
    public int getRateLimitPerHour() { return rateLimitPerHour; }
    public boolean isRateLimitingEnabled() { return enableRateLimiting; }
    
    public boolean isCachingEnabled() { return enableCaching; }
    public Duration getCacheTimeout() { return cacheTimeout; }
    public int getMaxCacheSize() { return maxCacheSize; }
    
    /**
     * Create configuration for different environments
     */
    public static SdkConfiguration forDevelopment(String apiKey) {
        return builder()
            .apiKey(apiKey)
            .baseUrl("https://api-dev.ainflue.com")
            .environment("development")
            .enableLogging(true)
            .logLevel("DEBUG")
            .validateCertificates(false)
            .build();
    }
    
    public static SdkConfiguration forStaging(String apiKey) {
        return builder()
            .apiKey(apiKey)
            .baseUrl("https://api-staging.ainflue.com")
            .environment("staging")
            .enableLogging(true)
            .logLevel("INFO")
            .enableTracing(true)
            .build();
    }
    
    public static SdkConfiguration forProduction(String apiKey) {
        return builder()
            .apiKey(apiKey)
            .baseUrl("https://api.ainflue.com")
            .environment("production")
            .enableLogging(true)
            .logLevel("WARN")
            .enableMetrics(true)
            .enableTracing(false)
            .build();
    }
    
    @Override
    public String toString() {
        return "SdkConfiguration{" +
            "baseUrl='" + baseUrl + '\'' +
            ", environment='" + environment + '\'' +
            ", region='" + region + '\'' +
            ", timeout=" + timeout +
            ", maxRetries=" + maxRetries +
            ", enableMetrics=" + enableMetrics +
            ", enableLogging=" + enableLogging +
            ", logLevel='" + logLevel + '\'' +
            '}';
    }
}