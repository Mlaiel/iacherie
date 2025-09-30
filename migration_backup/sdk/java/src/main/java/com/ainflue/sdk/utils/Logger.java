package com.ainflue.sdk.utils;

/**
 * Logger Utility for Ainflue Java SDK
 * Enterprise logging with structured output and security filtering
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: DevOps + Security + Backend Senior
 */

import java.time.Instant;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.SimpleFormatter;
import java.util.regex.Pattern;

/**
 * SDK Logger with security filtering and structured output
 */
public class Logger {
    
    private static final Pattern SENSITIVE_PATTERN = Pattern.compile(
        "(?i)(password|token|key|secret|authorization|bearer|apikey)=[^\\s,}]+",
        Pattern.CASE_INSENSITIVE
    );
    
    private final java.util.logging.Logger javaLogger;
    private final String className;
    
    private Logger(String className) {
        this.className = className;
        this.javaLogger = java.util.logging.Logger.getLogger(className);
        configureLogger();
    }
    
    public static Logger getLogger(Class<?> clazz) {
        return new Logger(clazz.getName());
    }
    
    public static Logger getLogger(String name) {
        return new Logger(name);
    }
    
    private void configureLogger() {
        // Configure formatter for structured logging
        javaLogger.getHandlers()[0].setFormatter(new SecurityAwareFormatter());
    }
    
    // Info level logging
    public void info(String message) {
        log(Level.INFO, message);
    }
    
    public void info(String format, Object... args) {
        log(Level.INFO, String.format(format, args));
    }
    
    // Warning level logging
    public void warn(String message) {
        log(Level.WARNING, message);
    }
    
    public void warn(String format, Object... args) {
        log(Level.WARNING, String.format(format, args));
    }
    
    public void warn(String message, Throwable throwable) {
        log(Level.WARNING, message, throwable);
    }
    
    // Error level logging
    public void error(String message) {
        log(Level.SEVERE, message);
    }
    
    public void error(String format, Object... args) {
        log(Level.SEVERE, String.format(format, args));
    }
    
    public void error(String message, Throwable throwable) {
        log(Level.SEVERE, message, throwable);
    }
    
    // Debug level logging
    public void debug(String message) {
        log(Level.FINE, message);
    }
    
    public void debug(String format, Object... args) {
        log(Level.FINE, String.format(format, args));
    }
    
    // Trace level logging
    public void trace(String message) {
        log(Level.FINER, message);
    }
    
    public void trace(String format, Object... args) {
        log(Level.FINER, String.format(format, args));
    }
    
    private void log(Level level, String message) {
        if (javaLogger.isLoggable(level)) {
            String sanitizedMessage = sanitizeMessage(message);
            javaLogger.log(level, sanitizedMessage);
        }
    }
    
    private void log(Level level, String message, Throwable throwable) {
        if (javaLogger.isLoggable(level)) {
            String sanitizedMessage = sanitizeMessage(message);
            javaLogger.log(level, sanitizedMessage, throwable);
        }
    }
    
    /**
     * Sanitize log message to remove sensitive information
     * Implementation: Security + DevOps
     */
    private String sanitizeMessage(String message) {
        if (message == null) {
            return null;
        }
        
        // Replace sensitive information with [REDACTED]
        return SENSITIVE_PATTERN.matcher(message).replaceAll("$1=[REDACTED]");
    }
    
    /**
     * Check if logging level is enabled
     */
    public boolean isDebugEnabled() {
        return javaLogger.isLoggable(Level.FINE);
    }
    
    public boolean isTraceEnabled() {
        return javaLogger.isLoggable(Level.FINER);
    }
    
    public boolean isInfoEnabled() {
        return javaLogger.isLoggable(Level.INFO);
    }
    
    /**
     * Security-aware formatter for structured logging
     * Implementation: Security + DevOps
     */
    private static class SecurityAwareFormatter extends SimpleFormatter {
        
        private static final String LOG_FORMAT = 
            "%s [%s] %s.%s - %s%n";
        
        @Override
        public String format(LogRecord record) {
            return String.format(LOG_FORMAT,
                Instant.ofEpochMilli(record.getMillis()),
                record.getLevel(),
                record.getLoggerName(),
                getMethodName(record),
                formatMessage(record)
            );
        }
        
        private String getMethodName(LogRecord record) {
            if (record.getSourceMethodName() != null) {
                return record.getSourceMethodName();
            }
            return "unknown";
        }
        
        private String formatMessage(LogRecord record) {
            String message = super.formatMessage(record);
            
            // Additional security filtering at formatter level
            if (message.contains("Exception")) {
                // Sanitize exception messages that might contain sensitive data
                message = message.replaceAll("(password|token|key|secret)=[^\\s,}]+", "$1=[REDACTED]");
            }
            
            return message;
        }
    }
}