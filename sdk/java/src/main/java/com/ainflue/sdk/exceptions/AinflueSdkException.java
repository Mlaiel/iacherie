package com.ainflue.sdk.exceptions;

/**
 * Exception Classes for Ainflue Java SDK
 * Comprehensive error handling for enterprise applications
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Security + Backend Senior + DevOps
 */

import java.time.Instant;
import java.util.UUID;

/**
 * Base exception class for all SDK-related errors
 * Implementation: Security + Backend Senior
 */
public class AinflueSdkException extends RuntimeException {
    
    private final String errorId;
    private final Instant timestamp;
    private final String errorCode;
    
    public AinflueSdkException(String message) {
        this(message, null, null);
    }
    
    public AinflueSdkException(String message, Throwable cause) {
        this(message, cause, null);
    }
    
    public AinflueSdkException(String message, Throwable cause, String errorCode) {
        super(message, cause);
        this.errorId = generateErrorId();
        this.timestamp = Instant.now();
        this.errorCode = errorCode;
    }
    
    private String generateErrorId() {
        return "err_" + System.currentTimeMillis() + "_" + 
               UUID.randomUUID().toString().substring(0, 8);
    }
    
    public String getErrorId() {
        return errorId;
    }
    
    public Instant getTimestamp() {
        return timestamp;
    }
    
    public String getErrorCode() {
        return errorCode;
    }
    
    @Override
    public String toString() {
        return String.format("AinflueSdkException{errorId='%s', timestamp=%s, message='%s'}", 
                           errorId, timestamp, getMessage());
    }
}

/**
 * Authentication related exceptions
 * Implementation: Security
 */
class AuthenticationException extends AinflueSdkException {
    public AuthenticationException(String message) {
        super(message, null, "AUTH_001");
    }
    
    public AuthenticationException(String message, Throwable cause) {
        super(message, cause, "AUTH_001");
    }
}

/**
 * Authorization related exceptions
 * Implementation: Security
 */
class AuthorizationException extends AinflueSdkException {
    public AuthorizationException(String message) {
        super(message, null, "AUTH_002");
    }
    
    public AuthorizationException(String message, Throwable cause) {
        super(message, cause, "AUTH_002");
    }
}

/**
 * Configuration related exceptions
 * Implementation: DevOps + Backend Senior
 */
class ConfigurationException extends AinflueSdkException {
    public ConfigurationException(String message) {
        super(message, null, "CONFIG_001");
    }
    
    public ConfigurationException(String message, Throwable cause) {
        super(message, cause, "CONFIG_001");
    }
}

/**
 * Network and connectivity exceptions
 * Implementation: DevOps + Backend Senior
 */
class NetworkException extends AinflueSdkException {
    public NetworkException(String message) {
        super(message, null, "NETWORK_001");
    }
    
    public NetworkException(String message, Throwable cause) {
        super(message, cause, "NETWORK_001");
    }
}

/**
 * Rate limiting exceptions
 * Implementation: DevOps + Security
 */
class RateLimitException extends AinflueSdkException {
    private final int retryAfterSeconds;
    
    public RateLimitException(String message, int retryAfterSeconds) {
        super(message, null, "RATE_001");
        this.retryAfterSeconds = retryAfterSeconds;
    }
    
    public int getRetryAfterSeconds() {
        return retryAfterSeconds;
    }
}

/**
 * Server error exceptions (5xx HTTP status codes)
 * Implementation: Backend Senior + DevOps
 */
class ServerException extends AinflueSdkException {
    private final int statusCode;
    
    public ServerException(String message, int statusCode) {
        super(message, null, "SERVER_" + statusCode);
        this.statusCode = statusCode;
    }
    
    public int getStatusCode() {
        return statusCode;
    }
}

/**
 * Client error exceptions (4xx HTTP status codes)
 * Implementation: Backend Senior + Security
 */
class ClientException extends AinflueSdkException {
    private final int statusCode;
    
    public ClientException(String message, int statusCode) {
        super(message, null, "CLIENT_" + statusCode);
        this.statusCode = statusCode;
    }
    
    public int getStatusCode() {
        return statusCode;
    }
}

/**
 * Resource not found exceptions
 * Implementation: Backend Senior
 */
class NotFoundException extends ClientException {
    public NotFoundException(String message) {
        super(message, 404);
    }
}

/**
 * Service unavailable exceptions
 * Implementation: DevOps + Microservices
 */
class ServiceUnavailableException extends ServerException {
    public ServiceUnavailableException(String message) {
        super(message, 503);
    }
}