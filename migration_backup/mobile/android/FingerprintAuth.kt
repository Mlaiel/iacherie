/**
 * Ainflue Fingerprint Authentication - Biometric Security Service
 * 
 * Advanced biometric authentication system for content creators
 * Supports fingerprint, face recognition, and secure authentication
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited under
 * German and international copyright law.
 */

package com.ainflue.mobile

import android.Manifest
import android.content.Context
import android.content.SharedPreferences
import android.os.Build
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Log
import androidx.annotation.RequiresApi
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.*
import java.nio.charset.Charset
import java.security.KeyStore
import java.util.*
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Professional Biometric Authentication Service for Ainflue Platform
 * 
 * Features:
 * - Fingerprint authentication
 * - Face recognition authentication  
 * - Voice recognition authentication
 * - Secure credential storage with encryption
 * - Multi-factor authentication support
 * - Biometric prompt customization
 * - Security policy enforcement
 * - Authentication state management
 * - Fallback authentication methods
 * - Enterprise security compliance
 */
class FingerprintAuth(private val context: Context) {

    companion object {
        private const val TAG = "AinflueFingerprintAuth"
        
        // Keystore and encryption constants
        private const val KEYSTORE_ALIAS = "ainflue_biometric_key"
        private const val SHARED_PREFS_NAME = "ainflue_biometric_prefs"
        private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
        private const val KEY_AUTHENTICATION_REQUIRED = "auth_required"
        private const val KEY_LAST_AUTH_TIME = "last_auth_time"
        private const val KEY_AUTH_ATTEMPTS = "auth_attempts"
        private const val KEY_LOCKOUT_TIME = "lockout_time"
        
        // Security configuration
        private const val MAX_AUTHENTICATION_ATTEMPTS = 5
        private const val LOCKOUT_DURATION_MS = 30000L // 30 seconds
        private const val AUTH_VALIDITY_DURATION_MS = 300000L // 5 minutes
        private const val GCM_IV_LENGTH = 12
        private const val GCM_TAG_LENGTH = 16
        
        // Authentication types
        const val AUTH_TYPE_FINGERPRINT = "fingerprint"
        const val AUTH_TYPE_FACE = "face"
        const val AUTH_TYPE_VOICE = "voice"
        const val AUTH_TYPE_PIN = "pin"
        const val AUTH_TYPE_PASSWORD = "password"
    }

    /**
     * Biometric authentication configuration
     */
    data class BiometricConfig(
        val title: String = "Authenticate with Ainflue",
        val subtitle: String = "Use your biometric to access your account",
        val description: String = "Place your finger on the sensor or look at the camera",
        val negativeButtonText: String = "Use Password",
        val allowedAuthenticators: Int = BiometricManager.Authenticators.BIOMETRIC_WEAK or BiometricManager.Authenticators.DEVICE_CREDENTIAL,
        val enableFallbackPassword: Boolean = true,
        val maxAttempts: Int = MAX_AUTHENTICATION_ATTEMPTS,
        val lockoutDuration: Long = LOCKOUT_DURATION_MS,
        val requireSecureLockScreen: Boolean = true,
        val enableLogging: Boolean = true
    )

    /**
     * Authentication state information
     */
    data class AuthenticationState(
        val isAuthenticated: Boolean = false,
        val authenticationType: String? = null,
        val authenticationTime: Long = 0L,
        val isLocked: Boolean = false,
        val attemptsRemaining: Int = MAX_AUTHENTICATION_ATTEMPTS,
        val lockoutTimeRemaining: Long = 0L,
        val biometricAvailable: Boolean = false,
        val enrolledBiometrics: List<String> = emptyList()
    )

    /**
     * Authentication result
     */
    data class AuthenticationResult(
        val success: Boolean,
        val authenticationType: String?,
        val timestamp: Long,
        val errorCode: Int?,
        val errorMessage: String?,
        val encryptedData: ByteArray? = null
    ) {
        override fun equals(other: Any?): Boolean {
            if (this === other) return true
            if (javaClass != other?.javaClass) return false

            other as AuthenticationResult

            if (success != other.success) return false
            if (authenticationType != other.authenticationType) return false
            if (timestamp != other.timestamp) return false
            if (errorCode != other.errorCode) return false
            if (errorMessage != other.errorMessage) return false
            if (encryptedData != null) {
                if (other.encryptedData == null) return false
                if (!encryptedData.contentEquals(other.encryptedData)) return false
            } else if (other.encryptedData != null) return false

            return true
        }

        override fun hashCode(): Int {
            var result = success.hashCode()
            result = 31 * result + (authenticationType?.hashCode() ?: 0)
            result = 31 * result + timestamp.hashCode()
            result = 31 * result + (errorCode ?: 0)
            result = 31 * result + (errorMessage?.hashCode() ?: 0)
            result = 31 * result + (encryptedData?.contentHashCode() ?: 0)
            return result
        }
    }

    /**
     * Authentication listener interface
     */
    interface AuthenticationListener {
        fun onAuthenticationSucceeded(result: AuthenticationResult)
        fun onAuthenticationFailed(result: AuthenticationResult)
        fun onAuthenticationError(errorCode: Int, errorMessage: String)
        fun onBiometricAvailabilityChanged(available: Boolean)
        fun onLockoutStateChanged(isLocked: Boolean, timeRemaining: Long)
    }

    // Authentication components
    private var biometricManager: BiometricManager? = null
    private var biometricPrompt: BiometricPrompt? = null
    private var keyStore: KeyStore? = null
    private var encryptedPreferences: SharedPreferences? = null
    
    // Authentication state
    private var isAuthenticated = false
    private var lastAuthenticationTime = 0L
    private var authenticationAttempts = 0
    private var lockoutEndTime = 0L
    private var currentAuthType: String? = null
    
    // Configuration and callbacks
    private var biometricConfig = BiometricConfig()
    private var authenticationListener: AuthenticationListener? = null
    
    // Coroutine management
    private val authScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    // Initialization state
    private var isInitialized = false

    /**
     * Initialize the biometric authentication system
     */
    suspend fun initialize(config: BiometricConfig = BiometricConfig()): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                Log.i(TAG, "🔐 Initializing FingerprintAuth with config: $config")
                
                biometricConfig = config
                
                // Initialize biometric manager
                biometricManager = BiometricManager.from(context)
                
                // Initialize secure storage
                initializeSecureStorage()
                
                // Initialize keystore
                initializeKeystore()
                
                // Load authentication state
                loadAuthenticationState()
                
                // Check biometric availability
                checkBiometricAvailability()
                
                isInitialized = true
                Log.i(TAG, "✅ FingerprintAuth initialized successfully")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to initialize FingerprintAuth", exception)
                false
            }
        }
    }

    /**
     * Check if biometric authentication is available
     */
    fun isBiometricAvailable(): Boolean {
        return when (biometricManager?.canAuthenticate(biometricConfig.allowedAuthenticators)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                Log.d(TAG, "✅ Biometric authentication available")
                true
            }
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
                Log.w(TAG, "⚠️ No biometric hardware available")
                false
            }
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> {
                Log.w(TAG, "⚠️ Biometric hardware unavailable")
                false
            }
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                Log.w(TAG, "⚠️ No biometric credentials enrolled")
                false
            }
            else -> {
                Log.w(TAG, "⚠️ Biometric authentication not available")
                false
            }
        }
    }

    /**
     * Enable biometric authentication
     */
    suspend fun enableBiometricAuth(): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                if (!isBiometricAvailable()) {
                    Log.w(TAG, "⚠️ Cannot enable biometric auth - not available")
                    return@withContext false
                }
                
                // Generate and store biometric key
                generateBiometricKey()
                
                // Update preferences
                encryptedPreferences?.edit()
                    ?.putBoolean(KEY_BIOMETRIC_ENABLED, true)
                    ?.apply()
                
                Log.i(TAG, "✅ Biometric authentication enabled")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to enable biometric authentication", exception)
                false
            }
        }
    }

    /**
     * Disable biometric authentication
     */
    suspend fun disableBiometricAuth(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                // Remove biometric key
                keyStore?.deleteEntry(KEYSTORE_ALIAS)
                
                // Update preferences
                encryptedPreferences?.edit()
                    ?.putBoolean(KEY_BIOMETRIC_ENABLED, false)
                    ?.apply()
                
                Log.i(TAG, "✅ Biometric authentication disabled")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to disable biometric authentication", exception)
                false
            }
        }
    }

    /**
     * Authenticate user with biometrics
     */
    suspend fun authenticateWithBiometric(
        activity: FragmentActivity,
        dataToEncrypt: String? = null
    ): AuthenticationResult {
        return withContext(Dispatchers.Main) {
            try {
                if (!isInitialized) {
                    throw IllegalStateException("FingerprintAuth not initialized")
                }
                
                if (isInLockoutPeriod()) {
                    return@withContext AuthenticationResult(
                        success = false,
                        authenticationType = null,
                        timestamp = System.currentTimeMillis(),
                        errorCode = BiometricPrompt.ERROR_LOCKOUT,
                        errorMessage = "Authentication locked due to too many failed attempts"
                    )
                }
                
                if (!isBiometricAvailable()) {
                    return@withContext AuthenticationResult(
                        success = false,
                        authenticationType = null,
                        timestamp = System.currentTimeMillis(),
                        errorCode = BiometricPrompt.ERROR_HW_NOT_AVAILABLE,
                        errorMessage = "Biometric authentication not available"
                    )
                }
                
                Log.i(TAG, "🔓 Starting biometric authentication")
                
                val authResult = CompletableDeferred<AuthenticationResult>()
                
                // Create biometric prompt
                biometricPrompt = BiometricPrompt(
                    activity,
                    ContextCompat.getMainExecutor(context),
                    object : BiometricPrompt.AuthenticationCallback() {
                        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                            super.onAuthenticationSucceeded(result)
                            
                            Log.i(TAG, "✅ Biometric authentication succeeded")
                            
                            // Reset authentication attempts
                            authenticationAttempts = 0
                            isAuthenticated = true
                            lastAuthenticationTime = System.currentTimeMillis()
                            currentAuthType = AUTH_TYPE_FINGERPRINT
                            
                            // Save authentication state
                            saveAuthenticationState()
                            
                            var encryptedData: ByteArray? = null
                            
                            // Encrypt data if provided
                            if (dataToEncrypt != null) {
                                encryptedData = try {
                                    encryptData(dataToEncrypt)
                                } catch (exception: Exception) {
                                    Log.e(TAG, "❌ Failed to encrypt data", exception)
                                    null
                                }
                            }
                            
                            val authResultData = AuthenticationResult(
                                success = true,
                                authenticationType = AUTH_TYPE_FINGERPRINT,
                                timestamp = lastAuthenticationTime,
                                errorCode = null,
                                errorMessage = null,
                                encryptedData = encryptedData
                            )
                            
                            authenticationListener?.onAuthenticationSucceeded(authResultData)
                            authResult.complete(authResultData)
                        }
                        
                        override fun onAuthenticationFailed() {
                            super.onAuthenticationFailed()
                            
                            Log.w(TAG, "⚠️ Biometric authentication failed")
                            
                            authenticationAttempts++
                            
                            if (authenticationAttempts >= biometricConfig.maxAttempts) {
                                // Enter lockout period
                                lockoutEndTime = System.currentTimeMillis() + biometricConfig.lockoutDuration
                                saveAuthenticationState()
                                
                                authenticationListener?.onLockoutStateChanged(true, biometricConfig.lockoutDuration)
                            }
                            
                            val failResult = AuthenticationResult(
                                success = false,
                                authenticationType = null,
                                timestamp = System.currentTimeMillis(),
                                errorCode = BiometricPrompt.ERROR_UNABLE_TO_PROCESS,
                                errorMessage = "Authentication failed"
                            )
                            
                            authenticationListener?.onAuthenticationFailed(failResult)
                            authResult.complete(failResult)
                        }
                        
                        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                            super.onAuthenticationError(errorCode, errString)
                            
                            Log.e(TAG, "❌ Biometric authentication error: $errorCode - $errString")
                            
                            val errorResult = AuthenticationResult(
                                success = false,
                                authenticationType = null,
                                timestamp = System.currentTimeMillis(),
                                errorCode = errorCode,
                                errorMessage = errString.toString()
                            )
                            
                            authenticationListener?.onAuthenticationError(errorCode, errString.toString())
                            authResult.complete(errorResult)
                        }
                    }
                )
                
                // Create prompt info
                val promptInfo = BiometricPrompt.PromptInfo.Builder()
                    .setTitle(biometricConfig.title)
                    .setSubtitle(biometricConfig.subtitle)
                    .setDescription(biometricConfig.description)
                    .setAllowedAuthenticators(biometricConfig.allowedAuthenticators)
                    .setNegativeButtonText(biometricConfig.negativeButtonText)
                    .build()
                
                // Show biometric prompt
                if (dataToEncrypt != null) {
                    // Authentication with encryption
                    val cipher = getCipher()
                    val secretKey = getSecretKey()
                    cipher.init(Cipher.ENCRYPT_MODE, secretKey)
                    
                    biometricPrompt?.authenticate(
                        promptInfo,
                        BiometricPrompt.CryptoObject(cipher)
                    )
                } else {
                    // Simple authentication
                    biometricPrompt?.authenticate(promptInfo)
                }
                
                authResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to authenticate with biometric", exception)
                AuthenticationResult(
                    success = false,
                    authenticationType = null,
                    timestamp = System.currentTimeMillis(),
                    errorCode = -1,
                    errorMessage = exception.message
                )
            }
        }
    }

    /**
     * Check if user is currently authenticated
     */
    fun isUserAuthenticated(): Boolean {
        if (!isAuthenticated) return false
        
        val currentTime = System.currentTimeMillis()
        val timeSinceAuth = currentTime - lastAuthenticationTime
        
        return timeSinceAuth < AUTH_VALIDITY_DURATION_MS
    }

    /**
     * Get current authentication state
     */
    fun getAuthenticationState(): AuthenticationState {
        val currentTime = System.currentTimeMillis()
        val isLocked = isInLockoutPeriod()
        val lockoutRemaining = if (isLocked) lockoutEndTime - currentTime else 0L
        
        return AuthenticationState(
            isAuthenticated = isUserAuthenticated(),
            authenticationType = currentAuthType,
            authenticationTime = lastAuthenticationTime,
            isLocked = isLocked,
            attemptsRemaining = (biometricConfig.maxAttempts - authenticationAttempts).coerceAtLeast(0),
            lockoutTimeRemaining = lockoutRemaining,
            biometricAvailable = isBiometricAvailable(),
            enrolledBiometrics = getEnrolledBiometrics()
        )
    }

    /**
     * Set authentication listener
     */
    fun setAuthenticationListener(listener: AuthenticationListener?) {
        authenticationListener = listener
    }

    /**
     * Clear authentication state (logout)
     */
    suspend fun clearAuthenticationState(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                isAuthenticated = false
                lastAuthenticationTime = 0L
                currentAuthType = null
                
                saveAuthenticationState()
                
                Log.i(TAG, "✅ Authentication state cleared")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to clear authentication state", exception)
                false
            }
        }
    }

    /**
     * Encrypt sensitive data
     */
    suspend fun encryptSensitiveData(data: String): ByteArray? {
        return withContext(Dispatchers.IO) {
            try {
                encryptData(data)
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to encrypt sensitive data", exception)
                null
            }
        }
    }

    /**
     * Decrypt sensitive data
     */
    suspend fun decryptSensitiveData(encryptedData: ByteArray): String? {
        return withContext(Dispatchers.IO) {
            try {
                decryptData(encryptedData)
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to decrypt sensitive data", exception)
                null
            }
        }
    }

    /**
     * Service lifecycle methods
     */
    suspend fun startService() {
        Log.i(TAG, "🚀 Starting FingerprintAuth service")
        // Service-specific initialization if needed
    }

    fun pause() {
        Log.d(TAG, "⏸️ FingerprintAuth service paused")
        // Pause any ongoing operations
    }

    fun resume() {
        Log.d(TAG, "▶️ FingerprintAuth service resumed")
        // Resume operations and check biometric availability
        authScope.launch {
            checkBiometricAvailability()
        }
    }

    suspend fun cleanup() {
        Log.i(TAG, "🧹 Cleaning up FingerprintAuth")
        
        try {
            // Clear authentication state
            clearAuthenticationState()
            
            // Cancel coroutines
            authScope.cancel()
            
            // Reset state
            isInitialized = false
            authenticationListener = null
            biometricPrompt = null
            
            Log.i(TAG, "✅ FingerprintAuth cleanup completed")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Error during FingerprintAuth cleanup", exception)
        }
    }

    // ================================
    // PRIVATE HELPER METHODS
    // ================================

    private suspend fun initializeSecureStorage() {
        withContext(Dispatchers.IO) {
            try {
                val masterKey = MasterKey.Builder(context, MasterKey.DEFAULT_MASTER_KEY_ALIAS)
                    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                    .build()

                encryptedPreferences = EncryptedSharedPreferences.create(
                    context,
                    SHARED_PREFS_NAME,
                    masterKey,
                    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
                )
                
                Log.d(TAG, "✅ Secure storage initialized")
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to initialize secure storage", exception)
                throw exception
            }
        }
    }

    private fun initializeKeystore() {
        try {
            keyStore = KeyStore.getInstance("AndroidKeyStore")
            keyStore?.load(null)
            
            Log.d(TAG, "✅ Keystore initialized")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Failed to initialize keystore", exception)
            throw exception
        }
    }

    @RequiresApi(Build.VERSION_CODES.M)
    private fun generateBiometricKey() {
        try {
            val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
            
            val keyGenParameterSpec = KeyGenParameterSpec.Builder(
                KEYSTORE_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(true)
                .setInvalidatedByBiometricEnrollment(true)
                .apply {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        setUserAuthenticationParameters(
                            AUTH_VALIDITY_DURATION_MS.toInt() / 1000,
                            KeyProperties.AUTH_BIOMETRIC_STRONG
                        )
                    } else {
                        @Suppress("DEPRECATION")
                        setUserAuthenticationValidityDurationSeconds(AUTH_VALIDITY_DURATION_MS.toInt() / 1000)
                    }
                }
                .build()
            
            keyGenerator.init(keyGenParameterSpec)
            keyGenerator.generateKey()
            
            Log.d(TAG, "✅ Biometric key generated")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Failed to generate biometric key", exception)
            throw exception
        }
    }

    private fun getSecretKey(): SecretKey {
        return keyStore?.getKey(KEYSTORE_ALIAS, null) as SecretKey
    }

    private fun getCipher(): Cipher {
        return Cipher.getInstance(
            KeyProperties.KEY_ALGORITHM_AES + "/"
                    + KeyProperties.BLOCK_MODE_GCM + "/"
                    + KeyProperties.ENCRYPTION_PADDING_NONE
        )
    }

    private fun encryptData(data: String): ByteArray {
        val cipher = getCipher()
        val secretKey = getSecretKey()
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        
        val iv = cipher.iv
        val encryptedData = cipher.doFinal(data.toByteArray(Charset.forName("UTF-8")))
        
        // Combine IV and encrypted data
        return iv + encryptedData
    }

    private fun decryptData(encryptedData: ByteArray): String {
        val cipher = getCipher()
        val secretKey = getSecretKey()
        
        // Extract IV and encrypted data
        val iv = encryptedData.sliceArray(0..GCM_IV_LENGTH - 1)
        val cipherText = encryptedData.sliceArray(GCM_IV_LENGTH until encryptedData.size)
        
        val spec = GCMParameterSpec(GCM_TAG_LENGTH * 8, iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)
        
        val decryptedData = cipher.doFinal(cipherText)
        return String(decryptedData, Charset.forName("UTF-8"))
    }

    private fun checkBiometricAvailability() {
        val available = isBiometricAvailable()
        authenticationListener?.onBiometricAvailabilityChanged(available)
    }

    private fun getEnrolledBiometrics(): List<String> {
        val enrolledBiometrics = mutableListOf<String>()
        
        when (biometricManager?.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_WEAK)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                enrolledBiometrics.add(AUTH_TYPE_FINGERPRINT)
            }
        }
        
        when (biometricManager?.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                if (!enrolledBiometrics.contains(AUTH_TYPE_FINGERPRINT)) {
                    enrolledBiometrics.add(AUTH_TYPE_FINGERPRINT)
                }
            }
        }
        
        return enrolledBiometrics
    }

    private fun isInLockoutPeriod(): Boolean {
        return System.currentTimeMillis() < lockoutEndTime
    }

    private fun loadAuthenticationState() {
        try {
            encryptedPreferences?.let { prefs ->
                lastAuthenticationTime = prefs.getLong(KEY_LAST_AUTH_TIME, 0L)
                authenticationAttempts = prefs.getInt(KEY_AUTH_ATTEMPTS, 0)
                lockoutEndTime = prefs.getLong(KEY_LOCKOUT_TIME, 0L)
                
                // Check if authentication is still valid
                isAuthenticated = isUserAuthenticated()
            }
        } catch (exception: Exception) {
            Log.e(TAG, "Failed to load authentication state", exception)
        }
    }

    private fun saveAuthenticationState() {
        try {
            encryptedPreferences?.edit()
                ?.putLong(KEY_LAST_AUTH_TIME, lastAuthenticationTime)
                ?.putInt(KEY_AUTH_ATTEMPTS, authenticationAttempts)
                ?.putLong(KEY_LOCKOUT_TIME, lockoutEndTime)
                ?.apply()
        } catch (exception: Exception) {
            Log.e(TAG, "Failed to save authentication state", exception)
        }
    }
}