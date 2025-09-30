package com.ainflue.sdk.metrics;

/**
 * Request Metrics Collection for Ainflue Java SDK
 * Enterprise monitoring and performance tracking
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: DevOps + ML Engineer + Lead Dev IA
 */

import com.ainflue.sdk.utils.Logger;

import java.time.Instant;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;

/**
 * Request metrics collector with real-time analytics
 */
public class RequestMetrics {
    
    private static final Logger logger = Logger.getLogger(RequestMetrics.class);
    private static final int MAX_RECENT_REQUESTS = 1000;
    
    // Atomic counters for thread-safe metrics
    private final AtomicLong totalRequests = new AtomicLong(0);
    private final AtomicLong successfulRequests = new AtomicLong(0);
    private final AtomicLong failedRequests = new AtomicLong(0);
    private final AtomicLong totalResponseTime = new AtomicLong(0);
    
    // Status code counters
    private final ConcurrentHashMap<Integer, AtomicLong> statusCodeCounts = new ConcurrentHashMap<>();
    
    // Method counters
    private final ConcurrentHashMap<String, AtomicLong> methodCounts = new ConcurrentHashMap<>();
    
    // Error type counters
    private final ConcurrentHashMap<String, AtomicLong> errorCounts = new ConcurrentHashMap<>();
    
    // Recent requests for sliding window analytics
    private final List<RequestRecord> recentRequests = Collections.synchronizedList(new ArrayList<>());
    
    // Performance thresholds
    private final AtomicReference<PerformanceThresholds> thresholds = new AtomicReference<>(
        new PerformanceThresholds(1000, 5000, 10000) // 1s, 5s, 10s
    );
    
    /**
     * Record a successful request
     * Implementation: DevOps + ML Engineer
     */
    public void recordRequest(String method, String url, int statusCode, long responseTimeMs) {
        totalRequests.incrementAndGet();
        totalResponseTime.addAndGet(responseTimeMs);
        
        // Update status code counters
        statusCodeCounts.computeIfAbsent(statusCode, k -> new AtomicLong(0)).incrementAndGet();
        
        // Update method counters
        methodCounts.computeIfAbsent(method.toUpperCase(), k -> new AtomicLong(0)).incrementAndGet();
        
        // Track success/failure
        if (statusCode >= 200 && statusCode < 400) {
            successfulRequests.incrementAndGet();
        } else {
            failedRequests.incrementAndGet();
        }
        
        // Record for sliding window analysis
        RequestRecord record = new RequestRecord(method, sanitizeUrl(url), statusCode, responseTimeMs, Instant.now());
        addRecentRequest(record);
        
        // Performance analysis
        analyzePerformance(record);
        
        logger.debug("Request recorded: {} {} - {} ({}ms)", method, url, statusCode, responseTimeMs);
    }
    
    /**
     * Record a request failure
     * Implementation: DevOps + Lead Dev IA
     */
    public void recordFailure(String method, String url, String errorType) {
        totalRequests.incrementAndGet();
        failedRequests.incrementAndGet();
        
        // Update method counters
        methodCounts.computeIfAbsent(method.toUpperCase(), k -> new AtomicLong(0)).incrementAndGet();
        
        // Update error type counters
        errorCounts.computeIfAbsent(errorType, k -> new AtomicLong(0)).incrementAndGet();
        
        // Record for sliding window analysis
        RequestRecord record = new RequestRecord(method, sanitizeUrl(url), 0, 0, Instant.now(), errorType);
        addRecentRequest(record);
        
        logger.warn("Request failure recorded: {} {} - {}", method, url, errorType);
    }
    
    /**
     * Get current metrics summary
     * Implementation: DevOps + ML Engineer
     */
    public MetricsSummary getMetricsSummary() {
        long total = totalRequests.get();
        long successful = successfulRequests.get();
        long failed = failedRequests.get();
        long totalTime = totalResponseTime.get();
        
        double successRate = total > 0 ? (double) successful / total * 100 : 0;
        double averageResponseTime = successful > 0 ? (double) totalTime / successful : 0;
        
        return new MetricsSummary(
            total,
            successful,
            failed,
            successRate,
            averageResponseTime,
            getCurrentThroughput(),
            getRecentErrorRate(),
            getSlowRequestsCount()
        );
    }
    
    /**
     * Get performance insights using ML-style analysis
     * Implementation: ML Engineer + Lead Dev IA
     */
    public PerformanceInsights getPerformanceInsights() {
        List<RequestRecord> recent = getRecentRequests(300); // Last 5 minutes
        
        if (recent.isEmpty()) {
            return new PerformanceInsights();
        }
        
        // Calculate percentiles
        List<Long> responseTimes = recent.stream()
            .filter(r -> r.statusCode >= 200 && r.statusCode < 400)
            .map(r -> r.responseTimeMs)
            .sorted()
            .toList();
        
        PerformanceInsights insights = new PerformanceInsights();
        
        if (!responseTimes.isEmpty()) {
            insights.p50 = calculatePercentile(responseTimes, 50);
            insights.p95 = calculatePercentile(responseTimes, 95);
            insights.p99 = calculatePercentile(responseTimes, 99);
            insights.min = responseTimes.get(0);
            insights.max = responseTimes.get(responseTimes.size() - 1);
        }
        
        // Analyze trends
        insights.trend = analyzeTrend(recent);
        insights.recommendations = generateRecommendations(recent);
        
        return insights;
    }
    
    /**
     * Sanitize URL for metrics (remove sensitive data)
     * Implementation: Security + DevOps
     */
    private String sanitizeUrl(String url) {
        if (url == null) return "unknown";
        
        // Remove query parameters and replace IDs with placeholders
        String sanitized = url.split("\\?")[0];
        sanitized = sanitized.replaceAll("/\\d+", "/:id");
        sanitized = sanitized.replaceAll("/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", "/:uuid");
        
        return sanitized;
    }
    
    /**
     * Add request to recent requests with size limit
     * Implementation: DevOps + DBA
     */
    private void addRecentRequest(RequestRecord record) {
        synchronized (recentRequests) {
            recentRequests.add(record);
            
            // Maintain size limit
            while (recentRequests.size() > MAX_RECENT_REQUESTS) {
                recentRequests.remove(0);
            }
        }
    }
    
    /**
     * Analyze request performance and trigger alerts
     * Implementation: Lead Dev IA + DevOps
     */
    private void analyzePerformance(RequestRecord record) {
        PerformanceThresholds current = thresholds.get();
        
        if (record.responseTimeMs > current.criticalThresholdMs) {
            logger.warn("Critical performance detected: {} {} took {}ms", 
                       record.method, record.url, record.responseTimeMs);
        } else if (record.responseTimeMs > current.warningThresholdMs) {
            logger.info("Slow request detected: {} {} took {}ms", 
                       record.method, record.url, record.responseTimeMs);
        }
    }
    
    /**
     * Calculate percentile from sorted list
     * Implementation: ML Engineer
     */
    private long calculatePercentile(List<Long> sortedValues, int percentile) {
        if (sortedValues.isEmpty()) return 0;
        
        int index = (int) Math.ceil((percentile / 100.0) * sortedValues.size()) - 1;
        index = Math.max(0, Math.min(index, sortedValues.size() - 1));
        
        return sortedValues.get(index);
    }
    
    /**
     * Analyze performance trend
     * Implementation: ML Engineer + Lead Dev IA
     */
    private String analyzeTrend(List<RequestRecord> recent) {
        if (recent.size() < 10) return "insufficient_data";
        
        // Simple trend analysis - compare first half vs second half
        int midPoint = recent.size() / 2;
        double firstHalfAvg = recent.subList(0, midPoint).stream()
            .filter(r -> r.statusCode >= 200 && r.statusCode < 400)
            .mapToLong(r -> r.responseTimeMs)
            .average()
            .orElse(0);
            
        double secondHalfAvg = recent.subList(midPoint, recent.size()).stream()
            .filter(r -> r.statusCode >= 200 && r.statusCode < 400)
            .mapToLong(r -> r.responseTimeMs)
            .average()
            .orElse(0);
        
        double change = (secondHalfAvg - firstHalfAvg) / firstHalfAvg * 100;
        
        if (Math.abs(change) < 5) return "stable";
        return change > 0 ? "degrading" : "improving";
    }
    
    /**
     * Generate performance recommendations
     * Implementation: Lead Dev IA + ML Engineer
     */
    private List<String> generateRecommendations(List<RequestRecord> recent) {
        List<String> recommendations = new ArrayList<>();
        
        double errorRate = getRecentErrorRate();
        if (errorRate > 5) {
            recommendations.add("High error rate detected (" + String.format("%.1f", errorRate) + "%). Check service health.");
        }
        
        long slowRequests = getSlowRequestsCount();
        if (slowRequests > recent.size() * 0.1) {
            recommendations.add("High number of slow requests. Consider optimizing or scaling.");
        }
        
        // Check for specific patterns
        Map<String, Long> errorsByType = recent.stream()
            .filter(r -> r.errorType != null)
            .collect(java.util.stream.Collectors.groupingBy(
                r -> r.errorType,
                java.util.stream.Collectors.counting()
            ));
        
        errorsByType.entrySet().stream()
            .filter(e -> e.getValue() > 5)
            .forEach(e -> recommendations.add("Frequent " + e.getKey() + " errors detected. Check connectivity and configuration."));
        
        return recommendations;
    }
    
    private double getCurrentThroughput() {
        // Calculate requests per second based on recent activity
        List<RequestRecord> lastMinute = getRecentRequests(60);
        return lastMinute.size() / 60.0;
    }
    
    private double getRecentErrorRate() {
        List<RequestRecord> recent = getRecentRequests(300); // Last 5 minutes
        if (recent.isEmpty()) return 0;
        
        long errors = recent.stream()
            .mapToLong(r -> (r.statusCode >= 400 || r.errorType != null) ? 1 : 0)
            .sum();
            
        return (double) errors / recent.size() * 100;
    }
    
    private long getSlowRequestsCount() {
        PerformanceThresholds current = thresholds.get();
        return getRecentRequests(300).stream()
            .mapToLong(r -> r.responseTimeMs > current.warningThresholdMs ? 1 : 0)
            .sum();
    }
    
    private List<RequestRecord> getRecentRequests(int seconds) {
        Instant cutoff = Instant.now().minusSeconds(seconds);
        synchronized (recentRequests) {
            return recentRequests.stream()
                .filter(r -> r.timestamp.isAfter(cutoff))
                .toList();
        }
    }
    
    // Data classes
    public static class MetricsSummary {
        public final long totalRequests;
        public final long successfulRequests;
        public final long failedRequests;
        public final double successRate;
        public final double averageResponseTime;
        public final double currentThroughput;
        public final double recentErrorRate;
        public final long slowRequestsCount;
        
        public MetricsSummary(long totalRequests, long successfulRequests, long failedRequests,
                            double successRate, double averageResponseTime, double currentThroughput,
                            double recentErrorRate, long slowRequestsCount) {
            this.totalRequests = totalRequests;
            this.successfulRequests = successfulRequests;
            this.failedRequests = failedRequests;
            this.successRate = successRate;
            this.averageResponseTime = averageResponseTime;
            this.currentThroughput = currentThroughput;
            this.recentErrorRate = recentErrorRate;
            this.slowRequestsCount = slowRequestsCount;
        }
    }
    
    public static class PerformanceInsights {
        public long p50, p95, p99, min, max;
        public String trend;
        public List<String> recommendations = new ArrayList<>();
    }
    
    public static class PerformanceThresholds {
        public final long normalThresholdMs;
        public final long warningThresholdMs;
        public final long criticalThresholdMs;
        
        public PerformanceThresholds(long normal, long warning, long critical) {
            this.normalThresholdMs = normal;
            this.warningThresholdMs = warning;
            this.criticalThresholdMs = critical;
        }
    }
    
    private static class RequestRecord {
        public final String method;
        public final String url;
        public final int statusCode;
        public final long responseTimeMs;
        public final Instant timestamp;
        public final String errorType;
        
        public RequestRecord(String method, String url, int statusCode, long responseTimeMs, Instant timestamp) {
            this(method, url, statusCode, responseTimeMs, timestamp, null);
        }
        
        public RequestRecord(String method, String url, int statusCode, long responseTimeMs, Instant timestamp, String errorType) {
            this.method = method;
            this.url = url;
            this.statusCode = statusCode;
            this.responseTimeMs = responseTimeMs;
            this.timestamp = timestamp;
            this.errorType = errorType;
        }
    }
}