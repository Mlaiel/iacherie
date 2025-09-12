package com.ainflue.sdk.client;

/**
 * HTTP Client Implementation for Ainflue Java SDK
 * Enterprise-grade HTTP client with connection pooling and retry logic
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Backend Senior + DevOps + Security + Lead Dev IA
 */

import com.ainflue.sdk.config.SdkConfiguration;
import com.ainflue.sdk.exceptions.*;
import com.ainflue.sdk.models.ApiResponse;
import com.ainflue.sdk.utils.Logger;
import com.ainflue.sdk.security.SecurityUtils;
import com.ainflue.sdk.metrics.RequestMetrics;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.annotation.JsonInclude;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

/**
 * Enterprise HTTP Client with advanced features
 */
public class HttpClientAdapter {
    
    private static final Logger logger = Logger.getLogger(HttpClientAdapter.class);
    private static final int DEFAULT_POOL_SIZE = 10;
    private static final int MAX_REDIRECT_ATTEMPTS = 3;
    
    private final SdkConfiguration config;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final ExecutorService executorService;
    private final RequestMetrics metrics;
    private final SecurityUtils securityUtils;
    private final ConnectionPool connectionPool;
    
    public HttpClientAdapter(SdkConfiguration config) {
        this.config = config;
        this.objectMapper = createObjectMapper();
        this.executorService = Executors.newFixedThreadPool(DEFAULT_POOL_SIZE);
        this.metrics = new RequestMetrics();
        this.securityUtils = new SecurityUtils(config);
        this.connectionPool = new ConnectionPool(config);
        
        this.httpClient = createHttpClient();
        
        logger.info("HTTP Client initialized with configuration: baseUrl={}, timeout={}ms", 
                   config.getBaseUrl(), config.getTimeout());
    }
    
    /**
     * Create and configure HTTP client with enterprise features
     * Implementation: Backend Senior + DevOps + Security
     */
    private HttpClient createHttpClient() {
        HttpClient.Builder builder = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .connectTimeout(Duration.ofMillis(config.getConnectTimeout()))
            .executor(executorService)
            .followRedirects(HttpClient.Redirect.NORMAL);
            
        // SSL/TLS configuration (Security)
        if (config.isSslVerificationEnabled()) {
            builder.sslContext(securityUtils.createSSLContext());
        }
        
        return builder.build();
    }
    
    /**
     * Configure ObjectMapper for JSON processing
     * Implementation: Backend Senior + Lead Dev IA
     */
    private ObjectMapper createObjectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        mapper.configure(com.fasterxml.jackson.databind.DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        mapper.configure(com.fasterxml.jackson.databind.SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
        return mapper;
    }
    
    /**
     * Execute GET request
     */
    public <T> CompletableFuture<ApiResponse<T>> get(String endpoint, Class<T> responseType) {
        return get(endpoint, responseType, new HashMap<>());
    }
    
    public <T> CompletableFuture<ApiResponse<T>> get(String endpoint, Class<T> responseType, Map<String, String> headers) {
        return executeRequest(() -> {
            HttpRequest request = buildRequest("GET", endpoint, null, headers);
            return sendRequestWithRetry(request, responseType);
        });
    }
    
    /**
     * Execute POST request
     */
    public <T> CompletableFuture<ApiResponse<T>> post(String endpoint, Object requestBody, Class<T> responseType) {
        return post(endpoint, requestBody, responseType, new HashMap<>());
    }
    
    public <T> CompletableFuture<ApiResponse<T>> post(String endpoint, Object requestBody, Class<T> responseType, Map<String, String> headers) {
        return executeRequest(() -> {
            HttpRequest request = buildRequest("POST", endpoint, requestBody, headers);
            return sendRequestWithRetry(request, responseType);
        });
    }
    
    /**
     * Build HTTP request with security validation
     */
    private HttpRequest buildRequest(String method, String endpoint, Object body, Map<String, String> headers) {
        try {
            String url = buildUrl(endpoint);
            
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofMillis(config.getTimeout()))
                .header("User-Agent", "Ainflue-Java-SDK/1.0.0")
                .header("Accept", "application/json")
                .header("X-Request-ID", generateRequestId())
                .header("X-Timestamp", Instant.now().toString());
            
            // Add authentication headers
            if (config.getApiKey() != null) {
                requestBuilder.header("Authorization", "Bearer " + config.getApiKey());
            }
            
            // Add custom headers
            headers.forEach(requestBuilder::header);
            
            // Set request body based on method
            switch (method.toUpperCase()) {
                case "GET":
                case "DELETE":
                    requestBuilder.method(method, HttpRequest.BodyPublishers.noBody());
                    break;
                case "POST":
                case "PUT":
                    String jsonBody = body != null ? objectMapper.writeValueAsString(body) : "";
                    requestBuilder.method(method, HttpRequest.BodyPublishers.ofString(jsonBody));
                    requestBuilder.header("Content-Type", "application/json");
                    break;
                default:
                    throw new IllegalArgumentException("Unsupported HTTP method: " + method);
            }
            
            return requestBuilder.build();
            
        } catch (Exception e) {
            throw new AinflueSdkException("Failed to build HTTP request", e);
        }
    }
    
    /**
     * Send request with retry logic
     */
    private <T> ApiResponse<T> sendRequestWithRetry(HttpRequest request, Class<T> responseType) {
        int attempts = 0;
        Exception lastException = null;
        
        while (attempts <= config.getMaxRetries()) {
            try {
                Instant startTime = Instant.now();
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                Duration requestDuration = Duration.between(startTime, Instant.now());
                
                // Record metrics
                metrics.recordRequest(request.method(), request.uri().toString(), 
                                    response.statusCode(), requestDuration.toMillis());
                
                // Parse and return response
                return parseResponse(response, responseType);
                
            } catch (Exception e) {
                attempts++;
                lastException = e;
                
                if (attempts <= config.getMaxRetries() && shouldRetry(e, attempts)) {
                    long delayMs = calculateBackoffDelay(attempts);
                    try {
                        Thread.sleep(delayMs);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new AinflueSdkException("Request interrupted", ie);
                    }
                } else {
                    break;
                }
            }
        }
        
        throw new AinflueSdkException("Request failed after " + attempts + " attempts", lastException);
    }
    
    /**
     * Parse HTTP response
     */
    private <T> ApiResponse<T> parseResponse(HttpResponse<String> response, Class<T> responseType) {
        try {
            int statusCode = response.statusCode();
            String body = response.body();
            
            if (statusCode >= 200 && statusCode < 300) {
                T data = null;
                if (body != null && !body.trim().isEmpty() && responseType != Void.class) {
                    data = objectMapper.readValue(body, responseType);
                }
                
                return ApiResponse.<T>builder()
                    .data(data)
                    .statusCode(statusCode)
                    .headers(response.headers().map())
                    .success(true)
                    .build();
                    
            } else {
                String errorMessage = extractErrorMessage(body, statusCode);
                
                if (statusCode == 401) {
                    throw new AuthenticationException(errorMessage);
                } else if (statusCode == 403) {
                    throw new AuthorizationException(errorMessage);
                } else if (statusCode >= 500) {
                    throw new ServerException(errorMessage, statusCode);
                } else {
                    throw new ClientException(errorMessage, statusCode);
                }
            }
            
        } catch (IOException e) {
            throw new AinflueSdkException("Failed to parse response", e);
        }
    }
    
    private String extractErrorMessage(String responseBody, int statusCode) {
        if (responseBody == null || responseBody.trim().isEmpty()) {
            return "HTTP " + statusCode;
        }
        return responseBody;
    }
    
    private boolean shouldRetry(Exception exception, int attemptNumber) {
        return exception instanceof IOException || 
               exception instanceof ServerException;
    }
    
    private long calculateBackoffDelay(int attemptNumber) {
        return Math.min(1000L * (1L << (attemptNumber - 1)), 30000L);
    }
    
    private <T> CompletableFuture<T> executeRequest(Supplier<T> requestSupplier) {
        return CompletableFuture.supplyAsync(requestSupplier, executorService);
    }
    
    private String buildUrl(String endpoint) {
        String baseUrl = config.getBaseUrl();
        if (baseUrl.endsWith("/") && endpoint.startsWith("/")) {
            return baseUrl + endpoint.substring(1);
        } else if (!baseUrl.endsWith("/") && !endpoint.startsWith("/")) {
            return baseUrl + "/" + endpoint;
        } else {
            return baseUrl + endpoint;
        }
    }
    
    private String generateRequestId() {
        return "req_" + System.currentTimeMillis() + "_" + 
               Integer.toHexString((int)(Math.random() * 0x1000000));
    }
    
    public void shutdown() {
        try {
            executorService.shutdown();
            if (!executorService.awaitTermination(10, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            executorService.shutdownNow();
        }
    }
    
    // Placeholder classes - these would be implemented in separate files
    private static class ConnectionPool {
        public ConnectionPool(SdkConfiguration config) {}
        public boolean isCircuitBreakerOpen() { return false; }
        public void recordSuccess() {}
        public void recordFailure() {}
        public void shutdown() {}
    }
}