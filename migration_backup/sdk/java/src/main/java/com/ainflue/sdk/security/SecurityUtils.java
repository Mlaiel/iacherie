package com.ainflue.sdk.security;

/**
 * Security Utilities for Ainflue Java SDK
 * Enterprise security validation and SSL/TLS configuration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Security + DevOps + Backend Senior
 */

import com.ainflue.sdk.config.SdkConfiguration;
import com.ainflue.sdk.exceptions.SecurityException;
import com.ainflue.sdk.utils.Logger;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;
import java.net.URL;
import java.security.KeyStore;
import java.security.cert.X509Certificate;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * Security utilities for SDK operations
 */
public class SecurityUtils {
    
    private static final Logger logger = Logger.getLogger(SecurityUtils.class);
    
    // Security patterns and limits
    private static final Pattern VALID_URL_PATTERN = Pattern.compile(
        "^https://[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(:[0-9]+)?(/.*)?$"
    );
    
    private static final Pattern LOCALHOST_PATTERN = Pattern.compile(
        "^https?://localhost(:[0-9]+)?(/.*)?$|^https?://127\\.0\\.0\\.1(:[0-9]+)?(/.*)?$"
    );
    
    private static final int MAX_REQUEST_SIZE = 50 * 1024 * 1024; // 50MB
    private static final int MAX_HEADER_SIZE = 8192; // 8KB
    
    // Required security headers
    private static final String[] REQUIRED_SECURITY_HEADERS = {
        "strict-transport-security",
        "x-content-type-options",
        "x-frame-options"
    };
    
    private final SdkConfiguration config;
    
    public SecurityUtils(SdkConfiguration config) {
        this.config = config;
    }
    
    /**
     * Validate URL for security compliance
     * Implementation: Security + Backend Senior
     */
    public void validateUrl(String url) {
        if (url == null || url.trim().isEmpty()) {
            throw new SecurityException("URL cannot be null or empty");
        }
        
        try {
            URL parsedUrl = new URL(url);
            
            // Protocol validation
            String protocol = parsedUrl.getProtocol().toLowerCase();
            if (!protocol.equals("https")) {
                // Allow HTTP only for localhost in development
                if (!isLocalhostUrl(url) || config.isProductionMode()) {
                    throw new SecurityException("Only HTTPS URLs are allowed in production");
                }
            }
            
            // Host validation
            String host = parsedUrl.getHost();
            if (host == null || host.trim().isEmpty()) {
                throw new SecurityException("Invalid host in URL");
            }
            
            // Check for suspicious patterns
            if (containsSuspiciousPatterns(url)) {
                throw new SecurityException("URL contains suspicious patterns");
            }
            
            // Validate against allowlist if configured
            if (config.hasUrlAllowlist() && !config.isUrlAllowed(url)) {
                throw new SecurityException("URL not in allowlist: " + host);
            }
            
            logger.debug("URL validation passed: {}", sanitizeUrlForLogging(url));
            
        } catch (Exception e) {
            if (e instanceof SecurityException) {
                throw e;
            }
            throw new SecurityException("Invalid URL format: " + e.getMessage());
        }
    }
    
    /**
     * Validate request size for DoS protection
     * Implementation: Security + DevOps
     */
    public void validateRequestSize(int requestSizeBytes) {
        if (requestSizeBytes > MAX_REQUEST_SIZE) {
            throw new SecurityException(
                String.format("Request size (%d bytes) exceeds maximum allowed size (%d bytes)",
                            requestSizeBytes, MAX_REQUEST_SIZE)
            );
        }
        
        if (requestSizeBytes > config.getMaxRequestSize()) {
            throw new SecurityException(
                String.format("Request size (%d bytes) exceeds configured limit (%d bytes)",
                            requestSizeBytes, config.getMaxRequestSize())
            );
        }
        
        logger.trace("Request size validation passed: {} bytes", requestSizeBytes);
    }
    
    /**
     * Validate request headers for security
     * Implementation: Security
     */
    public void validateRequestHeaders(Map<String, String> headers) {
        if (headers == null) return;
        
        for (Map.Entry<String, String> header : headers.entrySet()) {
            String name = header.getKey();
            String value = header.getValue();
            
            // Header size validation
            if (value != null && value.length() > MAX_HEADER_SIZE) {
                throw new SecurityException(
                    String.format("Header '%s' exceeds maximum size (%d bytes)", name, MAX_HEADER_SIZE)
                );
            }
            
            // Header injection protection
            if (containsHeaderInjection(name) || containsHeaderInjection(value)) {
                throw new SecurityException("Header injection attempt detected");
            }
            
            // Validate sensitive headers
            if (isSensitiveHeader(name)) {
                validateSensitiveHeader(name, value);
            }
        }
        
        logger.trace("Request headers validation passed");
    }
    
    /**
     * Validate response headers for security compliance
     * Implementation: Security + DevOps
     */
    public void validateResponseHeaders(Map<String, List<String>> headers) {
        if (headers == null) return;
        
        // Check for required security headers
        for (String requiredHeader : REQUIRED_SECURITY_HEADERS) {
            if (!headers.containsKey(requiredHeader)) {
                logger.warn("Missing security header: {}", requiredHeader);
            }
        }
        
        // Validate specific security headers
        validateSecurityHeader(headers, "strict-transport-security", this::validateHSTS);
        validateSecurityHeader(headers, "x-content-type-options", value -> {
            if (!"nosniff".equals(value)) {
                logger.warn("Invalid X-Content-Type-Options value: {}", value);
            }
        });
        validateSecurityHeader(headers, "x-frame-options", value -> {
            if (!"DENY".equals(value) && !"SAMEORIGIN".equals(value) && !value.startsWith("ALLOW-FROM")) {
                logger.warn("Invalid X-Frame-Options value: {}", value);
            }
        });
        
        logger.trace("Response headers validation completed");
    }
    
    /**
     * Create secure SSL context
     * Implementation: Security + DevOps
     */
    public SSLContext createSSLContext() {
        try {
            if (config.hasCustomTrustStore()) {
                return createCustomSSLContext();
            } else {
                return createDefaultSSLContext();
            }
        } catch (Exception e) {
            logger.error("Failed to create SSL context", e);
            throw new SecurityException("SSL context creation failed: " + e.getMessage());
        }
    }
    
    /**
     * Sanitize API key for logging
     * Implementation: Security
     */
    public String sanitizeApiKey(String apiKey) {
        if (apiKey == null || apiKey.length() < 8) {
            return "[REDACTED]";
        }
        
        return apiKey.substring(0, 4) + "..." + apiKey.substring(apiKey.length() - 4);
    }
    
    /**
     * Generate secure request ID
     * Implementation: Security + DevOps
     */
    public String generateSecureRequestId() {
        // Use cryptographically secure random for request IDs
        java.security.SecureRandom secureRandom = new java.security.SecureRandom();
        byte[] randomBytes = new byte[16];
        secureRandom.nextBytes(randomBytes);
        
        StringBuilder sb = new StringBuilder("req_");
        sb.append(System.currentTimeMillis()).append("_");
        for (byte b : randomBytes) {
            sb.append(String.format("%02x", b));
        }
        
        return sb.toString();
    }
    
    // Private helper methods
    
    private boolean isLocalhostUrl(String url) {
        return LOCALHOST_PATTERN.matcher(url).matches();
    }
    
    private boolean containsSuspiciousPatterns(String url) {
        String lowerUrl = url.toLowerCase();
        
        // Check for common malicious patterns
        String[] suspiciousPatterns = {
            "javascript:", "data:", "file:", "ftp:",
            "../", "..\\", "%2e%2e", "%2f", "%5c",
            "127.0.0.1", "localhost", "0.0.0.0",
            "169.254.", "10.", "172.16.", "192.168."
        };
        
        for (String pattern : suspiciousPatterns) {
            if (lowerUrl.contains(pattern)) {
                return true;
            }
        }
        
        return false;
    }
    
    private boolean containsHeaderInjection(String value) {
        if (value == null) return false;
        
        return value.contains("\r") || value.contains("\n") || 
               value.contains("\0") || value.contains("\u0000");
    }
    
    private boolean isSensitiveHeader(String headerName) {
        String lowerName = headerName.toLowerCase();
        return lowerName.equals("authorization") ||
               lowerName.equals("cookie") ||
               lowerName.equals("x-api-key") ||
               lowerName.equals("x-auth-token");
    }
    
    private void validateSensitiveHeader(String name, String value) {
        if (value == null || value.trim().isEmpty()) {
            throw new SecurityException("Sensitive header '" + name + "' cannot be empty");
        }
        
        // Additional validation for specific headers
        if ("authorization".equals(name.toLowerCase())) {
            if (!value.matches("^(Bearer|Basic|Digest)\\s+.+$")) {
                logger.warn("Authorization header format may be invalid");
            }
        }
    }
    
    private void validateSecurityHeader(Map<String, List<String>> headers, String headerName, 
                                      java.util.function.Consumer<String> validator) {
        List<String> values = headers.get(headerName);
        if (values != null && !values.isEmpty()) {
            validator.accept(values.get(0));
        }
    }
    
    private void validateHSTS(String value) {
        if (value == null || !value.contains("max-age=")) {
            logger.warn("Invalid HSTS header: {}", value);
            return;
        }
        
        try {
            String maxAgeStr = value.replaceAll(".*max-age=(\\d+).*", "$1");
            long maxAge = Long.parseLong(maxAgeStr);
            
            if (maxAge < 31536000) { // Less than 1 year
                logger.warn("HSTS max-age is less than recommended 1 year: {} seconds", maxAge);
            }
        } catch (NumberFormatException e) {
            logger.warn("Unable to parse HSTS max-age: {}", value);
        }
    }
    
    private SSLContext createDefaultSSLContext() throws Exception {
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, null, null);
        return sslContext;
    }
    
    private SSLContext createCustomSSLContext() throws Exception {
        KeyStore trustStore = config.getTrustStore();
        TrustManagerFactory tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        tmf.init(trustStore);
        
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, tmf.getTrustManagers(), null);
        
        return sslContext;
    }
    
    private String sanitizeUrlForLogging(String url) {
        if (url == null) return null;
        
        // Remove sensitive query parameters
        String sanitized = url.replaceAll("([?&])(password|token|key|secret|apikey)=[^&]*", "$1$2=[REDACTED]");
        
        return sanitized;
    }
}