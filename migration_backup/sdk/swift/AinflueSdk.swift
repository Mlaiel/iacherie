import Foundation
import Network
import CryptoKit

/**
 * Ainflue SDK for iOS/Swift
 * Native iOS implementation with Combine and async/await support
 *
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 *
 * Expert Implementation by: Mobile + Security + Audio Engineer + Lead Dev IA
 */

@available(iOS 13.0, *)
public class AinflueSdk: ObservableObject {
    
    // MARK: - Properties
    private let configuration: SdkConfiguration
    private let urlSession: URLSession
    private let logger: SDKLogger
    private let securityValidator: SecurityValidator
    private let metricsCollector: MetricsCollector
    private let networkMonitor: NWPathMonitor
    private let operationQueue: OperationQueue
    
    // MARK: - Published Properties for SwiftUI
    @Published public var isOnline: Bool = true
    @Published public var metrics: SDKMetrics = SDKMetrics()
    
    // MARK: - Constants
    private static let userAgent = "Ainflue-iOS-SDK/1.0.0"
    private static let defaultTimeout: TimeInterval = 30.0
    
    // MARK: - Initialization
    
    /// Initialize the Ainflue SDK with configuration
    /// Implementation: Mobile + Security + DevOps
    public init(configuration: SdkConfiguration) throws {
        self.configuration = configuration
        self.logger = SDKLogger(category: "AinflueSdk")
        self.securityValidator = SecurityValidator(configuration: configuration)
        self.metricsCollector = MetricsCollector()
        self.networkMonitor = NWPathMonitor()
        self.operationQueue = OperationQueue()
        
        // Validate configuration
        try self.validateConfiguration()
        
        // Create URL session with custom configuration
        self.urlSession = self.createURLSession()
        
        // Setup network monitoring
        self.setupNetworkMonitoring()
        
        logger.info("Ainflue iOS SDK initialized with base URL: \(configuration.baseURL)")
    }
    
    // MARK: - HTTP Methods
    
    /// Execute GET request with async/await
    /// Implementation: Mobile + Backend Senior + Lead Dev IA
    public func get<T: Codable>(
        endpoint: String,
        headers: [String: String]? = nil,
        type: T.Type
    ) async throws -> ApiResponse<T> {
        return try await executeRequest(
            method: .GET,
            endpoint: endpoint,
            body: nil,
            headers: headers,
            responseType: type
        )
    }
    
    /// Execute POST request with data
    /// Implementation: Mobile + Security
    public func post<T: Codable, U: Codable>(
        endpoint: String,
        body: U? = nil,
        headers: [String: String]? = nil,
        responseType: T.Type
    ) async throws -> ApiResponse<T> {
        return try await executeRequest(
            method: .POST,
            endpoint: endpoint,
            body: body,
            headers: headers,
            responseType: responseType
        )
    }
    
    /// Execute PUT request
    public func put<T: Codable, U: Codable>(
        endpoint: String,
        body: U? = nil,
        headers: [String: String]? = nil,
        responseType: T.Type
    ) async throws -> ApiResponse<T> {
        return try await executeRequest(
            method: .PUT,
            endpoint: endpoint,
            body: body,
            headers: headers,
            responseType: responseType
        )
    }
    
    /// Execute DELETE request
    public func delete<T: Codable>(
        endpoint: String,
        headers: [String: String]? = nil,
        responseType: T.Type
    ) async throws -> ApiResponse<T> {
        return try await executeRequest(
            method: .DELETE,
            endpoint: endpoint,
            body: nil as String?,
            headers: headers,
            responseType: responseType
        )
    }
    
    // MARK: - Core Request Execution
    
    /// Core request execution method with comprehensive error handling
    /// Implementation: Lead Dev IA + Mobile + Security + DevOps
    private func executeRequest<T: Codable, U: Codable>(
        method: HTTPMethod,
        endpoint: String,
        body: U?,
        headers: [String: String]?,
        responseType: T.Type
    ) async throws -> ApiResponse<T> {
        
        let requestId = generateRequestId()
        let startTime = Date()
        
        do {
            // Security validation
            try securityValidator.validateEndpoint(endpoint)
            
            // Build request
            let request = try buildRequest(
                method: method,
                endpoint: endpoint,
                body: body,
                headers: headers,
                requestId: requestId
            )
            
            // Execute request with retry logic
            let (data, response) = try await executeWithRetry(request: request)
            
            let duration = Date().timeIntervalSince(startTime)
            
            // Record metrics
            let httpResponse = response as! HTTPURLResponse
            await metricsCollector.recordRequest(
                method: method.rawValue,
                endpoint: endpoint,
                statusCode: httpResponse.statusCode,
                duration: duration
            )
            
            // Parse response
            return try parseResponse(
                data: data,
                response: httpResponse,
                requestId: requestId,
                responseType: responseType
            )
            
        } catch {
            let duration = Date().timeIntervalSince(startTime)
            await metricsCollector.recordFailure(
                method: method.rawValue,
                endpoint: endpoint,
                error: error.localizedDescription
            )
            
            logger.error("Request failed: \(method.rawValue) \(endpoint) [\(requestId)] - \(error)")
            throw SDKError.requestFailed(requestId: requestId, underlyingError: error)
        }
    }
    
    // MARK: - Request Building
    
    /// Build HTTP request with security and validation
    /// Implementation: Security + Mobile
    private func buildRequest<U: Codable>(
        method: HTTPMethod,
        endpoint: String,
        body: U?,
        headers: [String: String]?,
        requestId: String
    ) throws -> URLRequest {
        
        // Build URL
        guard let url = URL(string: configuration.baseURL + "/" + endpoint.trimmingCharacters(in: CharacterSet(charactersIn: "/"))) else {
            throw SDKError.invalidURL(endpoint)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.timeoutInterval = configuration.timeout
        
        // Set default headers
        request.setValue(Self.userAgent, forHTTPHeaderField: "User-Agent")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(requestId, forHTTPHeaderField: "X-Request-ID")
        request.setValue(ISO8601DateFormatter().string(from: Date()), forHTTPHeaderField: "X-Timestamp")
        
        // Add authentication header
        if let apiKey = configuration.apiKey {
            request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        }
        
        // Add custom headers
        headers?.forEach { key, value in
            // Security: Validate headers
            do {
                try securityValidator.validateHeader(key: key, value: value)
                request.setValue(value, forHTTPHeaderField: key)
            } catch {
                logger.warning("Invalid header \(key): \(error)")
            }
        }
        
        // Add request body
        if let body = body, method != .GET && method != .DELETE {
            do {
                let jsonData = try JSONEncoder().encode(body)
                
                // Security: Validate request size
                try securityValidator.validateRequestSize(size: jsonData.count)
                
                request.httpBody = jsonData
            } catch {
                throw SDKError.encodingFailed(error)
            }
        }
        
        return request
    }
    
    // MARK: - Response Parsing
    
    /// Parse HTTP response with comprehensive error handling
    /// Implementation: Mobile + Security
    private func parseResponse<T: Codable>(
        data: Data,
        response: HTTPURLResponse,
        requestId: String,
        responseType: T.Type
    ) throws -> ApiResponse<T> {
        
        // Security: Validate response headers
        securityValidator.validateResponseHeaders(response.allHeaderFields as? [String: String] ?? [:])
        
        let apiResponse = ApiResponse<T>(
            statusCode: response.statusCode,
            headers: response.allHeaderFields as? [String: String] ?? [:],
            requestId: requestId,
            success: 200..<300 ~= response.statusCode
        )
        
        if apiResponse.success {
            // Parse successful response
            if !data.isEmpty && responseType != EmptyResponse.self {
                do {
                    apiResponse.data = try JSONDecoder().decode(responseType, from: data)
                } catch {
                    logger.warning("Failed to decode response: \(error)")
                    throw SDKError.decodingFailed(error)
                }
            }
        } else {
            // Handle error response
            let errorMessage = extractErrorMessage(from: data, statusCode: response.statusCode)
            
            switch response.statusCode {
            case 401:
                throw SDKError.authenticationFailed(errorMessage)
            case 403:
                throw SDKError.authorizationFailed(errorMessage)
            case 404:
                throw SDKError.notFound(errorMessage)
            case 429:
                let retryAfter = response.value(forHTTPHeaderField: "Retry-After").flatMap(Int.init) ?? 60
                throw SDKError.rateLimited(message: errorMessage, retryAfter: retryAfter)
            case 500...599:
                throw SDKError.serverError(message: errorMessage, statusCode: response.statusCode)
            default:
                throw SDKError.clientError(message: errorMessage, statusCode: response.statusCode)
            }
        }
        
        return apiResponse
    }
    
    // MARK: - Audio Processing
    
    /// Process audio data for AI analysis
    /// Implementation: Audio Engineer + ML Engineer + Lead Dev IA
    public func processAudio(audioData: Data, processingOptions: AudioProcessingOptions) async throws -> ApiResponse<AudioProcessingResult> {
        
        // Validate audio data
        try securityValidator.validateAudioData(audioData)
        
        // Create multipart form data
        let boundary = "Boundary-\(UUID().uuidString)"
        var formData = Data()
        
        // Add audio file
        formData.append("--\(boundary)\r\n".data(using: .utf8)!)
        formData.append("Content-Disposition: form-data; name=\"audio\"; filename=\"audio.m4a\"\r\n".data(using: .utf8)!)
        formData.append("Content-Type: audio/mp4\r\n\r\n".data(using: .utf8)!)
        formData.append(audioData)
        formData.append("\r\n".data(using: .utf8)!)
        
        // Add processing options
        let optionsData = try JSONEncoder().encode(processingOptions)
        formData.append("--\(boundary)\r\n".data(using: .utf8)!)
        formData.append("Content-Disposition: form-data; name=\"options\"\r\n".data(using: .utf8)!)
        formData.append("Content-Type: application/json\r\n\r\n".data(using: .utf8)!)
        formData.append(optionsData)
        formData.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        // Build request
        guard let url = URL(string: configuration.baseURL + "/api/v1/audio/process") else {
            throw SDKError.invalidURL("/api/v1/audio/process")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.httpBody = formData
        
        // Execute request
        let (data, response) = try await urlSession.data(for: request)
        let httpResponse = response as! HTTPURLResponse
        
        return try parseResponse(
            data: data,
            response: httpResponse,
            requestId: generateRequestId(),
            responseType: AudioProcessingResult.self
        )
    }
    
    // MARK: - Helper Methods
    
    /// Create URL session with custom configuration
    /// Implementation: Mobile + Security + DevOps
    private func createURLSession() -> URLSession {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = configuration.timeout
        config.timeoutIntervalForResource = configuration.timeout * 2
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.httpMaximumConnectionsPerHost = 4
        
        // Security: Configure TLS
        config.tlsMinimumSupportedProtocolVersion = .TLSv12
        
        return URLSession(configuration: config)
    }
    
    /// Setup network monitoring for offline/online detection
    /// Implementation: DevOps + Mobile
    private func setupNetworkMonitoring() {
        networkMonitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isOnline = path.status == .satisfied
            }
        }
        
        let queue = DispatchQueue(label: "NetworkMonitor")
        networkMonitor.start(queue: queue)
    }
    
    /// Execute request with intelligent retry logic
    /// Implementation: Lead Dev IA + DevOps
    private func executeWithRetry(request: URLRequest) async throws -> (Data, URLResponse) {
        var lastError: Error?
        
        for attempt in 0...configuration.maxRetries {
            do {
                let result = try await urlSession.data(for: request)
                return result
            } catch {
                lastError = error
                
                if attempt < configuration.maxRetries && shouldRetry(error: error) {
                    let delay = calculateBackoffDelay(attempt: attempt)
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                }
            }
        }
        
        throw lastError ?? SDKError.unknownError
    }
    
    /// Determine if error should trigger retry
    private func shouldRetry(error: Error) -> Bool {
        if let urlError = error as? URLError {
            switch urlError.code {
            case .timedOut, .networkConnectionLost, .notConnectedToInternet:
                return true
            default:
                return false
            }
        }
        return false
    }
    
    /// Calculate exponential backoff delay
    private func calculateBackoffDelay(attempt: Int) -> Double {
        let baseDelay = min(pow(2.0, Double(attempt)), 30.0) // Max 30 seconds
        let jitter = Double.random(in: 0...0.1) * baseDelay
        return baseDelay + jitter
    }
    
    /// Extract error message from response data
    private func extractErrorMessage(from data: Data, statusCode: Int) -> String {
        guard !data.isEmpty else {
            return "HTTP \(statusCode)"
        }
        
        do {
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                let messageFields = ["message", "error", "detail", "errorMessage"]
                for field in messageFields {
                    if let message = json[field] as? String {
                        return message
                    }
                }
            }
        } catch {
            // Fall back to raw string
        }
        
        return String(data: data, encoding: .utf8) ?? "Unknown error"
    }
    
    /// Generate unique request ID
    private func generateRequestId() -> String {
        return "req_\(Int(Date().timeIntervalSince1970 * 1000))_\(UUID().uuidString.prefix(8))"
    }
    
    /// Validate SDK configuration
    private func validateConfiguration() throws {
        guard !configuration.baseURL.isEmpty else {
            throw SDKError.invalidConfiguration("Base URL is required")
        }
        
        guard URL(string: configuration.baseURL) != nil else {
            throw SDKError.invalidConfiguration("Invalid base URL format")
        }
        
        guard configuration.timeout > 0 else {
            throw SDKError.invalidConfiguration("Timeout must be positive")
        }
    }
    
    deinit {
        networkMonitor.cancel()
    }
}

// MARK: - Supporting Types

/// HTTP methods enumeration
public enum HTTPMethod: String, CaseIterable {
    case GET = "GET"
    case POST = "POST"
    case PUT = "PUT"
    case DELETE = "DELETE"
    case PATCH = "PATCH"
}

/// SDK Configuration
public struct SdkConfiguration {
    public let baseURL: String
    public let apiKey: String?
    public let timeout: TimeInterval
    public let maxRetries: Int
    public let enableMetrics: Bool
    public let enableSecurity: Bool
    
    public init(
        baseURL: String,
        apiKey: String? = nil,
        timeout: TimeInterval = 30.0,
        maxRetries: Int = 3,
        enableMetrics: Bool = true,
        enableSecurity: Bool = true
    ) {
        self.baseURL = baseURL
        self.apiKey = apiKey
        self.timeout = timeout
        self.maxRetries = maxRetries
        self.enableMetrics = enableMetrics
        self.enableSecurity = enableSecurity
    }
}

/// Generic API Response
public class ApiResponse<T: Codable>: ObservableObject {
    @Published public var data: T?
    public let statusCode: Int
    public let headers: [String: String]
    public let requestId: String
    public let success: Bool
    public let timestamp: Date
    
    public init(statusCode: Int, headers: [String: String], requestId: String, success: Bool) {
        self.statusCode = statusCode
        self.headers = headers
        self.requestId = requestId
        self.success = success
        self.timestamp = Date()
    }
}

/// Empty response type for requests that don't return data
public struct EmptyResponse: Codable {}

/// Audio processing options
public struct AudioProcessingOptions: Codable {
    public let processingType: String
    public let language: String?
    public let sampleRate: Int?
    public let channels: Int?
    
    public init(processingType: String, language: String? = nil, sampleRate: Int? = nil, channels: Int? = nil) {
        self.processingType = processingType
        self.language = language
        self.sampleRate = sampleRate
        self.channels = channels
    }
}

/// Audio processing result
public struct AudioProcessingResult: Codable {
    public let processingId: String
    public let status: String
    public let result: AudioAnalysisResult?
    public let progress: Double?
}

public struct AudioAnalysisResult: Codable {
    public let transcription: String?
    public let sentiment: String?
    public let keywords: [String]?
    public let duration: Double?
}

/// SDK Error types
public enum SDKError: LocalizedError {
    case invalidConfiguration(String)
    case invalidURL(String)
    case authenticationFailed(String)
    case authorizationFailed(String)
    case notFound(String)
    case rateLimited(message: String, retryAfter: Int)
    case serverError(message: String, statusCode: Int)
    case clientError(message: String, statusCode: Int)
    case requestFailed(requestId: String, underlyingError: Error)
    case encodingFailed(Error)
    case decodingFailed(Error)
    case unknownError
    
    public var errorDescription: String? {
        switch self {
        case .invalidConfiguration(let message):
            return "Invalid configuration: \(message)"
        case .invalidURL(let url):
            return "Invalid URL: \(url)"
        case .authenticationFailed(let message):
            return "Authentication failed: \(message)"
        case .authorizationFailed(let message):
            return "Authorization failed: \(message)"
        case .notFound(let message):
            return "Not found: \(message)"
        case .rateLimited(let message, let retryAfter):
            return "Rate limited: \(message) (retry after \(retryAfter)s)"
        case .serverError(let message, let statusCode):
            return "Server error (\(statusCode)): \(message)"
        case .clientError(let message, let statusCode):
            return "Client error (\(statusCode)): \(message)"
        case .requestFailed(let requestId, let underlyingError):
            return "Request failed [\(requestId)]: \(underlyingError.localizedDescription)"
        case .encodingFailed(let error):
            return "Encoding failed: \(error.localizedDescription)"
        case .decodingFailed(let error):
            return "Decoding failed: \(error.localizedDescription)"
        case .unknownError:
            return "Unknown error occurred"
        }
    }
}

// MARK: - Supporting Classes (Simplified)

class SDKLogger {
    let category: String
    
    init(category: String) {
        self.category = category
    }
    
    func info(_ message: String) {
        print("[INFO] \(category): \(message)")
    }
    
    func warning(_ message: String) {
        print("[WARN] \(category): \(message)")
    }
    
    func error(_ message: String) {
        print("[ERROR] \(category): \(message)")
    }
}

class SecurityValidator {
    let configuration: SdkConfiguration
    
    init(configuration: SdkConfiguration) {
        self.configuration = configuration
    }
    
    func validateEndpoint(_ endpoint: String) throws {
        // Security validation logic
    }
    
    func validateHeader(key: String, value: String) throws {
        // Header validation logic
    }
    
    func validateRequestSize(size: Int) throws {
        if size > 50 * 1024 * 1024 { // 50MB
            throw SDKError.clientError(message: "Request too large", statusCode: 413)
        }
    }
    
    func validateResponseHeaders(_ headers: [String: String]) {
        // Response header validation
    }
    
    func validateAudioData(_ data: Data) throws {
        if data.isEmpty {
            throw SDKError.invalidConfiguration("Audio data cannot be empty")
        }
        
        if data.count > 100 * 1024 * 1024 { // 100MB
            throw SDKError.clientError(message: "Audio file too large", statusCode: 413)
        }
    }
}

@MainActor
class MetricsCollector: ObservableObject {
    @Published var metrics = SDKMetrics()
    
    func recordRequest(method: String, endpoint: String, statusCode: Int, duration: TimeInterval) {
        // Record metrics
    }
    
    func recordFailure(method: String, endpoint: String, error: String) {
        // Record failure metrics
    }
}

public struct SDKMetrics: Codable {
    public var totalRequests: Int = 0
    public var successfulRequests: Int = 0
    public var failedRequests: Int = 0
    public var averageLatency: TimeInterval = 0
}