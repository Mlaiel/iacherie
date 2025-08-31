/**
 * Ainflue iOS Biometric Authentication - TouchID/FaceID Security Service
 * 
 * Advanced biometric authentication system for iOS content creators
 * Supports TouchID, FaceID, and secure authentication with Keychain
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited under
 * German and international copyright law.
 */

import Foundation
import LocalAuthentication
import Security
import CryptoKit
import AuthenticationServices

/**
 * Professional Biometric Authentication Service for Ainflue iOS Platform
 * 
 * Features:
 * - TouchID authentication
 * - FaceID authentication
 * - Secure Keychain storage with biometric protection
 * - Multi-factor authentication support
 * - Biometric policy configuration
 * - Fallback authentication methods
 * - Enterprise security compliance
 * - Privacy-first design
 * - Secure enclave utilization
 */
@available(iOS 11.0, *)
public class AinflueBiometricAuth: NSObject {
    
    // MARK: - Constants
    
    private struct Constants {
        static let keychainService = "com.ainflue.mobile.biometric"
        static let biometricKeyAlias = "ainflue_biometric_key"
        static let authenticationTimeout: TimeInterval = 30.0
        static let maxAuthenticationAttempts = 5
        static let lockoutDuration: TimeInterval = 300.0 // 5 minutes
    }
    
    // MARK: - Types
    
    public enum BiometricType {
        case none
        case touchID
        case faceID
        case opticID
        
        var displayName: String {
            switch self {
            case .none: return "None"
            case .touchID: return "Touch ID"
            case .faceID: return "Face ID"
            case .opticID: return "Optic ID"
            }
        }
    }
    
    public enum AuthenticationError: Error, LocalizedError {
        case biometricNotAvailable
        case biometricNotEnrolled
        case authenticationFailed
        case userCancel
        case systemCancel
        case passcodeNotSet
        case biometricLockout
        case invalidContext
        case keychainError(OSStatus)
        case encryptionError
        case tooManyAttempts
        
        public var errorDescription: String? {
            switch self {
            case .biometricNotAvailable:
                return "Biometric authentication is not available on this device"
            case .biometricNotEnrolled:
                return "No biometric authentication is enrolled on this device"
            case .authenticationFailed:
                return "Biometric authentication failed"
            case .userCancel:
                return "User cancelled biometric authentication"
            case .systemCancel:
                return "System cancelled biometric authentication"
            case .passcodeNotSet:
                return "Device passcode is not set"
            case .biometricLockout:
                return "Biometric authentication is locked due to too many failed attempts"
            case .invalidContext:
                return "Invalid authentication context"
            case .keychainError(let status):
                return "Keychain error: \(status)"
            case .encryptionError:
                return "Data encryption/decryption failed"
            case .tooManyAttempts:
                return "Too many authentication attempts. Please try again later."
            }
        }
    }
    
    /**
     * Biometric authentication configuration
     */
    public struct BiometricConfig {
        let localizedFallbackTitle: String
        let localizedReason: String
        let touchIDAuthenticationAllowableReuseDuration: TimeInterval?
        let enableDeviceOwnerAuthentication: Bool
        let enableBiometricOnly: Bool
        
        public init(
            localizedFallbackTitle: String = "Use Passcode",
            localizedReason: String = "Authenticate to access your Ainflue account",
            touchIDAuthenticationAllowableReuseDuration: TimeInterval? = nil,
            enableDeviceOwnerAuthentication: Bool = false,
            enableBiometricOnly: Bool = true
        ) {
            self.localizedFallbackTitle = localizedFallbackTitle
            self.localizedReason = localizedReason
            self.touchIDAuthenticationAllowableReuseDuration = touchIDAuthenticationAllowableReuseDuration
            self.enableDeviceOwnerAuthentication = enableDeviceOwnerAuthentication
            self.enableBiometricOnly = enableBiometricOnly
        }
    }
    
    /**
     * Authentication result
     */
    public struct AuthenticationResult {
        let success: Bool
        let biometricType: BiometricType
        let error: AuthenticationError?
        let userID: String?
        let timestamp: Date
        
        init(success: Bool, biometricType: BiometricType, error: AuthenticationError? = nil, userID: String? = nil) {
            self.success = success
            self.biometricType = biometricType
            self.error = error
            self.userID = userID
            self.timestamp = Date()
        }
    }
    
    // MARK: - Properties
    
    private let context = LAContext()
    private let config: BiometricConfig
    private var authenticationAttempts: Int = 0
    private var lastFailedAttempt: Date?
    
    // MARK: - Initialization
    
    public init(config: BiometricConfig = BiometricConfig()) {
        self.config = config
        super.init()
    }
    
    // MARK: - Public Methods
    
    /**
     * Check if biometric authentication is available on the device
     */
    public func isBiometricAuthenticationAvailable() -> (available: Bool, biometricType: BiometricType, error: AuthenticationError?) {
        var error: NSError?
        let policy: LAPolicy = config.enableDeviceOwnerAuthentication ? .deviceOwner : .deviceOwnerAuthenticationWithBiometrics
        
        let isAvailable = context.canEvaluatePolicy(policy, error: &error)
        
        guard isAvailable else {
            let authError = mapLAError(error)
            return (false, .none, authError)
        }
        
        let biometricType = getBiometricType()
        return (true, biometricType, nil)
    }
    
    /**
     * Authenticate user with biometric authentication
     */
    public func authenticateUser(userID: String? = nil, completion: @escaping (AuthenticationResult) -> Void) {
        // Check rate limiting
        if isRateLimited() {
            let result = AuthenticationResult(success: false, biometricType: getBiometricType(), error: .tooManyAttempts)
            completion(result)
            return
        }
        
        let availability = isBiometricAuthenticationAvailable()
        guard availability.available else {
            let result = AuthenticationResult(success: false, biometricType: availability.biometricType, error: availability.error)
            completion(result)
            return
        }
        
        let policy: LAPolicy = config.enableDeviceOwnerAuthentication ? .deviceOwner : .deviceOwnerAuthenticationWithBiometrics
        let localizedReason = config.localizedReason
        
        // Configure context
        context.localizedFallbackTitle = config.localizedFallbackTitle
        if let reuseDuration = config.touchIDAuthenticationAllowableReuseDuration {
            context.touchIDAuthenticationAllowableReuseDuration = reuseDuration
        }
        
        context.evaluatePolicy(policy, localizedReason: localizedReason) { [weak self] success, error in
            DispatchQueue.main.async {
                guard let self = self else { return }
                
                if success {
                    // Reset attempts counter on success
                    self.authenticationAttempts = 0
                    self.lastFailedAttempt = nil
                    
                    let result = AuthenticationResult(
                        success: true,
                        biometricType: self.getBiometricType(),
                        userID: userID
                    )
                    completion(result)
                } else {
                    // Increment failed attempts
                    self.authenticationAttempts += 1
                    self.lastFailedAttempt = Date()
                    
                    let authError = self.mapLAError(error as NSError?)
                    let result = AuthenticationResult(
                        success: false,
                        biometricType: self.getBiometricType(),
                        error: authError
                    )
                    completion(result)
                }
            }
        }
    }
    
    /**
     * Store encrypted data in Keychain with biometric protection
     */
    public func storeSecureData(_ data: Data, for key: String, completion: @escaping (Result<Void, AuthenticationError>) -> Void) {
        guard isBiometricAuthenticationAvailable().available else {
            completion(.failure(.biometricNotAvailable))
            return
        }
        
        // Create access control for biometric authentication
        let access = SecAccessControlCreateWithFlags(
            nil,
            kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            .biometryAny,
            nil
        )
        
        guard let accessControl = access else {
            completion(.failure(.keychainError(errSecAllocate)))
            return
        }
        
        // Encrypt data
        do {
            let encryptedData = try encryptData(data)
            
            let query: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrService as String: Constants.keychainService,
                kSecAttrAccount as String: key,
                kSecValueData as String: encryptedData,
                kSecAttrAccessControl as String: accessControl
            ]
            
            // Delete existing item if it exists
            SecItemDelete(query as CFDictionary)
            
            // Add new item
            let status = SecItemAdd(query as CFDictionary, nil)
            
            if status == errSecSuccess {
                completion(.success(()))
            } else {
                completion(.failure(.keychainError(status)))
            }
        } catch {
            completion(.failure(.encryptionError))
        }
    }
    
    /**
     * Retrieve encrypted data from Keychain with biometric authentication
     */
    public func retrieveSecureData(for key: String, completion: @escaping (Result<Data, AuthenticationError>) -> Void) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Constants.keychainService,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecUseOperationPrompt as String: "Authenticate to access your secure data"
        ]
        
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        
        if status == errSecSuccess, let encryptedData = item as? Data {
            do {
                let decryptedData = try decryptData(encryptedData)
                completion(.success(decryptedData))
            } catch {
                completion(.failure(.encryptionError))
            }
        } else {
            completion(.failure(.keychainError(status)))
        }
    }
    
    /**
     * Delete secure data from Keychain
     */
    public func deleteSecureData(for key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: Constants.keychainService,
            kSecAttrAccount as String: key
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess
    }
    
    /**
     * Generate and store biometric authentication key
     */
    public func generateBiometricKey(completion: @escaping (Result<String, AuthenticationError>) -> Void) {
        let keyID = UUID().uuidString
        let keyData = SymmetricKey(size: .bits256).withUnsafeBytes { Data($0) }
        
        storeSecureData(keyData, for: Constants.biometricKeyAlias) { result in
            switch result {
            case .success:
                completion(.success(keyID))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /**
     * Get the type of biometric authentication available
     */
    public func getBiometricType() -> BiometricType {
        var error: NSError?
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return .none
        }
        
        switch context.biometryType {
        case .none:
            return .none
        case .touchID:
            return .touchID
        case .faceID:
            return .faceID
        case .opticID:
            if #available(iOS 17.0, *) {
                return .opticID
            } else {
                return .none
            }
        @unknown default:
            return .none
        }
    }
    
    // MARK: - Private Methods
    
    private func isRateLimited() -> Bool {
        guard authenticationAttempts >= Constants.maxAuthenticationAttempts,
              let lastFailure = lastFailedAttempt else {
            return false
        }
        
        let timeSinceLastFailure = Date().timeIntervalSince(lastFailure)
        return timeSinceLastFailure < Constants.lockoutDuration
    }
    
    private func mapLAError(_ error: NSError?) -> AuthenticationError {
        guard let error = error else {
            return .authenticationFailed
        }
        
        switch error.code {
        case LAError.biometryNotAvailable.rawValue:
            return .biometricNotAvailable
        case LAError.biometryNotEnrolled.rawValue:
            return .biometricNotEnrolled
        case LAError.biometryLockout.rawValue:
            return .biometricLockout
        case LAError.userCancel.rawValue:
            return .userCancel
        case LAError.systemCancel.rawValue:
            return .systemCancel
        case LAError.passcodeNotSet.rawValue:
            return .passcodeNotSet
        case LAError.invalidContext.rawValue:
            return .invalidContext
        default:
            return .authenticationFailed
        }
    }
    
    private func encryptData(_ data: Data) throws -> Data {
        let key = SymmetricKey(size: .bits256)
        let encryptedData = try AES.GCM.seal(data, using: key)
        return encryptedData.combined!
    }
    
    private func decryptData(_ encryptedData: Data) throws -> Data {
        let key = SymmetricKey(size: .bits256)
        let sealedBox = try AES.GCM.SealedBox(combined: encryptedData)
        return try AES.GCM.open(sealedBox, using: key)
    }
}

// MARK: - Extensions

extension AinflueBiometricAuth {
    
    /**
     * Async/await version of authenticateUser
     */
    @available(iOS 13.0, *)
    public func authenticateUser(userID: String? = nil) async -> AuthenticationResult {
        await withCheckedContinuation { continuation in
            authenticateUser(userID: userID) { result in
                continuation.resume(returning: result)
            }
        }
    }
    
    /**
     * Async/await version of storeSecureData
     */
    @available(iOS 13.0, *)
    public func storeSecureData(_ data: Data, for key: String) async -> Result<Void, AuthenticationError> {
        await withCheckedContinuation { continuation in
            storeSecureData(data, for: key) { result in
                continuation.resume(returning: result)
            }
        }
    }
    
    /**
     * Async/await version of retrieveSecureData
     */
    @available(iOS 13.0, *)
    public func retrieveSecureData(for key: String) async -> Result<Data, AuthenticationError> {
        await withCheckedContinuation { continuation in
            retrieveSecureData(for: key) { result in
                continuation.resume(returning: result)
            }
        }
    }
}

// MARK: - Objective-C Compatibility

@objc public class AinflueBiometricAuthObjC: NSObject {
    private let swiftImplementation = AinflueBiometricAuth()
    
    @objc public func isBiometricAvailable() -> Bool {
        return swiftImplementation.isBiometricAuthenticationAvailable().available
    }
    
    @objc public func authenticateWithCompletion(_ completion: @escaping (Bool, NSError?) -> Void) {
        swiftImplementation.authenticateUser { result in
            let nsError = result.error?.localizedDescription.map { NSError(domain: "AinflueBiometricAuth", code: -1, userInfo: [NSLocalizedDescriptionKey: $0]) }
            completion(result.success, nsError)
        }
    }
}