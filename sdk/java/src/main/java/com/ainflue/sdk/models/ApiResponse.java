package com.ainflue.sdk.models;

/**
 * API Response Model for Ainflue Java SDK
 * Type-safe response handling with comprehensive metadata
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Backend Senior + DBA + Lead Dev IA
 */

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Generic API Response wrapper
 * Implementation: Backend Senior + DBA
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    
    @JsonProperty("data")
    private T data;
    
    @JsonProperty("status_code")
    private int statusCode;
    
    @JsonProperty("headers")
    private Map<String, List<String>> headers;
    
    @JsonProperty("success")
    private boolean success;
    
    @JsonProperty("timestamp")
    private Instant timestamp;
    
    @JsonProperty("request_id")
    private String requestId;
    
    @JsonProperty("pagination")
    private PaginationInfo pagination;
    
    @JsonProperty("error")
    private ErrorInfo error;
    
    // Default constructor for Jackson
    public ApiResponse() {
        this.timestamp = Instant.now();
    }
    
    // Builder pattern for fluent API construction
    public static <T> Builder<T> builder() {
        return new Builder<>();
    }
    
    public static class Builder<T> {
        private T data;
        private int statusCode;
        private Map<String, List<String>> headers;
        private boolean success = true;
        private PaginationInfo pagination;
        private ErrorInfo error;
        private String requestId;
        
        public Builder<T> data(T data) {
            this.data = data;
            return this;
        }
        
        public Builder<T> statusCode(int statusCode) {
            this.statusCode = statusCode;
            return this;
        }
        
        public Builder<T> headers(Map<String, List<String>> headers) {
            this.headers = headers;
            return this;
        }
        
        public Builder<T> success(boolean success) {
            this.success = success;
            return this;
        }
        
        public Builder<T> pagination(PaginationInfo pagination) {
            this.pagination = pagination;
            return this;
        }
        
        public Builder<T> error(ErrorInfo error) {
            this.error = error;
            this.success = false;
            return this;
        }
        
        public Builder<T> requestId(String requestId) {
            this.requestId = requestId;
            return this;
        }
        
        public ApiResponse<T> build() {
            ApiResponse<T> response = new ApiResponse<>();
            response.data = this.data;
            response.statusCode = this.statusCode;
            response.headers = this.headers;
            response.success = this.success;
            response.pagination = this.pagination;
            response.error = this.error;
            response.requestId = this.requestId;
            return response;
        }
    }
    
    // Getters and setters
    public T getData() {
        return data;
    }
    
    public void setData(T data) {
        this.data = data;
    }
    
    public int getStatusCode() {
        return statusCode;
    }
    
    public void setStatusCode(int statusCode) {
        this.statusCode = statusCode;
    }
    
    public Map<String, List<String>> getHeaders() {
        return headers;
    }
    
    public void setHeaders(Map<String, List<String>> headers) {
        this.headers = headers;
    }
    
    public boolean isSuccess() {
        return success;
    }
    
    public void setSuccess(boolean success) {
        this.success = success;
    }
    
    public Instant getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(Instant timestamp) {
        this.timestamp = timestamp;
    }
    
    public String getRequestId() {
        return requestId;
    }
    
    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }
    
    public PaginationInfo getPagination() {
        return pagination;
    }
    
    public void setPagination(PaginationInfo pagination) {
        this.pagination = pagination;
    }
    
    public ErrorInfo getError() {
        return error;
    }
    
    public void setError(ErrorInfo error) {
        this.error = error;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ApiResponse<?> that = (ApiResponse<?>) o;
        return statusCode == that.statusCode &&
               success == that.success &&
               Objects.equals(data, that.data) &&
               Objects.equals(requestId, that.requestId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(data, statusCode, success, requestId);
    }
    
    @Override
    public String toString() {
        return "ApiResponse{" +
               "statusCode=" + statusCode +
               ", success=" + success +
               ", requestId='" + requestId + '\'' +
               ", timestamp=" + timestamp +
               '}';
    }
}

/**
 * Pagination information for paginated responses
 * Implementation: DBA + Backend Senior
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class PaginationInfo {
    
    @JsonProperty("page")
    private int page;
    
    @JsonProperty("limit")
    private int limit;
    
    @JsonProperty("total")
    private long total;
    
    @JsonProperty("total_pages")
    private int totalPages;
    
    @JsonProperty("has_next")
    private boolean hasNext;
    
    @JsonProperty("has_previous")
    private boolean hasPrevious;
    
    @JsonProperty("next_page")
    private String nextPage;
    
    @JsonProperty("previous_page")
    private String previousPage;
    
    // Constructors
    public PaginationInfo() {}
    
    public PaginationInfo(int page, int limit, long total) {
        this.page = page;
        this.limit = limit;
        this.total = total;
        this.totalPages = (int) Math.ceil((double) total / limit);
        this.hasNext = page < totalPages;
        this.hasPrevious = page > 1;
    }
    
    // Getters and setters
    public int getPage() { return page; }
    public void setPage(int page) { this.page = page; }
    
    public int getLimit() { return limit; }
    public void setLimit(int limit) { this.limit = limit; }
    
    public long getTotal() { return total; }
    public void setTotal(long total) { this.total = total; }
    
    public int getTotalPages() { return totalPages; }
    public void setTotalPages(int totalPages) { this.totalPages = totalPages; }
    
    public boolean isHasNext() { return hasNext; }
    public void setHasNext(boolean hasNext) { this.hasNext = hasNext; }
    
    public boolean isHasPrevious() { return hasPrevious; }
    public void setHasPrevious(boolean hasPrevious) { this.hasPrevious = hasPrevious; }
    
    public String getNextPage() { return nextPage; }
    public void setNextPage(String nextPage) { this.nextPage = nextPage; }
    
    public String getPreviousPage() { return previousPage; }
    public void setPreviousPage(String previousPage) { this.previousPage = previousPage; }
}

/**
 * Error information for failed responses
 * Implementation: Security + Backend Senior
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class ErrorInfo {
    
    @JsonProperty("code")
    private String code;
    
    @JsonProperty("message")
    private String message;
    
    @JsonProperty("details")
    private Map<String, Object> details;
    
    @JsonProperty("trace_id")
    private String traceId;
    
    @JsonProperty("timestamp")
    private Instant timestamp;
    
    public ErrorInfo() {
        this.timestamp = Instant.now();
    }
    
    public ErrorInfo(String code, String message) {
        this();
        this.code = code;
        this.message = message;
    }
    
    // Getters and setters
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    public Map<String, Object> getDetails() { return details; }
    public void setDetails(Map<String, Object> details) { this.details = details; }
    
    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }
    
    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }
}