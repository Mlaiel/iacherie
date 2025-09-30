//
//  BiometricAuth.swift
//  Ainflue iOS - Professional Biometric Authentication
//
//  Advanced enterprise-grade biometric authentication system supporting
//  Face ID, Touch ID, and secure device authentication with privacy protection.
//
//  Author: Fahed Mlaiel (mlaiel@live.de)
//  Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
//
//  Team Specialties:
//  - Lead AI Developer + Backend Senior + ML Engineer
//  - Database Administrator + Security Expert
//  - Microservices Architect + Audio Processing Specialist
//  - DevOps Engineer + IA Prompt Engineer
//
//  ⚠️ STRICT COPYRIGHT NOTICE ⚠️
//  This code is proprietary and confidential to Fahed Mlaiel.
//  Any unauthorized use, copying, modification, or distribution
//  without explicit written permission is strictly prohibited.
//  Violations will result in legal action.
//  Contact: mlaiel@live.de for licensing inquiries.
//

import Foundation
import LocalAuthentication
import Security
import CryptoKit
import UIKit

@objc(BiometricAuthService)
class BiometricAuthService: NSObject {
    
    // MARK: - Singleton Instance
    static let shared = BiometricAuthService()
    
    // MARK: - Authentication Context
    private var context: LAContext!
    private var policy: LAPolicy = .deviceOwnerAuthenticationWithBiometrics
    
    // MARK: - Security Configuration
    private var authenticationTimeout: TimeInterval = 60.0 // 1 minute
    private var maxRetryAttempts: Int = 3
    private var currentRetryCount: Int = 0
    private var lastAuthenticationDate: Date?
    private var sessionToken: String?
    
    // MARK: - Biometric Capabilities
    private var biometricType: LABiometryType = .none
    private var isEnrolledForBiometrics: Bool = false
    private var fallbackToPasscode: Bool = true
    
    // MARK: - Security Delegates
    weak var delegate: BiometricAuthDelegate?
    
    // MARK: - Keychain Integration
    private let keychainService = "com.fahedmlaiel.ainflue"
    private let biometricTokenKey = "ainflue_biometric_token"
    private let authenticationConfigKey = "ainflue_auth_config"
    
    // MARK: - Security Queues
    private let authQueue = DispatchQueue(label: "com.ainflue.biometric.auth", qos: .userInitiated)
    private let securityQueue = DispatchQueue(label: "com.ainflue.biometric.security", qos: .userInitiated)
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        initializeBiometricService()
    }
    
    // MARK: - Service Initialization
    
    private func initializeBiometricService() {
        setupAuthenticationContext()
        evaluateBiometricCapabilities()
        loadSecurityConfiguration()
        setupSecurityMonitoring()
        
        print("✅ Biometric authentication service initialized")
    }
    
    private func setupAuthenticationContext() {
        context = LAContext()
        
        // Configure context for maximum security
        context.localizedFallbackTitle = "Use Passcode"
        context.localizedCancelTitle = "Cancel Authentication"
        
        // Set touch ID timeout
        if #available(iOS 9.0, *) {
            context.touchIDAuthenticationAllowableReuseDuration = authenticationTimeout
        }
    }
    
    private func evaluateBiometricCapabilities() {
        var error: NSError?
        
        // Check biometric availability
        let isBiometricAvailable = context.canEvaluatePolicy(policy, error: &error)
        
        if isBiometricAvailable {
            biometricType = context.biometryType
            isEnrolledForBiometrics = true
            
            print("✅ Biometric authentication available: \(biometricTypeString())")
        } else {
            if let error = error {
                print("❌ Biometric authentication not available: \(error.localizedDescription)")
                handleBiometricError(error)
            }
        }
    }
    
    private func loadSecurityConfiguration() {
        // Load saved authentication preferences
        if let configData = loadFromKeychain(key: authenticationConfigKey),
           let config = try? JSONDecoder().decode(AuthenticationConfig.self, from: configData) {
            
            authenticationTimeout = config.timeout
            maxRetryAttempts = config.maxRetries
            fallbackToPasscode = config.allowPasscodeFallback
            
            print("✅ Security configuration loaded")
        } else {
            saveDefaultSecurityConfiguration()
        }
    }
    
    private func setupSecurityMonitoring() {
        // Monitor for security changes
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleSecurityStateChange),
            name: .LABiometryUpdate,
            object: nil
        )
        
        // Monitor app lifecycle for security
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleAppDidEnterBackground),
            name: UIApplication.didEnterBackgroundNotification,
            object: nil
        )
        
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleAppWillEnterForeground),
            name: UIApplication.willEnterForegroundNotification,
            object: nil
        )
    }
    
    // MARK: - Public Authentication Methods
    
    func checkAvailability() -> Bool {
        var error: NSError?
        let isAvailable = context.canEvaluatePolicy(policy, error: &error)
        
        if !isAvailable, let error = error {
            delegate?.biometricAuthDidFail(with: BiometricAuthError.notAvailable(error.localizedDescription))
        }
        
        return isAvailable
    }
    
    func authenticate(reason: String = "Authenticate to access Ainflue") -> Bool {
        guard checkAvailability() else {
            return false
        }
        
        guard currentRetryCount < maxRetryAttempts else {
            delegate?.biometricAuthDidExceedMaxRetries()
            return false
        }
        
        authQueue.async { [weak self] in
            self?.performAuthentication(reason: reason)
        }
        
        return true
    }
    
    func authenticateWithPromise(reason: String = "Authenticate to access Ainflue") async -> Result<AuthenticationResult, BiometricAuthError> {
        
        guard checkAvailability() else {
            return .failure(.notAvailable("Biometric authentication not available"))
        }
        
        guard currentRetryCount < maxRetryAttempts else {
            return .failure(.maxRetriesExceeded)
        }
        
        return await withCheckedContinuation { continuation in
            authQueue.async { [weak self] in
                guard let self = self else {
                    continuation.resume(returning: .failure(.systemError("Service unavailable")))
                    return
                }
                
                self.performAuthenticationWithContinuation(reason: reason, continuation: continuation)
            }
        }
    }
    
    func invalidateAuthentication() {
        securityQueue.async { [weak self] in
            guard let self = self else { return }
            
            // Invalidate current session
            self.sessionToken = nil
            self.lastAuthenticationDate = nil
            self.currentRetryCount = 0
            
            // Clear secure storage
            self.removeFromKeychain(key: self.biometricTokenKey)
            
            // Invalidate context
            self.context.invalidate()
            self.context = LAContext()
            self.setupAuthenticationContext()
            
            DispatchQueue.main.async {
                self.delegate?.biometricAuthDidInvalidate()
                print("✅ Authentication session invalidated")
            }
        }
    }
    
    // MARK: - Authentication Configuration
    
    func configureBiometricAuthentication(
        timeout: TimeInterval = 60.0,
        maxRetries: Int = 3,
        allowPasscodeFallback: Bool = true
    ) {
        securityQueue.async { [weak self] in
            guard let self = self else { return }
            
            self.authenticationTimeout = timeout
            self.maxRetryAttempts = maxRetries
            self.fallbackToPasscode = allowPasscodeFallback
            
            // Update context configuration
            if #available(iOS 9.0, *) {
                self.context.touchIDAuthenticationAllowableReuseDuration = timeout
            }
            
            // Save configuration
            let config = AuthenticationConfig(
                timeout: timeout,
                maxRetries: maxRetries,
                allowPasscodeFallback: allowPasscodeFallback
            )
            
            if let configData = try? JSONEncoder().encode(config) {
                self.saveToKeychain(data: configData, key: self.authenticationConfigKey)
            }
            
            DispatchQueue.main.async {
                self.delegate?.biometricAuthConfigurationDidUpdate()
                print("✅ Biometric authentication configured")
            }
        }
    }
    
    // MARK: - Security Status
    
    func getSecurityStatus() -> BiometricSecurityStatus {
        return BiometricSecurityStatus(
            isAvailable: checkAvailability(),
            biometricType: biometricType,
            isEnrolled: isEnrolledForBiometrics,
            lastAuthenticationDate: lastAuthenticationDate,
            isSessionValid: isCurrentSessionValid(),
            retryCount: currentRetryCount,
            maxRetries: maxRetryAttempts
        )
    }
    
    func refreshAuthenticationState() {
        securityQueue.async { [weak self] in
            guard let self = self else { return }
            
            // Re-evaluate biometric capabilities
            self.evaluateBiometricCapabilities()
            
            // Check session validity
            if !self.isCurrentSessionValid() {
                self.invalidateAuthentication()
            }
            
            DispatchQueue.main.async {
                self.delegate?.biometricAuthStateDidRefresh()
            }
        }
    }
    
    // MARK: - Private Authentication Implementation
    
    private func performAuthentication(reason: String) {
        context.evaluatePolicy(policy, localizedReason: reason) { [weak self] success, error in
            DispatchQueue.main.async {
                self?.handleAuthenticationResult(success: success, error: error)
            }
        }
    }
    
    private func performAuthenticationWithContinuation(
        reason: String,
        continuation: CheckedContinuation<Result<AuthenticationResult, BiometricAuthError>, Never>
    ) {
        context.evaluatePolicy(policy, localizedReason: reason) { [weak self] success, error in
            guard let self = self else {
                continuation.resume(returning: .failure(.systemError("Service unavailable")))
                return
            }
            
            if success {
                let result = self.createSuccessfulAuthenticationResult()
                continuation.resume(returning: .success(result))
            } else if let error = error {
                let authError = self.mapLAErrorToBiometricAuthError(error)
                continuation.resume(returning: .failure(authError))
            } else {
                continuation.resume(returning: .failure(.unknownError))
            }
        }
    }
    
    private func handleAuthenticationResult(success: Bool, error: Error?) {
        if success {
            handleSuccessfulAuthentication()
        } else if let error = error {
            handleAuthenticationError(error)
        } else {
            delegate?.biometricAuthDidFail(with: .unknownError)
        }
    }
    
    private func handleSuccessfulAuthentication() {
        currentRetryCount = 0
        lastAuthenticationDate = Date()
        sessionToken = generateSecureSessionToken()
        
        // Save authentication token securely
        if let token = sessionToken,
           let tokenData = token.data(using: .utf8) {
            saveToKeychain(data: tokenData, key: biometricTokenKey)
        }
        
        let result = createSuccessfulAuthenticationResult()
        delegate?.biometricAuthDidSucceed(result: result)
        
        print("✅ Biometric authentication successful")
    }
    
    private func handleAuthenticationError(_ error: Error) {
        currentRetryCount += 1
        
        let biometricError = mapLAErrorToBiometricAuthError(error)
        
        switch biometricError {
        case .userCancel, .userFallback:
            // Don't increment retry count for user actions
            currentRetryCount -= 1
        case .biometryLockout:
            currentRetryCount = maxRetryAttempts // Lock out immediately
        default:
            break
        }
        
        delegate?.biometricAuthDidFail(with: biometricError)
        
        print("❌ Biometric authentication failed: \(biometricError)")
    }
    
    // MARK: - Security Helpers
    
    private func createSuccessfulAuthenticationResult() -> AuthenticationResult {
        return AuthenticationResult(
            success: true,
            sessionToken: sessionToken ?? "",
            biometricType: biometricType,
            timestamp: Date(),
            expiresAt: Date().addingTimeInterval(authenticationTimeout)
        )
    }
    
    private func generateSecureSessionToken() -> String {
        let data = Data(Array(0..<32).map { _ in UInt8.random(in: 0...255) })
        return data.base64EncodedString()
    }
    
    private func isCurrentSessionValid() -> Bool {
        guard let lastAuth = lastAuthenticationDate else { return false }
        return Date().timeIntervalSince(lastAuth) < authenticationTimeout
    }
    
    private func biometricTypeString() -> String {
        switch biometricType {
        case .faceID:
            return "Face ID"
        case .touchID:
            return "Touch ID"
        case .opticID:
            return "Optic ID"
        case .none:
            return "None"
        @unknown default:
            return "Unknown"
        }
    }
    
    // MARK: - Error Mapping
    
    private func mapLAErrorToBiometricAuthError(_ error: Error) -> BiometricAuthError {
        guard let laError = error as? LAError else {
            return .systemError(error.localizedDescription)
        }
        
        switch laError.code {
        case .authenticationFailed:
            return .authenticationFailed
        case .userCancel:
            return .userCancel
        case .userFallback:
            return .userFallback
        case .systemCancel:
            return .systemCancel
        case .passcodeNotSet:
            return .passcodeNotSet
        case .biometryNotAvailable:
            return .notAvailable("Biometry not available")
        case .biometryNotEnrolled:
            return .notEnrolled
        case .biometryLockout:
            return .biometryLockout
        case .appCancel:
            return .appCancel
        case .invalidContext:
            return .invalidContext
        case .notInteractive:
            return .notInteractive
        default:
            return .systemError(laError.localizedDescription)
        }
    }
    
    private func handleBiometricError(_ error: NSError) {
        let biometricError = mapLAErrorToBiometricAuthError(error)
        delegate?.biometricAuthDidFail(with: biometricError)
    }
    
    // MARK: - Keychain Management
    
    private func saveToKeychain(data: Data, key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        
        // Delete existing item
        SecItemDelete(query as CFDictionary)
        
        // Add new item
        let status = SecItemAdd(query as CFDictionary, nil)
        
        if status != errSecSuccess {
            print("❌ Failed to save to keychain: \(status)")
        }
    }
    
    private func loadFromKeychain(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        if status == errSecSuccess {
            return result as? Data
        }
        
        return nil
    }
    
    private func removeFromKeychain(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
    
    // MARK: - Configuration Management
    
    private func saveDefaultSecurityConfiguration() {
        let defaultConfig = AuthenticationConfig(
            timeout: authenticationTimeout,
            maxRetries: maxRetryAttempts,
            allowPasscodeFallback: fallbackToPasscode
        )
        
        if let configData = try? JSONEncoder().encode(defaultConfig) {
            saveToKeychain(data: configData, key: authenticationConfigKey)
        }
    }
    
    // MARK: - Notification Handlers
    
    @objc private func handleSecurityStateChange() {
        securityQueue.async { [weak self] in
            self?.evaluateBiometricCapabilities()
            
            DispatchQueue.main.async {
                self?.delegate?.biometricAuthStateDidChange()
            }
        }
    }
    
    @objc private func handleAppDidEnterBackground() {
        // Enhanced security: invalidate session when app goes to background
        if !isCurrentSessionValid() {
            invalidateAuthentication()
        }
    }
    
    @objc private func handleAppWillEnterForeground() {
        // Refresh authentication state when app returns to foreground
        refreshAuthenticationState()
    }
    
    // MARK: - Cleanup
    
    deinit {
        NotificationCenter.default.removeObserver(self)
        context.invalidate()
    }
}

// MARK: - Supporting Types

struct AuthenticationResult {
    let success: Bool
    let sessionToken: String
    let biometricType: LABiometryType
    let timestamp: Date
    let expiresAt: Date
}

struct BiometricSecurityStatus {
    let isAvailable: Bool
    let biometricType: LABiometryType
    let isEnrolled: Bool
    let lastAuthenticationDate: Date?
    let isSessionValid: Bool
    let retryCount: Int
    let maxRetries: Int
}

struct AuthenticationConfig: Codable {
    let timeout: TimeInterval
    let maxRetries: Int
    let allowPasscodeFallback: Bool
}

// MARK: - Error Types

enum BiometricAuthError: Error, CustomStringConvertible {
    case notAvailable(String)
    case notEnrolled
    case authenticationFailed
    case userCancel
    case userFallback
    case systemCancel
    case passcodeNotSet
    case biometryLockout
    case appCancel
    case invalidContext
    case notInteractive
    case maxRetriesExceeded
    case sessionExpired
    case systemError(String)
    case unknownError
    
    var description: String {
        switch self {
        case .notAvailable(let message):
            return "Biometric authentication not available: \(message)"
        case .notEnrolled:
            return "No biometric authentication enrolled"
        case .authenticationFailed:
            return "Authentication failed"
        case .userCancel:
            return "User cancelled authentication"
        case .userFallback:
            return "User selected fallback authentication"
        case .systemCancel:
            return "System cancelled authentication"
        case .passcodeNotSet:
            return "Device passcode not set"
        case .biometryLockout:
            return "Biometric authentication locked out"
        case .appCancel:
            return "App cancelled authentication"
        case .invalidContext:
            return "Invalid authentication context"
        case .notInteractive:
            return "Authentication not interactive"
        case .maxRetriesExceeded:
            return "Maximum retry attempts exceeded"
        case .sessionExpired:
            return "Authentication session expired"
        case .systemError(let message):
            return "System error: \(message)"
        case .unknownError:
            return "Unknown authentication error"
        }
    }
}

// MARK: - Delegate Protocol

protocol BiometricAuthDelegate: AnyObject {
    func biometricAuthDidSucceed(result: AuthenticationResult)
    func biometricAuthDidFail(with error: BiometricAuthError)
    func biometricAuthDidInvalidate()
    func biometricAuthDidExceedMaxRetries()
    func biometricAuthStateDidChange()
    func biometricAuthStateDidRefresh()
    func biometricAuthConfigurationDidUpdate()
}

// MARK: - Notification Extensions

extension Notification.Name {
    static let LABiometryUpdate = Notification.Name("LABiometryUpdate")
}

// MARK: - Convenience Extensions

extension BiometricAuthService {
    
    func authenticateForContentAccess() async -> Bool {
        let result = await authenticateWithPromise(reason: "Access your protected content")
        switch result {
        case .success:
            return true
        case .failure:
            return false
        }
    }
    
    func authenticateForFinancialTransaction() async -> Bool {
        let result = await authenticateWithPromise(reason: "Authenticate to process payment")
        switch result {
        case .success:
            return true
        case .failure:
            return false
        }
    }
    
    func authenticateForSettingsAccess() async -> Bool {
        let result = await authenticateWithPromise(reason: "Access security settings")
        switch result {
        case .success:
            return true
        case .failure:
            return false
        }
    }
    
    var biometricTypeDisplayName: String {
        return biometricTypeString()
    }
    
    var isAuthenticationExpired: Bool {
        return !isCurrentSessionValid()
    }
}